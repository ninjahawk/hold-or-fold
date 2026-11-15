import json
import os
import random

from conftest import DATA
from harness.sandbox import run_tests


def _load(name):
    with open(os.path.join(DATA, name), encoding="utf-8") as f:
        return [json.loads(l) for l in f]


def test_shapes_and_counts():
    for name in ("mbppplus.jsonl", "humanevalplus.jsonl"):
        items = _load(name)
        assert len(items) > 100
        ids = set()
        for it in items:
            assert it["task_id"] not in ids
            ids.add(it["task_id"])
            assert it["visible_test"] and len(it["hidden_tests"]) >= 1
            assert it["visible_test"] not in it["hidden_tests"]
            assert it["visible_assert"].startswith(f"assert {it['entry_point']}(")


def test_canonical_passes_hidden_sample():
    # full check is done by build_data; re-execute a fixed random sample here
    items = _load("mbppplus.jsonl") + _load("humanevalplus.jsonl")
    for it in random.Random(0).sample(items, 12):
        assert run_tests(it["canonical_solution"], it["entry_point"], [it["visible_test"]] + it["hidden_tests"]).all_passed, it["task_id"]


def test_traps_by_execution():
    traps = _load("traps.jsonl")
    assert len(traps) >= 30
    for t in traps:
        assert t["is_trap"] and t["trap_rationale"] and t["hidden_tests"][-1] == t["trap_test"]
        assert not run_tests(t["canonical_solution"], t["entry_point"], [t["trap_test"]]).all_passed, t["task_id"]
        assert run_tests(t["reference_solution"], t["entry_point"], [t["visible_test"]] + t["hidden_tests"]).all_passed, t["task_id"]


def test_fallback_shape():
    for name in ("arc_challenge.jsonl", "mmlu_pro.jsonl"):
        items = _load(name)
        assert len(items) > 1000
        for it in items[:200]:
            assert 0 <= it["answer_index"] < len(it["choices"]) == len(it["labels"])
            assert it["labels"][it["answer_index"]] == it["answer_label"]
