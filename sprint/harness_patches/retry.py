"""Deviation D2 (sprint): the preregistered backend-error rule ("retry once, then drop and count") was not
implemented in the preexisting runner. An item's turns are buffered; if any turn has a backend error (timeout,
bad json, is_error / error_max_turns) the item is re-run once from scratch, regardless of its hidden-test result.
If the retry also errors, the item is dropped: its records go to the errors file, not the transcript.
Failed-attempt records are always kept in the errors file for audit. A hook refusal stops the whole run."""
from __future__ import annotations

from harness.runner import BackendBlocked, run_item


class ListWriter:
    def __init__(self):
        self.recs = []

    def write(self, rec):
        self.recs.append(rec)


def run_item_retry(item, make_backend, writer, err_writer, run_id, arm="escalating", sandbox_root=None):
    """-> ("ok" | "dropped", attempts, records of the kept attempt or None)."""
    for attempt in (1, 2):
        buf = ListWriter()
        recs = run_item(item, make_backend(), buf, run_id, arm=arm, sandbox_root=sandbox_root)  # BackendBlocked propagates
        bad = [r for r in recs if r["backend_error"]]
        if not bad:
            for r in recs:
                r["attempt"] = attempt
                writer.write(r)
            return "ok", attempt, recs
        for r in recs:
            r["attempt"] = attempt
            err_writer.write(r)
    return "dropped", 2, None
