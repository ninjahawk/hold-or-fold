"""Model backends. Interface: start(task_dir, prompt) -> Reply; follow(prompt) -> Reply.
After each call the runner reads `solution.py` from task_dir (tool backends write it themselves;
answer-only backends get the code block extracted and written by the backend).

ClaudeCLIBackend: checked on the Windows host (see SMOKE.md). OllamaBackend: still a stub until its smoke run.
FakeBackend: unit tests and synthetic transcripts."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import urllib.request
from dataclasses import dataclass, field

from harness import prompts


@dataclass
class Reply:
    text: str
    raw: dict = field(default_factory=dict)
    seconds: float = 0.0
    cost_usd: float | None = None
    error: str | None = None


class Backend:
    name = "base"
    tools = True

    def start(self, task_dir: str, prompt: str) -> Reply:
        raise NotImplementedError

    def follow(self, prompt: str) -> Reply:
        raise NotImplementedError


def user_hooks_settings(home: str | None = None) -> dict:
    """The `hooks` block of the user's own Claude Code settings (~/.claude/settings.json), or {}.

    Isolated runs drop every settings source (no user CLAUDE.md, plugins, MCP servers, model/effort overrides
    reach the model under test), but the user's hooks are re-applied through `--settings` so local guards
    (e.g. a gate on who may run headless Claude) still run exactly as they would otherwise."""
    path = os.path.join(home or os.path.expanduser("~"), ".claude", "settings.json")
    try:
        with open(path, encoding="utf-8") as f:
            hooks = json.load(f).get("hooks")
    except (OSError, ValueError):
        return {}
    return {"hooks": hooks} if hooks else {}


def parse_usage(out: dict) -> dict:
    """Flat per-call token/latency record from `claude -p --output-format json` output."""
    u = out.get("usage") or {}
    return {
        "input_tokens": u.get("input_tokens", 0), "output_tokens": u.get("output_tokens", 0),
        "cache_creation_input_tokens": u.get("cache_creation_input_tokens", 0),
        "cache_read_input_tokens": u.get("cache_read_input_tokens", 0),
        "thinking_tokens": (u.get("output_tokens_details") or {}).get("thinking_tokens", 0),
        "num_turns": out.get("num_turns"), "duration_ms": out.get("duration_ms"),
        "duration_api_ms": out.get("duration_api_ms"),
    }


class ClaudeCLIBackend(Backend):
    """`claude -p` with tools, cwd = per-task sandbox dir, `--resume <session>` for later turns.

    The prompt goes on stdin (no command-line quoting or length limits on Windows). `isolate` (default) runs with
    `--setting-sources ""` + `--strict-mcp-config` and re-applies only the user's hooks (see user_hooks_settings)."""

    tools = True

    def __init__(self, model: str, claude_bin: str = "claude", timeout: int = 600,
                 allowed_tools: str = "Read,Write,Edit,Bash", max_turns: int = 20, dry_run: bool = False,
                 isolate: bool = True, settings: dict | None = None):
        self.model, self.bin, self.timeout = model, claude_bin, timeout
        self.allowed_tools, self.max_turns, self.dry_run = allowed_tools, max_turns, dry_run
        self.isolate = isolate
        self.settings = user_hooks_settings() if settings is None and isolate else (settings or {})
        self.name = f"claude:{model}"
        self.session_id = None
        self.task_dir = None

    def command(self) -> list[str]:
        cmd = [self.bin, "-p", "--model", self.model, "--output-format", "json",
               "--allowedTools", self.allowed_tools, "--permission-mode", "acceptEdits",
               "--max-turns", str(self.max_turns)]
        if self.isolate:
            cmd += ["--setting-sources", "", "--strict-mcp-config"]
            if self.settings:
                cmd += ["--settings", json.dumps(self.settings)]
        if self.session_id:
            cmd += ["--resume", self.session_id]
        return cmd

    def _call(self, prompt: str) -> Reply:
        cmd = self.command()
        if self.dry_run:
            return Reply(text="", raw={"cmd": cmd, "stdin": prompt})
        cmd[0] = shutil.which(cmd[0]) or cmd[0]  # claude.exe or a .cmd shim on Windows
        t0 = time.time()
        kw = {"creationflags": 0x08000000} if os.name == "nt" else {}  # CREATE_NO_WINDOW: nothing pops up
        try:
            cp = subprocess.run(cmd, input=prompt, cwd=self.task_dir, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=self.timeout, **kw)
        except subprocess.TimeoutExpired:
            return Reply(text="", seconds=time.time() - t0, error="timeout")
        return self.parse(cp.stdout, cp.stderr, cp.returncode, time.time() - t0)

    def parse(self, stdout: str, stderr: str, rc: int, seconds: float) -> Reply:
        try:
            out = json.loads(stdout)
        except json.JSONDecodeError:
            return Reply(text=stdout, seconds=seconds, error=f"bad json (rc {rc}): {stderr[-300:]}")
        if not isinstance(out, dict):
            return Reply(text=stdout, seconds=seconds, error=f"unexpected json (rc {rc})")
        resumed_from = self.session_id
        self.session_id = out.get("session_id") or self.session_id
        text = out.get("result") or ""
        err = None
        if out.get("is_error") or out.get("subtype", "success") != "success":
            err = f"is_error: {out.get('subtype')}"
        elif "operation blocked by hook" in text:
            err = "blocked by hook"
        usage = parse_usage(out)
        usage["session_id"], usage["resumed_from"] = out.get("session_id"), resumed_from  # audit: turns 2-5 resume
        return Reply(text=text, raw=usage, seconds=seconds, cost_usd=out.get("total_cost_usd"), error=err)

    def start(self, task_dir, prompt):
        self.task_dir, self.session_id = task_dir, None
        return self._call(prompt)

    def follow(self, prompt):
        return self._call(prompt)


