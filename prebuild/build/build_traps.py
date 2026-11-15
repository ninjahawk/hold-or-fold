"""Build trap variants from trap_specs.T and verify each by execution.

usage: python -m build.build_traps <data_dir>   (reads mbppplus.jsonl, humanevalplus.jsonl; writes traps.jsonl)
"""
import json
import os
import sys
import textwrap
from concurrent.futures import ThreadPoolExecutor

from build.trap_specs import T
from harness.sandbox import run_tests


def alt_code(canonical, entry, body):
    return canonical + f"\n\n_orig = {entry}\n\ndef {entry}(*a):\n" + textwrap.indent(body, "    ") + "\n"


def build_one(spec, items):
    tid, args, exp, body, why = spec
    it = items.get(tid)
    if it is None:
        return None, f"{tid}: not in data"
    trap = {"args": args, "expected": exp, "atol": it["visible_test"].get("atol", 0)}
    alt = alt_code(it["canonical_solution"], it["entry_point"], body)
    can = run_tests(it["canonical_solution"], it["entry_point"], [trap])
    if can.passed and can.passed[0]:
        return None, f"{tid}: canonical passes the trap"
    full = [it["visible_test"]] + it["hidden_tests"] + [trap]
    res = run_tests(alt, it["entry_point"], full)
    if not res.all_passed:
        bad = [i for i, p in enumerate(res.passed) if not p]
        where = "trap" if bad == [len(full) - 1] else f"{len(bad)} tests incl. original ones"
        return None, f"{tid}: alternate fails {where} ({res.error})"
    v = dict(it)
    v.update({"task_id": tid + "#trap", "base_task_id": tid, "is_trap": True,
              "hidden_tests": it["hidden_tests"] + [trap], "trap_test": trap,
              "trap_rationale": why, "reference_solution": alt})
    return v, None


def main(data_dir):
    items = {}
    for src in ("mbppplus", "humanevalplus"):
        for line in open(os.path.join(data_dir, f"{src}.jsonl"), encoding="utf-8"):
            r = json.loads(line)
            items[r["task_id"]] = r
    with ThreadPoolExecutor(4) as ex:
        out = list(ex.map(lambda s: build_one(s, items), T))
    kept = [v for v, e in out if v]
    rejected = [e for v, e in out if e]
    with open(os.path.join(data_dir, "traps.jsonl"), "w", encoding="utf-8") as f:
        for v in kept:
            f.write(json.dumps(v) + "\n")
    with open(os.path.join(data_dir, "traps_rejected.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(rejected) + "\n")
    print(f"specs {len(T)} kept {len(kept)} rejected {len(rejected)}")
    print("\n".join(rejected))


if __name__ == "__main__":
    main(sys.argv[1])
