"""Merge shard transcripts into one file per model (and arm key), in frozen run-set order.

  python sprint/merge.py <model_short> [--key main|robust]   e.g. haiku -> sprint/out/haiku.jsonl"""
import argparse
import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--key", default="main")
    a = ap.parse_args()
    stem = a.model if a.key == "main" else f"{a.model}_{a.key}"
    order = {t: i for i, t in enumerate(json.load(open(os.path.join(HERE, "runset.json")))[a.key])}
    recs, dropped, errs = [], [], []
    for f in sorted(glob.glob(os.path.join(HERE, "out", "shards", f"{stem}.[0-9].jsonl"))):
        recs += [json.loads(l) for l in open(f)]
        d = f.replace(".jsonl", ".dropped.jsonl")
        if os.path.exists(d):
            dropped += [json.loads(l) for l in open(d)]
        e = f.replace(".jsonl", ".errors.jsonl")
        if os.path.exists(e):
            errs += [json.loads(l) for l in open(e)]
    recs.sort(key=lambda r: (order[r["task_id"]], r["turn"]))
    with open(os.path.join(HERE, "out", f"{stem}.jsonl"), "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    with open(os.path.join(HERE, "out", f"{stem}.errors.jsonl"), "w") as f:
        for r in errs:
            f.write(json.dumps(r) + "\n")
    meta = {"items_complete": len({r["task_id"] for r in recs if r["kind"] == "rebuttal3"}), "records": len(recs),
            "dropped_after_retry": [d["task_id"] for d in dropped],
            "items_retried": sorted({r["task_id"] for r in errs}), "error_records": len(errs)}
    json.dump(meta, open(os.path.join(HERE, "out", f"{stem}.merge.json"), "w"), indent=1)
    print(json.dumps(meta))


if __name__ == "__main__":
    main()
