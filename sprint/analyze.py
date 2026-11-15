"""All preregistered metrics with 95% bootstrap CIs, the calibration-defense link test, trap split and paired model
comparisons. Uses the frozen scorer (prebuild/harness/scorer.py) for every metric definition.

  python sprint/analyze.py --models haiku sonnet [--key main] -> sprint/out/results[_key].json + results_tables[_key].md"""
import argparse
import json
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "prebuild")]
from harness import scorer  # noqa: E402

REPS, SEED = 2000, 0
TRAPS = os.path.join(HERE, "..", "prebuild", "data", "traps.jsonl")
DEGEN = re.compile(r"\bempty\b|no sublists|zero numbers|zero-length|no power of 2", re.I)


def degenerate_trap_ids():
    return {t["task_id"] for t in map(json.loads, open(TRAPS)) if DEGEN.search(t["trap_rationale"])}


def extra(m):
    m = dict(m)
    m["contrast_3"] = m["ftr_3"] - m["ftw_3"] if not (np.isnan(m["ftr_3"]) or np.isnan(m["ftw_3"])) else float("nan")
    for k in (1, 2):
        m[f"contrast_{k}"] = m[f"ftr_{k}"] - m[f"ftw_{k}"]
    return m


def boot(tasks, fn, reps=REPS, seed=SEED):
    """Percentile bootstrap over tasks of every key fn returns (NaN draws dropped)."""
    rng = np.random.default_rng(seed)
    n = len(tasks)
    draws = {}
    for _ in range(reps):
        s = [tasks[i] for i in rng.integers(0, n, n)]
        for k, v in fn(s).items():
            draws.setdefault(k, []).append(v)
    out = {}
    for k, v in draws.items():
        a = np.array([x for x in v if x is not None], float)
        a = a[~np.isnan(a)]
        out[k] = [float(np.quantile(a, .025)), float(np.quantile(a, .975)), int(len(a))] if len(a) else [None, None, 0]
    return out


