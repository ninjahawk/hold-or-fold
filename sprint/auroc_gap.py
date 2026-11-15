"""POST-HOC analysis added after review (Sun 11-15), NOT preregistered; no new model calls.
Tests the central contrast directly: gap = AUROC_hold - AUROC_fix per model, where
  AUROC_hold = initial confidence c0 predicting 'still passes after rebuttal 3' on originally-correct items,
  AUROC_fix  = initial confidence c0 predicting 'passes after rebuttal 3' on originally-wrong items
(the same AUROCs as analyze.link / redteam_analysis.auroc_of, all items, main arm).
The two AUROCs use disjoint item sets, so the bootstrap is stratified: originally-correct and originally-wrong items
are resampled separately (10,000 replicates, seed 0); 95% percentile CI; two-sided bootstrap p-value against 0
(2 * min tail share, as in redteam_analysis.boot_p), Holm across the 2 models. Secondary contrast:
|AUROC_hold - 0.5| - |AUROC_fix - 0.5| (distance from chance), reported but not primary.

  python sprint/auroc_gap.py -> sprint/out/auroc_gap.json + sprint/out/auroc_gap.md"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, "..", "prebuild")]
from harness import scorer  # noqa: E402
import analyze  # noqa: E402
from redteam_analysis import holm  # noqa: E402

MODELS = ("haiku", "sonnet")
NAME = {"haiku": "Haiku 5.5", "sonnet": "Sonnet 5.5"}
REPS, SEED = 10000, 0
O = lambda *p: os.path.join(HERE, "out", *p)  # noqa: E731


def arrays(model):
    tasks = scorer.per_task(scorer.load(O(f"{model}.jsonl")))[0].popitem()[1]
    c0 = np.array([t["c"][0] for t in tasks], float)
    y0 = np.array([t["y"][0] for t in tasks], int)
    y3 = np.array([t["y"][3] for t in tasks], int)
    return (c0[y0 == 1], y3[y0 == 1]), (c0[y0 == 0], y3[y0 == 0])


def p_two_sided(d, null=0.0):
    return float(min(1.0, 2 * min((d <= null).mean(), (d >= null).mean())))


def run(model, rng):
    (xh, yh), (xf, yf) = arrays(model)
    ah, af = analyze.auroc(xh, yh), analyze.auroc(xf, yf)
    gaps, dist = [], []
    for _ in range(REPS):
        i = rng.integers(0, len(xh), len(xh))
        j = rng.integers(0, len(xf), len(xf))
        bh, bf = analyze.auroc(xh[i], yh[i]), analyze.auroc(xf[j], yf[j])
        if np.isnan(bh) or np.isnan(bf):
            continue
        gaps.append(bh - bf)
        dist.append(abs(bh - .5) - abs(bf - .5))
    gaps, dist = np.array(gaps), np.array(dist)
    q = lambda a: [float(np.quantile(a, .025)), float(np.quantile(a, .975))]  # noqa: E731
    return {"n_hold": int(len(xh)), "n_hold_pos": int(yh.sum()), "n_fix": int(len(xf)), "n_fix_pos": int(yf.sum()),
            "auroc_hold": ah, "auroc_fix": af,
            "gap": ah - af, "gap_ci": q(gaps), "gap_p": p_two_sided(gaps),
            "dist_gap": abs(ah - .5) - abs(af - .5), "dist_ci": q(dist), "dist_p": p_two_sided(dist),
            "valid_draws": int(len(gaps))}


def main():
    rng = np.random.default_rng(SEED)
    R = {m: run(m, rng) for m in MODELS}
    for key in ("gap", "dist"):
        for m, a in zip(MODELS, holm([R[m][f"{key}_p"] for m in MODELS])):
            R[m][f"{key}_p_holm"] = a
    json.dump({"reps": REPS, "seed": SEED, "post_hoc": True, "models": R}, open(O("auroc_gap.json"), "w"), indent=1)
    f = lambda x, d=2: f"{x:.{d}f}"  # noqa: E731
    L = ["# AUROC gap test (POST-HOC, added after review 11-15, not preregistered)", "",
         f"Stratified bootstrap (originally-correct and originally-wrong items resampled separately), {REPS} replicates, "
         f"seed {SEED}, 95% percentile CI, two-sided bootstrap p (2 x min tail share; resolution 1/{REPS}), Holm over 2 models.", "",
         "| model | AUROC_hold (n, held) | AUROC_fix (n, fixed) | gap [95% CI] | p | p (Holm) | "
         "distance-from-0.5 gap [95% CI] | p | p (Holm) |", "|---|---|---|---|---|---|---|---|---|"]
    for m in MODELS:
        r = R[m]
        L.append(f"| {NAME[m]} | {f(r['auroc_hold'])} ({r['n_hold']}, {r['n_hold_pos']}) | {f(r['auroc_fix'])} "
                 f"({r['n_fix']}, {r['n_fix_pos']}) | {f(r['gap'])} [{f(r['gap_ci'][0])}, {f(r['gap_ci'][1])}] | "
                 f"{f(r['gap_p'], 4)} ({f(r['gap_p'], 3)}) | {f(r['gap_p_holm'], 4)} ({f(r['gap_p_holm'], 3)}) | {f(r['dist_gap'])} [{f(r['dist_ci'][0])}, "
                 f"{f(r['dist_ci'][1])}] | {f(r['dist_p'], 4)} ({f(r['dist_p'], 3)}) | {f(r['dist_p_holm'], 4)} ({f(r['dist_p_holm'], 3)}) |")
    L += ["", "p = 0.0000 means no replicate crossed 0 (p < 0.0001 at this resolution).", ""]
    open(O("auroc_gap.md"), "w").write("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main()
