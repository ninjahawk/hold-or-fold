"""Synthetic transcripts with known ground truth, to exercise the scorer and plots without any model.

Each fake model has: p_correct, a confidence rule, and per-rebuttal probabilities of flipping
correct work to wrong (capitulation) and wrong work to right (warranted update). Records have the
same schema as harness.runner output; solution code is a placeholder, hidden_pass is drawn.

usage: python -m harness.synth <out.jsonl> [--n 300] [--seed 0]"""
import argparse
import json

import numpy as np


KINDS = ["solve", "confidence", "rebuttal1", "rebuttal2", "rebuttal3"]

PROFILES = {
    # calibrated, defends correct work, fixes some wrong work
    "synthetic:steady": dict(p=0.7, conf=lambda y, r: np.clip(0.7 + r.normal(0, 0.1), 0, 1), ftw=[0.02, 0.04, 0.06], ftr=[0.1, 0.2, 0.3]),
    # overconfident, capitulates under pressure
    "synthetic:folder": dict(p=0.6, conf=lambda y, r: np.clip(0.95 + r.normal(0, 0.03), 0, 1), ftw=[0.05, 0.25, 0.45], ftr=[0.05, 0.1, 0.15]),
}


def gen(n=300, seed=0, trap_frac=0.15):
    r = np.random.default_rng(seed)
    recs = []
    for model, P in PROFILES.items():
        for i in range(n):
            tid = f"synthetic/{i}" + ("#trap" if i < int(n * trap_frac) else "")
            y = int(r.random() < P["p"])
            c0 = float(P["conf"](y, r))
            # cumulative targets: flip happens at the first level k with u < target[k], then stays
            u = r.random()
            target = P["ftw"] if y == 1 else P["ftr"]
            flip_at = next((k for k in range(3) if u < target[k]), None)
            ys = [y, y] + [(1 - y) if flip_at is not None and k >= flip_at else y for k in range(3)]
            cs = [None, round(100 * c0)] + [round(100 * float(np.clip(c0 - 0.1 * (k + 1) * model.endswith("folder"), 0, 1)))
                                           for k in range(3)]
            ver = [0, 0] + [int(flip_at is not None and k >= flip_at) for k in range(3)]
            changed = [None] + [ver[t] != ver[t - 1] for t in range(1, 5)]
            for t, kind in enumerate(KINDS):
                recs.append({"run_id": "synthetic", "model": model, "arm": "escalating", "task_id": tid,
                             "is_trap": tid.endswith("#trap"), "turn": t, "kind": kind, "prompt": "", "response": "",
                             "confidence": cs[t], "solution_sha": f"{tid}:{ver[t]}",
                             "changed": changed[t], "hidden_pass": bool(ys[t]), "hidden_n_passed": None,
                             "hidden_n": 10, "exec_error": None, "backend_error": None})
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    with open(a.out, "w", encoding="utf-8") as f:
        for rec in gen(a.n, a.seed):
            f.write(json.dumps(rec) + "\n")


if __name__ == "__main__":
    main()
