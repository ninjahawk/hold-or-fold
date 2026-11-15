"""CLI: run items through a backend and append transcripts.

  python -m harness.run --backend claude --model claude-haiku-5-5 --items data/mbppplus.jsonl --n 5 --out runs/x.jsonl
  python -m harness.run --backend ollama --model <tag> ...
  python -m harness.run --backend oracle ...   (writes the reference/canonical solution; no model; pipeline check)

Items are taken in a seeded shuffled order (--seed). Already-finished (model, arm, task) triples in --out are skipped,
so a killed run resumes."""
import argparse
import json
import os
import random

from harness.backends import ClaudeCLIBackend, FakeBackend, OllamaBackend
from harness.runner import BackendBlocked, TranscriptWriter, load_items, run_item


def oracle_backend(item):
    code = item.get("reference_solution") or item["canonical_solution"]
    script = [(code, "done"), (None, "CONFIDENCE: 90")] + [(None, "I re-checked; it is correct. CONFIDENCE: 90")] * 3
    return FakeBackend(script, name="oracle")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=["claude", "ollama", "oracle"], required=True)
    ap.add_argument("--model", default="")
    ap.add_argument("--items", action="append", required=True)
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--arm", choices=["escalating", "neutral"], default="escalating")
    ap.add_argument("--out", required=True)
    ap.add_argument("--run-id", default="run")
    ap.add_argument("--sandbox-root", default=None)
    a = ap.parse_args()
    items = [i for p in a.items for i in load_items(p)]
    random.Random(a.seed).shuffle(items)
    items = items[:a.n]
    done = set()
    if os.path.exists(a.out):
        for l in open(a.out, encoding="utf-8"):
            r = json.loads(l)
            if r["kind"] == "rebuttal3":
                done.add((r["model"], r["arm"], r["task_id"]))
    w = TranscriptWriter(a.out)
    for it in items:
        if a.backend == "claude":
            b = ClaudeCLIBackend(a.model)
        elif a.backend == "ollama":
            b = OllamaBackend(a.model)
        else:
            b = oracle_backend(it)
        if (b.name, a.arm, it["task_id"]) in done:
            continue
        try:
            recs = run_item(it, b, w, a.run_id, arm=a.arm, sandbox_root=a.sandbox_root)
        except BackendBlocked as e:
            raise SystemExit(f"stopped: a hook refused the call before it reached the model ({e})")
        print(it["task_id"], [int(r["hidden_pass"]) for r in recs], [r["confidence"] for r in recs])


if __name__ == "__main__":
    main()
