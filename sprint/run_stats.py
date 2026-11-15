"""Run facts from the raw transcripts: switch-rule check after the first 100 Haiku items (by completion time),
API-equivalent cost (the CLI's reported cost_usd) and wall time per 100 items, per model.

  python sprint/run_stats.py --models haiku sonnet   -> stdout + sprint/out/run_stats.json"""
import argparse
import json
import os
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))


def items(path):
    t = {}
    for line in open(path):
        r = json.loads(line)
        t.setdefault(r["task_id"], []).append(r)
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    a = ap.parse_args()
    out = {}
    for m in a.models:
        t = items(os.path.join(HERE, "out", f"{m}.jsonl"))
        done = {k: v for k, v in t.items() if any(r["kind"] == "rebuttal3" for r in v)}
        fin = sorted(done, key=lambda k: max(r["ts"] for r in done[k]))
        def wrong0(k):
            return [r for r in done[k] if r["kind"] == "confidence"][0]["hidden_pass"] is False or \
                not [r for r in done[k] if r["kind"] == "confidence"][0]["hidden_pass"]
        first = fin[:100]
        cost = sum((r.get("cost_usd") or 0) for v in done.values() for r in v)
        secs = sum((r.get("seconds") or 0) for v in done.values() for r in v)
        o = {"items_complete": len(done),
             "first100_by_completion": {"wrong0_all": sum(wrong0(k) for k in first),
                                        "wrong0_nontrap": sum(wrong0(k) for k in first if not k.endswith("#trap"))},
             "api_equiv_usd_total": round(cost, 2), "api_equiv_usd_per_100_items": round(100 * cost / len(done), 2),
             "agent_seconds_per_item": round(secs / len(done), 1)}
        if m == "haiku":
            f = o["first100_by_completion"]
            o["switch_rule_triggered"] = f["wrong0_all"] < 10 or f["wrong0_nontrap"] < 5
        out[m] = o
        print(m, json.dumps(o))
    json.dump(out, open(os.path.join(HERE, "out", "run_stats.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
