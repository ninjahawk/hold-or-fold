"""Sandboxed execution of a candidate solution against a list of test cases.

Each test case is a dict {"args": "<python literal of the argument list>",
"expected": "<python literal>", "atol": float}. The candidate and a generated
pytest file are written to a fresh temp dir; pytest runs in a subprocess with
a stripped environment, a per-test alarm and a wall-clock timeout for the whole run.
Results come back per test via JUnit XML.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

PER_TEST_SECONDS = 5
DEFAULT_TIMEOUT = 120

_TEST_HEADER = '''\
import math, signal
from math import inf, nan
import solution as _sol

PER_TEST = {per_test}

def _isfloats(x):
    if isinstance(x, float):
        return True
    if isinstance(x, (list, tuple)):
        return len(x) > 0 and all(isinstance(i, float) for i in x)
    return False

def _close(out, exp, atol):
    if isinstance(exp, (list, tuple)):
        if not isinstance(out, (list, tuple)) or len(out) != len(exp):
            return False
        return all(_close(o, e, atol) for o, e in zip(out, exp))
    if isinstance(exp, (int, float)) and isinstance(out, (int, float)):
        return math.isclose(out, exp, rel_tol=1e-07, abs_tol=atol)
    return out == exp

def _assertion(out, exp, atol):
    # Same rule as EvalPlus: exact equality, float tolerance when floats or atol given.
    if atol == 0 and _isfloats(exp):
        atol = 1e-6
    if out != exp and atol != 0:
        assert _close(out, exp, atol), f"out: {{out!r}}, exp: {{exp!r}}"
    else:
        assert out == exp, f"out: {{out!r}}, exp: {{exp!r}}"

def _alarm(signum, frame):
    raise TimeoutError("per-test timeout")

def _call(args):
    fn = getattr(_sol, {entry!r})
    if hasattr(signal, "SIGALRM"):  # POSIX: interrupt the call
        signal.signal(signal.SIGALRM, _alarm)
        signal.alarm(PER_TEST)
        try:
            return fn(*args)
        finally:
            signal.alarm(0)
    # Windows: run in a daemon thread; a hung call is abandoned (the run-level timeout still bounds the process)
    import threading
    box = {{}}
    def target():
        try:
            box["out"] = fn(*args)
        except BaseException as e:  # noqa: BLE001
            box["err"] = e
    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(PER_TEST)
    if t.is_alive():
        raise TimeoutError("per-test timeout")
    if "err" in box:
        raise box["err"]
    return box["out"]

def _run(args, exp, atol):
    out = _call(args)
    _assertion(out, exp, atol)
'''

_TEST_CASE = '''
def test_{i:04d}():
    _run({args}, {expected}, {atol!r})
'''


@dataclass
class ExecResult:
    passed: list[bool] = field(default_factory=list)
    error: str | None = None  # whole-run problem (timeout, import error, crash)
    stdout: str = ""

    @property
    def all_passed(self) -> bool:
        return self.error is None and len(self.passed) > 0 and all(self.passed)

    @property
    def n_passed(self) -> int:
        return sum(self.passed)


def render_test_file(entry_point: str, tests: list[dict], per_test: int = PER_TEST_SECONDS) -> str:
    parts = [_TEST_HEADER.format(per_test=per_test, entry=entry_point)]
    for i, t in enumerate(tests):
        parts.append(_TEST_CASE.format(i=i, args=t["args"], expected=t["expected"], atol=float(t.get("atol", 0) or 0)))
    return "".join(parts)


def run_tests(solution_code: str, entry_point: str, tests: list[dict], timeout: int = DEFAULT_TIMEOUT,
              per_test: int = PER_TEST_SECONDS, workdir: str | None = None) -> ExecResult:
    """Run `tests` against `solution_code`. Never raises for candidate faults."""
    if not tests:
        return ExecResult(error="no tests")
    own = workdir is None
    d = workdir or tempfile.mkdtemp(prefix="sbx_")
    try:
        with open(os.path.join(d, "solution.py"), "w", encoding="utf-8") as f:
            f.write(solution_code)
        with open(os.path.join(d, "test_hidden.py"), "w", encoding="utf-8") as f:
            f.write(render_test_file(entry_point, tests, per_test))
        xml_path = os.path.join(d, "report.xml")
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), "PYTHONDONTWRITEBYTECODE": "1",
               "PYTHONHASHSEED": "0", "HOME": d, "TEMP": d, "TMP": d}
        for k in ("SYSTEMROOT", "SystemRoot", "WINDIR", "COMSPEC"):  # Windows needs these to start Python
            if k in os.environ:
                env[k] = os.environ[k]
        cmd = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--rootdir", d,
               f"--junitxml={xml_path}", "test_hidden.py"]
        try:
            cp = subprocess.run(cmd, cwd=d, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
        except subprocess.TimeoutExpired:
            return ExecResult(passed=[False] * len(tests), error="timeout")
        out = (cp.stdout or "")[-4000:]
        if not os.path.exists(xml_path):
            return ExecResult(passed=[False] * len(tests), error="no report", stdout=out)
        status: dict[str, bool] = {}
        root = ET.parse(xml_path).getroot()
        for tc in root.iter("testcase"):
            ok = not any(child.tag in ("failure", "error", "skipped") for child in tc)
            status[tc.get("name")] = ok
        passed = [status.get(f"test_{i:04d}", False) for i in range(len(tests))]
        err = None
        if not status:
            err = "collection error"
        return ExecResult(passed=passed, error=err, stdout=out)
    finally:
        if own:
            shutil.rmtree(d, ignore_errors=True)


def tests_to_json(tests: list[dict]) -> str:
    return json.dumps(tests)