def logit_slope(x, y, iters=50):
    """MLE logistic regression y ~ a + b*x (IRLS). Returns b, or nan if a class has < 5 items or no convergence."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    if min(y.sum(), len(y) - y.sum()) < 5 or np.ptp(x) == 0:
        return float("nan")
    X = np.c_[np.ones_like(x), x]
    w = np.zeros(2)
    for _ in range(iters):
        p = 1 / (1 + np.exp(-X @ w))
        W = p * (1 - p)
        H = X.T @ (X * W[:, None])
        try:
            step = np.linalg.solve(H, X.T @ (y - p))
        except np.linalg.LinAlgError:
            return float("nan")
        w += step
        if np.abs(step).max() < 1e-8:
            break
    else:
        return float("nan")
    return float(w[1]) if abs(w[1]) < 1e3 else float("nan")


def auroc(x, y):
    """P(x of a random positive > x of a random negative), ties 1/2. nan if a class is empty."""
    x, y = np.asarray(x, float), np.asarray(y, int)
    pos, neg = x[y == 1], x[y == 0]
    if not len(pos) or not len(neg):
        return float("nan")
    gt = (pos[:, None] > neg[None, :]).sum() + .5 * (pos[:, None] == neg[None, :]).sum()
    return float(gt / (len(pos) * len(neg)))


def link(tasks):
    """(a) held on originally-correct, (b) fixed on originally-wrong, (c) pooled ends-correct; slope per 0.1 of c0."""
    out = {}
    c0 = np.array([t["c"][0] for t in tasks], float)
    y0 = np.array([t["y"][0] for t in tasks], int)
    y3 = np.array([t["y"][3] for t in tasks], int)
    for name, mask in (("held_correct", y0 == 1), ("fixed_wrong", y0 == 0), ("pooled_end_correct", np.ones_like(y0, bool))):
        x, y = c0[mask] * 10, y3[mask]  # *10: slope = log-odds per 0.1 of confidence
        out[f"{name}_n"] = int(mask.sum())
        out[f"{name}_n_pos"] = int(y.sum())
        out[f"{name}_slope"] = logit_slope(x, y)
        out[f"{name}_auroc"] = auroc(x, y)
    return out


def link_point_and_ci(tasks):
    pt = link(tasks)
    ci = boot(tasks, lambda s: {k: v for k, v in link(s).items() if k.endswith(("_slope", "_auroc"))})
    return pt, ci


def block(tasks):
    m = extra(scorer.metrics(tasks))
    ci = boot(tasks, lambda s: extra(scorer.metrics(s)))
    return {"point": m, "ci": ci}


def analyze_model(path):
    recs = scorer.load(path)
    groups, dropped = scorer.per_task(recs)
    assert len(groups) == 1, groups.keys()
    (key, tasks), = groups.items()
    degen = degenerate_trap_ids()
    trap = [t for t in tasks if t["is_trap"]]
    non = [t for t in tasks if not t["is_trap"]]
    res = {"key": "|".join(key), "dropped_incomplete_or_no_conf": dropped[key],
           "n_conf_parse_fail_turns": sum(1 for r in recs if r["kind"] != "solve" and r["confidence"] is None),
           "all": block(tasks), "nontrap": block(non), "trap": block(trap),
           "trap_without_degenerate": block([t for t in trap if t["task_id"] not in degen]),
           "trap_degenerate_only": block([t for t in trap if t["task_id"] in degen]),
           "reliability": scorer.reliability([t["c"][0] for t in tasks], [t["y"][0] for t in tasks]),
           "reliability_nontrap": scorer.reliability([t["c"][0] for t in non], [t["y"][0] for t in non]),
           "reliability_trap": scorer.reliability([t["c"][0] for t in trap], [t["y"][0] for t in trap])}
    res["flip_counts"] = {"all": flip_counts(tasks), "nontrap": flip_counts(non), "trap": flip_counts(trap)}
    res["link"], res["link_ci"] = link_point_and_ci(tasks)
    res["link_nontrap"], res["link_nontrap_ci"] = link_point_and_ci(non)
    res["n_wrong0_nontrap"] = res["nontrap"]["point"]["n_wrong0"]
    res["nontrap_ftr_powered"] = res["n_wrong0_nontrap"] >= 15
    res["n_degenerate_traps"] = len([t for t in trap if t["task_id"] in degen])
    return res, {t["task_id"]: t for t in tasks}


PAIR_KEYS = ["acc0", "mean_conf0", "brier", "ece", "overconf", "ftw_3", "ftr_3", "contrast_3"]


def paired(ta, tb):
    shared = sorted(set(ta) & set(tb))
    pairs = [(ta[i], tb[i]) for i in shared]

    def diff(s):
        ma, mb = extra(scorer.metrics([p[0] for p in s])), extra(scorer.metrics([p[1] for p in s]))
        return {k: mb[k] - ma[k] for k in PAIR_KEYS}
    pt = diff(pairs)
    ci = boot(pairs, diff)
    both_wrong = sum(1 for a, b in pairs if a["y"][0] == 0 and b["y"][0] == 0)
    return {"n_shared": len(shared), "diff_b_minus_a": pt, "ci": ci, "n_both_wrong0": both_wrong}


def f(x, d=2):
    return "nan" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.{d}f}"


def wilson(k, n, z=1.959964):
    if not n:
        return [None, None]
    ph = k / n
    d = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / d
    h = z * (ph * (1 - ph) / n + z * z / (4 * n * n)) ** .5 / d
    return [max(0.0, c - h), min(1.0, c + h)]


def flip_counts(tasks):
    """Supplementary (not preregistered): raw counts and Wilson 95% intervals for FTW_k / FTR_k, because the
    percentile bootstrap collapses to [0, 0] when a rate is exactly 0."""
    out = {}
    corr = [t for t in tasks if t["y"][0] == 1]
    wrong = [t for t in tasks if t["y"][0] == 0]
    for k in (1, 2, 3):
        a = sum(1 for t in corr if t["y"][k] == 0)
        b = sum(1 for t in wrong if t["y"][k] == 1)
        out[f"ftw_{k}"] = {"k": a, "n": len(corr), "wilson": wilson(a, len(corr))}
        out[f"ftr_{k}"] = {"k": b, "n": len(wrong), "wilson": wilson(b, len(wrong))}
    return out


def table(results):
    L = []
    for model, r in results["models"].items():
        L.append(f"\n### {model} ({r['key']})\n")
        L.append(f"dropped (incomplete or no initial confidence): {r['dropped_incomplete_or_no_conf']}; "
                 f"turns without a parseable CONFIDENCE: {r['n_conf_parse_fail_turns']}\n")
        L.append("| subset | n | wrong0 | acc0 | conf0 | Brier | ECE | overconf | FTW_1 | FTW_2 | FTW_3 | FTR_1 | FTR_2 | FTR_3 | FTR_3-FTW_3 |")
        L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
        for sub in ("all", "nontrap", "trap", "trap_without_degenerate", "trap_degenerate_only"):
            p, c = r[sub]["point"], r[sub]["ci"]
            cell = lambda k: f"{f(p[k])} [{f(c[k][0])}, {f(c[k][1])}]" if k in c and c[k][0] is not None else f(p[k])
            L.append(f"| {sub} | {p['n']} | {p['n_wrong0']} | " + " | ".join(
                cell(k) for k in ("acc0", "mean_conf0", "brier", "ece", "overconf", "ftw_1", "ftw_2", "ftw_3",
                                  "ftr_1", "ftr_2", "ftr_3", "contrast_3")) + " |")
        p = r["all"]["point"]
        L.append("\nCode-change rate by turn k (all items): correct " + ", ".join(f(p[f'chg_correct_{k}']) for k in (1, 2, 3))
                 + "; wrong " + ", ".join(f(p[f'chg_wrong_{k}']) for k in (1, 2, 3))
                 + ". Confidence drop on correct items: " + ", ".join(f(p[f'conf_drop_correct_{k}']) for k in (1, 2, 3)))
        L.append("\nSupplementary (not preregistered) raw flip counts k/n with Wilson 95% intervals:\n")
        L.append("| subset | " + " | ".join(f"{m}_{k}" for m in ("ftw", "ftr") for k in (1, 2, 3)) + " |")
        L.append("|---|" + "---|" * 6)
        for sub, fc in r["flip_counts"].items():
            L.append(f"| {sub} | " + " | ".join(
                f"{fc[f'{m}_{k}']['k']}/{fc[f'{m}_{k}']['n']} [{f(fc[f'{m}_{k}']['wilson'][0])}, {f(fc[f'{m}_{k}']['wilson'][1])}]"
                for m in ("ftw", "ftr") for k in (1, 2, 3)) + " |")
        for lk in ("link", "link_nontrap"):
            lp, lc = r[lk], r[lk + "_ci"]
            L.append(f"\nCalibration-defense link ({'all items' if lk == 'link' else 'non-trap items'}; slope = log-odds per 0.1 confidence):\n")
            L.append("| outcome | n | n positive | slope [95% CI] | AUROC of c0 [95% CI] |")
            L.append("|---|---|---|---|---|")
            for name in ("held_correct", "fixed_wrong", "pooled_end_correct"):
                s, a = lc[f"{name}_slope"], lc[f"{name}_auroc"]
                # prereg: fewer than 5 items in an outcome class -> slope not estimable, AUROC only (fixed 11-14, S5)
                n_pos, n_all = lp[name + '_n_pos'], lp[name + '_n']
                if min(n_pos, n_all - n_pos) < 5 or lp[name + '_slope'] != lp[name + '_slope']:
                    sl = "not estimable (outcome class < 5)"
                else:
                    sl = f"{f(lp[name + '_slope'])} [{f(s[0])}, {f(s[1])}]" + (f" ({s[2]}/2000 draws)" if len(s) > 2 and s[2] < 2000 else "")
                au = (f"{f(lp[name + '_auroc'])} [{f(a[0])}, {f(a[1])}]" if min(n_pos, n_all - n_pos) >= 5 or
                      lp[name + '_auroc'] != lp[name + '_auroc'] else
                      f"{f(lp[name + '_auroc'])} [{f(a[0])}, {f(a[1])}] (outcome class < 5: uninformative)")
                L.append(f"| {name} | {n_all} | {n_pos} | {sl} | {au} |")
        L.append(f"\nNon-trap originally-wrong n = {r['n_wrong0_nontrap']} (prereg minimum 15 for non-trap FTR: "
                 f"{'met' if r['nontrap_ftr_powered'] else 'NOT met, non-trap FTR underpowered'}). Degenerate-input traps: {r['n_degenerate_traps']}.")
    for name, pr in results.get("paired", {}).items():
        L.append(f"\n### Paired {name} (n shared = {pr['n_shared']}, both wrong at start = {pr['n_both_wrong0']})\n")
        L.append("| metric | diff | 95% CI |")
        L.append("|---|---|---|")
        for k in PAIR_KEYS:
            c = pr["ci"][k]
            L.append(f"| {k} | {f(pr['diff_b_minus_a'][k], 3)} | [{f(c[0], 3)}, {f(c[1], 3)}] |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--key", default="main")
    ap.add_argument("--tables-only", action="store_true", help="re-render the tables from the existing results json")
    a = ap.parse_args()
    sfx = "" if a.key == "main" else f"_{a.key}"
    if a.tables_only:
        t = table(json.load(open(os.path.join(HERE, "out", f"results{sfx}.json"))))
        open(os.path.join(HERE, "out", f"results_tables{sfx}.md"), "w").write(t)
        print(t)
        return
    results, tasks = {"models": {}}, {}
    for m in a.models:
        results["models"][m], tasks[m] = analyze_model(os.path.join(HERE, "out", f"{m}{sfx}.jsonl"))
    if len(a.models) == 2:
        results["paired"] = {f"{a.models[1]} - {a.models[0]}": paired(tasks[a.models[0]], tasks[a.models[1]])}
    json.dump(results, open(os.path.join(HERE, "out", f"results{sfx}.json"), "w"), indent=1)
    t = table(results)
    open(os.path.join(HERE, "out", f"results_tables{sfx}.md"), "w").write(t)
    print(t)


if __name__ == "__main__":
    main()
