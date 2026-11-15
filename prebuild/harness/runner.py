"""Run one item through: solve -> confidence -> 3 rebuttals. After every turn the current
solution.py is snapshotted and scored against the hidden tests in a separate sandbox; one JSONL
transcript line per turn.

Turn kinds: "solve", "confidence", "rebuttal1", "rebuttal2", "rebuttal3"."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import time

from harness import prompts
from harness.sandbox import run_tests


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def _norm(code):
    if code is None:
        return None
    return "\n".join(l.rstrip() for l in code.strip().splitlines() if l.strip())


def sha(code):
    return None if code is None else hashlib.sha256(_norm(code).encode()).hexdigest()[:16]


class TranscriptWriter:
    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    def write(self, rec):
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")


class BackendBlocked(RuntimeError):
    """A hook refused the call before it reached the model: stop the run, write nothing."""


def run_item(item, backend, writer, run_id, arm="escalating", sandbox_root=None, keep_dir=False):
    """Returns the list of turn records (also written to `writer`)."""
    task_dir = tempfile.mkdtemp(prefix="task_", dir=sandbox_root)
    recs = []
    prev_sha = None
    tools = backend.tools
    turns = [("solve", prompts.solve_prompt(item, tools)), ("confidence", prompts.CONFIDENCE)]
    turns += [(f"rebuttal{k + 1}", prompts.rebuttal_prompt(k, tools, arm)) for k in range(3)]
    try:
        for idx, (kind, prompt) in enumerate(turns):
            reply = backend.start(task_dir, prompt) if idx == 0 else backend.follow(prompt)
            if reply.error == "blocked by hook":
                raise BackendBlocked(reply.text[:300])
            code = _read(os.path.join(task_dir, "solution.py"))
            h = sha(code)
            if code is None:
                res_pass, n_pass = False, 0
                err = "no solution.py"
            else:
                r = run_tests(code, item["entry_point"], item["hidden_tests"])
                res_pass, n_pass, err = r.all_passed, r.n_passed, r.error
            rec = {
                "run_id": run_id, "model": backend.name, "arm": arm, "task_id": item["task_id"],
                "is_trap": bool(item.get("is_trap")), "turn": idx, "kind": kind,
                "prompt": prompt, "response": reply.text, "backend_error": reply.error,
                "confidence": prompts.parse_confidence(reply.text) if kind != "solve" else None,
                "solution_sha": h, "solution_code": code,
                "changed": (h != prev_sha) if idx > 0 else None,
                "hidden_pass": res_pass, "hidden_n_passed": n_pass, "hidden_n": len(item["hidden_tests"]),
                "exec_error": err, "seconds": reply.seconds, "cost_usd": reply.cost_usd, "usage": reply.raw or None,
                "ts": time.time(),
            }
            prev_sha = h
            writer.write(rec)
            recs.append(rec)
    finally:
        if not keep_dir:
            shutil.rmtree(task_dir, ignore_errors=True)
    return recs


def load_items(path, ids=None):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if ids is None or r["task_id"] in ids:
                out.append(r)
    return out
