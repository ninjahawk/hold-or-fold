"""Freeze the run set (preregistered): 260 non-trap items (seed 0, stratified MBPP+/HumanEval+ in proportion to
the pool after removing the base ids of trap items) + all 40 trap variants, in one seeded order; plus the
robustness subset (60 items of the run set, seed 1). Same set for both models.

  python sprint/select_items.py sprint/runset.json"""
import json
import os
import random
import sys

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "prebuild", "data")


def ids(f):
    return [json.loads(l) for l in open(os.path.join(DATA, f), encoding="utf-8")]


def main(out):
    traps = ids("traps.jsonl")
    trap_bases = {t["base_task_id"] for t in traps}
    pools = {s: [i["task_id"] for i in ids(f) if i["task_id"] not in trap_bases]
             for s, f in (("mbppplus", "mbppplus.jsonl"), ("humanevalplus", "humanevalplus.jsonl"))}
    total = sum(len(p) for p in pools.values())
    n_he = round(260 * len(pools["humanevalplus"]) / total)
    quota = {"mbppplus": 260 - n_he, "humanevalplus": n_he}
    rng = random.Random(0)
    nontrap = []
    for s in ("mbppplus", "humanevalplus"):
        p = sorted(pools[s])
        rng.shuffle(p)
        nontrap += p[:quota[s]]
    main_ids = nontrap + [t["task_id"] for t in traps]
    random.Random(0).shuffle(main_ids)  # run order: traps spread across shards and time
    robust = random.Random(1).sample(main_ids, 60)
    meta = {"pool_after_trap_bases": {s: len(p) for s, p in pools.items()}, "quota_nontrap": quota,
            "n_trap": len(traps), "n_main": len(main_ids), "n_robust": len(robust),
            "robust_traps": sum(t.endswith("#trap") for t in robust)}
    assert len(set(main_ids)) == 300 and not (trap_bases & set(nontrap))
    json.dump({"meta": meta, "main": main_ids, "robust": robust}, open(out, "w"), indent=0)
    print(json.dumps(meta))


if __name__ == "__main__":
    main(sys.argv[1])
