"""Deviation D1 (sprint, Linux): ClaudeCLIBackend with a clean child environment.

The preexisting backend passes the parent's whole environment to each `claude -p` child. On the Linux runner the
parent is itself a Claude Code session, whose environment carries session variables (CLAUDECODE, CLAUDE_CODE_*
session/messaging ids, CLAUDE_EFFORT, CLAUDE_AUTOCOMPACT_PCT_OVERRIDE, AI_AGENT). Those would leak the parent's
effort setting and session identity into the model under test, which is exactly what the harness isolation
(`--setting-sources ""`, `--strict-mcp-config`) exists to prevent. This subclass drops them; the command line
(isolation flags, hooks re-applied via `--settings`) is unchanged."""
from __future__ import annotations

import os
import shutil
import subprocess
import time

from harness.backends import ClaudeCLIBackend, Reply

DROP_PREFIXES = ("CLAUDE_CODE_", "CLAUDE_")
DROP_EXACT = {"CLAUDECODE", "AI_AGENT", "CLAUDE_EFFORT", "CLAUDE_PID", "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE"}
KEEP = {"CLAUDE_CONFIG_DIR"}  # where credentials live, if set


def clean_env(env=None):
    env = dict(os.environ if env is None else env)
    return {k: v for k, v in env.items()
            if k in KEEP or not (k in DROP_EXACT or k.startswith(DROP_PREFIXES))}


class LinuxClaudeCLIBackend(ClaudeCLIBackend):
    def _call(self, prompt: str) -> Reply:
        cmd = self.command()
        if self.dry_run:
            return Reply(text="", raw={"cmd": cmd, "stdin": prompt, "env": clean_env()})
        cmd[0] = shutil.which(cmd[0]) or os.path.expanduser("~/.local/bin/claude")
        t0 = time.time()
        try:
            cp = subprocess.run(cmd, input=prompt, cwd=self.task_dir, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=self.timeout, env=clean_env())
        except subprocess.TimeoutExpired:
            return Reply(text="", seconds=time.time() - t0, error="timeout")
        return self.parse(cp.stdout, cp.stderr, cp.returncode, time.time() - t0)
