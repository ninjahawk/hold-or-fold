"""Build task JSONL from EvalPlus MBPP+ and HumanEval+ (public HF datasets evalplus/mbppplus, evalplus/humanevalplus).

Per item: 1 visible test (the first EvalPlus input), the rest hidden (capped, see MAX_HIDDEN).
Expected outputs are EvalPlus's own `results` lists. Every item is executed: the canonical
solution must pass the visible and every hidden test in the sandbox, else the item is dropped.

usage: python -m build.build_data <raw_dir> <out_dir>
"""
import ast
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from math import inf, nan  # noqa: F401  (used by eval of EvalPlus literals)

import pyarrow.parquet as pq

from harness.sandbox import run_tests

MAX_HIDDEN = 30          # hidden tests kept per item (first-come order: base inputs, then plus inputs)
MAX_TEST_CHARS = 2000    # drop single tests whose literal is longer than this (keeps prompts/test files small)
LOOP = re.compile(r"assertion\((\w+)\(\*inp\), exp, ([0-9.e-]+)\)")


def _lit(src):
    try:
        return ast.literal_eval(src)
    except Exception:
        return eval(src, {"inf": inf, "nan": nan, "__builtins__": {}})


def parse_tests(test_src):
    """Return (entry, atol, [(args, expected)]) or None if the test is not the standard loop."""
    m = LOOP.search(test_src)
    if not m:
        return None
    mi = re.search(r"^\s*inputs = (.*)$", test_src, re.M)
    mr = re.search(r"^\s*results = (.*)$", test_src, re.M)
    if not (mi and mr):
        return None
    inputs, results = _lit(mi.group(1)), _lit(mr.group(1))
    if len(inputs) != len(results):
        return None
    return m.group(1), float(m.group(2)), list(zip(inputs, results))


def to_case(args, exp, atol):
    a, e = repr(list(args)), repr(exp)
    if len(a) + len(e) > MAX_TEST_CHARS:
        return None
    try:  # must round-trip as a literal (inf/nan allowed)
        assert _lit(a) == list(args) or 'nan' in a
    except Exception:
        return None
    return {"args": a, "expected": e, "atol": atol}


def visible_assert(entry, case):
    args = case["args"][1:-1]
    return f"assert {entry}({args}) == {case['expected']}"


def load(raw_dir):
    items = []
    for name, src in [("mbppplus", "mbppplus"), ("humanevalplus", "humanevalplus")]:
        d = os.path.join(raw_dir, src, "data")
        rows = pq.read_table(os.path.join(d, os.listdir(d)[0])).to_pylist()
        for r in rows:
            parsed = parse_tests(r["test"])
            if parsed is None:
                items.append({"task_id": f"{name}/{r['task_id']}", "_drop": "nonstandard test"})
                continue
            entry, atol, pairs = parsed
            if name == "humanevalplus":
                entry = r["entry_point"]
                canonical = r["prompt"] + r["canonical_solution"]
                prompt = r["prompt"]
                imports = ""
            else:
                canonical = r["code"]
                prompt = r["prompt"]
                imports = "\n".join(r.get("test_imports") or [])
            cases = [c for c in (to_case(a, e, atol) for a, e in pairs) if c]
            if len(cases) < 2:
                items.append({"task_id": f"{name}/{r['task_id']}", "_drop": "fewer than 2 usable tests"})
                continue
            visible, hidden = cases[0], cases[1:1 + MAX_HIDDEN]
            items.append({
                "task_id": f"{name}/{r['task_id']}", "source": name, "entry_point": entry,
                "prompt": prompt, "visible_test": visible, "visible_assert": visible_assert(entry, visible),
                "hidden_tests": hidden, "canonical_solution": (imports + "\n" + canonical) if imports else canonical,
                "is_trap": False,
            })
    return items


def verify(item):
    if "_drop" in item:
        return item
    res = run_tests(item["canonical_solution"], item["entry_point"], [item["visible_test"]] + item["hidden_tests"])
    if not res.all_passed:
        item = {"task_id": item["task_id"], "_drop": f"canonical fails ({res.error or str(len(res.passed) - res.n_passed) + ' tests'})"}
    return item


def main(raw_dir, out_dir):
    items = load(raw_dir)
    with ThreadPoolExecutor(4) as ex:
        items = list(ex.map(verify, items))
    stats = {}
    os.makedirs(out_dir, exist_ok=True)
    for src in ("mbppplus", "humanevalplus"):
        kept = [i for i in items if i["task_id"].startswith(src) and "_drop" not in i]
        dropped = [i for i in items if i["task_id"].startswith(src) and "_drop" in i]
        with open(os.path.join(out_dir, f"{src}.jsonl"), "w", encoding="utf-8") as f:
            for i in kept:
                f.write(json.dumps(i) + "\n")
        stats[src] = {"kept": len(kept), "dropped": len(dropped),
                      "dropped_items": {d["task_id"]: d["_drop"] for d in dropped},
                      "hidden_tests_total": sum(len(i["hidden_tests"]) for i in kept)}
    with open(os.path.join(out_dir, "build_stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=1)
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "dropped_items"} for k, v in stats.items()}))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
