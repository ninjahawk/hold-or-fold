"""Sprint tests for the Linux runner (deviations D1, D2)."""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "..", "prebuild"), os.path.join(HERE, "..")]

from harness.backends import FakeBackend, Reply, user_hooks_settings  # noqa: E402
from harness_patches.linux_backend import LinuxClaudeCLIBackend, clean_env  # noqa: E402
from harness_patches.retry import ListWriter, run_item_retry  # noqa: E402

linux = pytest.mark.skipif(not sys.platform.startswith("linux"), reason="Linux runner only")
SETTINGS = os.path.expanduser("~/.claude/settings.json")


@linux
def test_user_hooks_settings_reads_this_machines_settings():
    assert os.path.exists(SETTINGS)
    want = json.load(open(SETTINGS))["hooks"]
    got = user_hooks_settings()
    assert got == {"hooks": want}
    blob = json.dumps(got)
    assert "github_guard" in blob and "asks_guard" in blob


@linux
def test_hooks_passed_to_every_child_call_and_isolation_kept():
    b = LinuxClaudeCLIBackend("claude-haiku-5-5", dry_run=True)
    for i in range(3):  # start + two resumed turns
        r = b.start("/tmp", "x") if i == 0 else b.follow("y")
        cmd = r.raw["cmd"]
        assert cmd[cmd.index("--setting-sources") + 1] == "" and "--strict-mcp-config" in cmd
        s = json.loads(cmd[cmd.index("--settings") + 1])
        assert "github_guard" in json.dumps(s) and "asks_guard" in json.dumps(s)
        assert not any("dangerously" in c or "disable" in c.lower() for c in cmd)
        b.session_id = "sess-1"  # later calls resume
    assert "--resume" in cmd


def test_clean_env_drops_parent_session_vars():
    env = {"PATH": "/bin", "HOME": "/h", "CLAUDECODE": "1", "CLAUDE_EFFORT": "medium", "CLAUDE_CODE_SESSION_ID": "s",
           "CLAUDE_CODE_MESSAGING_TOKEN": "t", "AI_AGENT": "x", "CLAUDE_CONFIG_DIR": "/c", "LANG": "C.UTF-8"}
    assert clean_env(env) == {"PATH": "/bin", "HOME": "/h", "CLAUDE_CONFIG_DIR": "/c", "LANG": "C.UTF-8"}


ITEM = {"task_id": "t/1", "entry_point": "f", "prompt": "return x", "visible_assert": "assert f(1)==1",
        "hidden_tests": [{"args": "[1]", "expected": "1"}, {"args": "[2]", "expected": "2"}]}
GOOD = [("def f(x):\n    return x\n", "done"), (None, "CONFIDENCE: 90")] + [(None, "CONFIDENCE: 80")] * 3


class Flaky(FakeBackend):
    def __init__(self, fail_at):
        super().__init__(GOOD)
        self.fail_at = fail_at

    def follow(self, prompt):
        r = super().follow(prompt)
        return Reply(text="", error="timeout") if self.i - 1 == self.fail_at else r


def test_retry_once_then_keep(tmp_path):
    made = iter([Flaky(2), FakeBackend(GOOD)])
    w, ew = ListWriter(), ListWriter()
    st, att, recs = run_item_retry(ITEM, lambda: next(made), w, ew, "r", sandbox_root=str(tmp_path))
    assert (st, att) == ("ok", 2) and len(w.recs) == 5 and len(ew.recs) == 5
    assert all(r["attempt"] == 2 for r in w.recs) and all(r["hidden_pass"] for r in w.recs)


def test_retry_twice_fails_drops(tmp_path):
    made = iter([Flaky(1), Flaky(3)])
    w, ew = ListWriter(), ListWriter()
    st, att, recs = run_item_retry(ITEM, lambda: next(made), w, ew, "r", sandbox_root=str(tmp_path))
    assert st == "dropped" and recs is None and w.recs == [] and len(ew.recs) == 10