class OllamaBackend(Backend):
    """Answer-only: no tools. Keeps the chat history; writes the last code block to solution.py."""

    tools = False

    def __init__(self, model: str, url: str = "http://127.0.0.1:11434/api/chat", timeout: int = 300,
                 options: dict | None = None):
        self.model, self.url, self.timeout = model, url, timeout
        self.options = options or {"temperature": 0}
        self.name = f"ollama:{model}"
        self.messages, self.task_dir = [], None

    def _call(self, prompt):
        self.messages.append({"role": "user", "content": prompt})
        body = json.dumps({"model": self.model, "messages": self.messages, "stream": False,
                           "options": self.options}).encode()
        req = urllib.request.Request(self.url, data=body, headers={"Content-Type": "application/json"})
        t0 = time.time()
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                out = json.loads(r.read())
        except Exception as e:  # noqa: BLE001
            return Reply(text="", seconds=time.time() - t0, error=f"{type(e).__name__}: {e}")
        text = out.get("message", {}).get("content", "")
        self.messages.append({"role": "assistant", "content": text})
        code = prompts.extract_code(text)
        if code is not None:
            with open(os.path.join(self.task_dir, "solution.py"), "w", encoding="utf-8") as f:
                f.write(code)
        return Reply(text=text, raw={k: out.get(k) for k in ("eval_count", "prompt_eval_count", "total_duration")},
                     seconds=time.time() - t0)

    def start(self, task_dir, prompt):
        self.task_dir, self.messages = task_dir, []
        return self._call(prompt)

    def follow(self, prompt):
        return self._call(prompt)


class FakeBackend(Backend):
    """Scripted backend for tests and synthetic runs.

    script: list of (code or None, text) per call, in order: solve, confidence, rebuttal 1..3.
    code None = leave solution.py unchanged."""

    def __init__(self, script, name="fake", tools=True):
        self.script, self.name, self.tools = list(script), name, tools
        self.i, self.task_dir = 0, None

    def _call(self):
        code, text = self.script[self.i]
        self.i += 1
        if code is not None:
            with open(os.path.join(self.task_dir, "solution.py"), "w", encoding="utf-8") as f:
                f.write(code)
        return Reply(text=text)

    def start(self, task_dir, prompt):
        self.task_dir, self.i = task_dir, 0
        return self._call()

    def follow(self, prompt):
        return self._call()
