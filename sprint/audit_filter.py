"""Sensitivity analysis input (added after the freeze, not preregistered): drop, for every model, the items on
which ANY model's agent touched paths outside its sandbox (audit class != clean in sprint/out/access_audit.json),
so the comparison stays paired. Writes sprint/out/<model>_auditclean.jsonl; then
  python sprint/analyze.py --models haiku sonnet --key auditclean

  python sprint/audit_filter.py --models haiku sonnet"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    a = ap.parse_args()
    aud = json.load(open(os.path.join(HERE, "out", "access_audit.json")))
    drop = sorted({t for m in a.models for t in aud["items"].get(m, {})})
    for m in a.models:
        recs = [json.loads(l) for l in open(os.path.join(HERE, "out", f"{m}.jsonl"))]
        keep = [r for r in recs if r["task_id"] not in drop]
        with open(os.path.join(HERE, "out", f"{m}_auditclean.jsonl"), "w") as f:
            for r in keep:
                f.write(json.dumps(r) + "\n")
        print(m, "items kept", len({r["task_id"] for r in keep}), "dropped", len(drop))
    json.dump(drop, open(os.path.join(HERE, "out", "auditclean_dropped.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
