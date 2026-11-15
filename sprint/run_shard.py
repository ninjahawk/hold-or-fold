"""Run one shard of the frozen run set through a model (sprint runner; wraps the preexisting harness).

  python sprint/run_shard.py --model claude-haiku-5-5 --ids sprint/runset.json --shard 0 --nshards 4 \
      --out sprint/out/shards/haiku.0.jsonl [--arm escalating|neutral] [--key main|robust] [--limit N]

Shard k takes items k, k+N, k+2N, ... of the frozen order (disjoint). Items already finished in --out are skipped
(resume after a kill). Hook refusal stops the shard."""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "prebuild"), HERE]

from harness.runner import BackendBlocked, TranscriptWriter, load_items  # noqa: E402
from harness_patches.linux_backend import LinuxClaudeCLIBackend  # noqa: E402
from harness_patches.retry import run_item_retry  # noqa: E402

DATA = os.path.join(HERE, "..", "prebuild", "data")


def all_items():
    out = {}
    for f in ("mbppplus.jsonl", "humanevalplus.jsonl", "traps.jsonl"):
        for it in load_items(os.path.join(DATA, f)):
            out[it["task_id"]] = it
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--ids", required=True)
    ap.add_argument("--key", default="main")
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--nshards", type=int, default=1)
    ap.add_argument("--arm", default="escalating")
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=None, help="stop after this many positions of the frozen order")
    a = ap.parse_args()
    ids = json.load(open(a.ids))[a.key]
    if a.limit is not None:
        ids = ids[:a.limit]
    ids = ids[a.shard::a.nshards]
    items = all_items()
    done = set()
    errp = a.out.replace(".jsonl", ".errors.jsonl")
    for p in (a.out,):
        if os.path.exists(p):
            for l in open(p, encoding="utf-8"):
                r = json.loads(l)
                if r["kind"] == "rebuttal3":
                    done.add(r["task_id"])
    dropped_log = a.out.replace(".jsonl", ".dropped.jsonl")
    if os.path.exists(dropped_log):
        for l in open(dropped_log):
            done.add(json.loads(l)["task_id"])
    w, ew = TranscriptWriter(a.out), TranscriptWriter(errp)
    sbx = os.path.join("/tmp", "epi_sbx")
    os.makedirs(sbx, exist_ok=True)
    for tid in ids:
        if tid in done:
            continue
        it = items[tid]
        try:
            status, att, recs = run_item_retry(it, lambda: LinuxClaudeCLIBackend(a.model), w, ew,
                                               f"sprint-{a.key}", arm=a.arm, sandbox_root=sbx)
        except BackendBlocked as e:
            raise SystemExit(f"stopped: a hook refused the call ({e})")
        if status == "dropped":
            TranscriptWriter(dropped_log).write({"task_id": tid, "attempts": att})
            print(tid, "DROPPED after retry", flush=True)
        else:
            print(tid, att, [int(r["hidden_pass"]) for r in recs], [r["confidence"] for r in recs], flush=True)


if __name__ == "__main__":
    main()
