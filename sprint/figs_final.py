"""Final paper figures. Every plotted number is read from sprint/out/results.json (main arm) or
sprint/out/results_robust.json (neutral control arm); nothing is recomputed from transcripts here except
Wilson intervals for reliability bins, which use the bin n and accuracy stored in results.json.

  python sprint/figs_final.py   -> sprint/fig/hero.{pdf,png}, sprint/fig/calib_defense.{pdf,png}

Turn mapping (records per item): turn 0 = solve, turn 1 = confidence elicitation (state y0, c0),
turns 2-4 = rebuttals R1 (neutral re-check), R2 (reviewer says it fails), R3 (hidden tests fail, fix it)."""
import json
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402

for _f in ("/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
           "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"):
    if os.path.exists(_f):  # Times-metric serif; matplotlib's cache may not list it
        font_manager.fontManager.addfont(_f)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
FIG = os.path.join(HERE, "fig")

plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Liberation Serif", "Nimbus Roman", "Times New Roman", "DejaVu Serif"],
    "mathtext.fontset": "stix", "font.size": 8, "axes.labelsize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7,
    "legend.fontsize": 7, "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": 0.6,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6, "lines.linewidth": 1.2, "pdf.fonttype": 42, "ps.fonttype": 42,
    "savefig.dpi": 300,
})
# Okabe-Ito (colorblind-safe)
COL = {"haiku": "#0072B2", "sonnet": "#D55E00"}
NAME = {"haiku": "Haiku 5.5", "sonnet": "Sonnet 5.5"}
TURNS = ["Initial\nclaim", "R1\nre-check", "R2\nreviewer:\nfails", "R3\ntests fail,\nfix it"]


def load(name):
    with open(os.path.join(OUT, name), encoding="utf-8") as f:
        return json.load(f)["models"]


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"),) * 2
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def curves(m):
    """Pass rate on hidden tests by turn, originally-correct and originally-wrong items, with bootstrap CIs."""
    p, ci = m["all"]["point"], m["all"]["ci"]
    held = [1.0] + [1 - p[f"ftw_{k}"] for k in (1, 2, 3)]
    held_lo = [1.0] + [1 - ci[f"ftw_{k}"][1] for k in (1, 2, 3)]
    held_hi = [1.0] + [1 - ci[f"ftw_{k}"][0] for k in (1, 2, 3)]
    fixed = [0.0] + [p[f"ftr_{k}"] for k in (1, 2, 3)]
    fixed_lo = [0.0] + [ci[f"ftr_{k}"][0] for k in (1, 2, 3)]
    fixed_hi = [0.0] + [ci[f"ftr_{k}"][1] for k in (1, 2, 3)]
    return (held, held_lo, held_hi), (fixed, fixed_lo, fixed_hi)


def errbar(ax, x, y, lo, hi, **kw):
    yerr = [[100 * (a - b) for a, b in zip(y, lo)], [100 * (b - a) for a, b in zip(y, hi)]]
    return ax.errorbar(x, [100 * v for v in y], yerr=yerr, capsize=1.5, elinewidth=0.6, markersize=3.2, **kw)


def defense_panel(ax, main, robust, legend=True):
    for i, mk in enumerate(("haiku", "sonnet")):
        dx = -0.07 if i == 0 else 0.07
        x = [t + dx for t in range(4)]
        (h, hl, hh), (f, fl, fh) = curves(main[mk])
        n_c, n_w = main[mk]["all"]["point"]["n_correct0"], main[mk]["all"]["point"]["n_wrong0"]
        errbar(ax, x, h, hl, hh, color=COL[mk], marker="o", ls="-",
               label=f"{NAME[mk]}, initially correct (n={n_c})")
        errbar(ax, x, f, fl, fh, color=COL[mk], marker="s", ls="--", mfc="white",
               label=f"{NAME[mk]}, initially wrong (n={n_w})")
        if robust is not None:  # neutral control arm, after the third neutral re-check
            rp, rc = robust[mk]["all"]["point"], robust[mk]["all"]["ci"]
            xr = 4.0 + dx
            ax.errorbar([xr], [100 * rp["ftr_3"]], yerr=[[100 * (rp["ftr_3"] - rc["ftr_3"][0])],
                                                         [100 * (rc["ftr_3"][1] - rp["ftr_3"])]],
                        color=COL[mk], marker="^", mfc="white", ls="none", capsize=1.5, elinewidth=0.6, markersize=3.2)
    ticks, labels = list(range(4)), list(TURNS)
    if robust is not None:
        ax.axvline(3.5, color="0.8", lw=0.5)
        ticks.append(4.0)
        labels.append("Control:\n3x neutral\nre-check")
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels)
    ax.set_xlim(-0.3, 4.3)
    ax.set_ylim(-3, 103)
    ax.set_ylabel("Passing hidden tests (%)")
    ax.set_xlabel("Turn")
    if legend:
        ax.legend(loc="center left", frameon=False, handlelength=2.2, borderaxespad=0.2, bbox_to_anchor=(0.0, 0.52))


def link_panel(ax, main):
    labels = ["Holds when\ninitially correct", "Fixes when\ninitially wrong"]
    keys = ["held_correct_auroc", "fixed_wrong_auroc"]
    for i, mk in enumerate(("haiku", "sonnet")):
        L, C = main[mk]["link"], main[mk]["link_ci"]
        xs = [j + (-0.12 if i == 0 else 0.12) for j in range(2)]
        ys = [L[k] for k in keys]
        lo = [y - C[k][0] for y, k in zip(ys, keys)]
        hi = [C[k][1] - y for y, k in zip(ys, keys)]
        ax.errorbar(xs, ys, yerr=[lo, hi], color=COL[mk], marker="o" if i == 0 else "D", ls="none", capsize=2,
                    elinewidth=0.8, markersize=3.6, label=NAME[mk])
        for x, y, k in zip(xs, ys, ("held_correct", "fixed_wrong")):
            ax.annotate(f"{L[k + '_n_pos']}/{L[k + '_n']}", xy=(x, C[k + "_auroc"][0]), xytext=(0, -7),
                        textcoords="offset points", ha="center", fontsize=5.5, color=COL[mk])
    ax.axhline(0.5, color="0.5", lw=0.6, ls=":")
    ax.text(1.45, 0.505, "chance", fontsize=6, color="0.4", va="bottom", ha="right")
    ax.set_xticks(range(2))
    ax.set_xticklabels(labels)
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(0.1, 1.0)
    ax.set_ylabel("AUROC of initial confidence")
    ax.legend(loc="upper right", frameon=False)


def pool_bins(rows, min_n=10):
    """Merge consecutive low-confidence bins (from the bottom) until each plotted bin has >= min_n items;
    n-weighted means of the per-bin values stored in results.json."""
    out, acc = [], []
    for r in rows:
        acc.append(r)
        if sum(a["n"] for a in acc) >= min_n:
            n = sum(a["n"] for a in acc)
            out.append({"n": n, "conf": sum(a["conf"] * a["n"] for a in acc) / n,
                        "acc": sum(a["acc"] * a["n"] for a in acc) / n})
            acc = []
    if acc:  # leftover top bins (should not happen: the top bin is the largest)
        n = sum(a["n"] for a in acc)
        out.append({"n": n, "conf": sum(a["conf"] * a["n"] for a in acc) / n,
                    "acc": sum(a["acc"] * a["n"] for a in acc) / n})
    return out


def reliability_panel(ax, main):
    ax.plot([0, 1], [0, 1], color="0.5", lw=0.6, ls=":")
    for i, mk in enumerate(("haiku", "sonnet")):
        rows = pool_bins(main[mk]["reliability"])
        x = [r["conf"] for r in rows]
        y = [r["acc"] for r in rows]
        ci = [wilson(round(r["acc"] * r["n"]), r["n"]) for r in rows]
        ax.errorbar(x, y, yerr=[[a - c[0] for a, c in zip(y, ci)], [c[1] - a for a, c in zip(y, ci)]],
                    color=COL[mk], marker="o" if i == 0 else "D", ls="-", lw=0.9, capsize=1.5, elinewidth=0.5,
                    markersize=0, alpha=0.9)
        ax.scatter(x, y, s=[6 + 0.25 * r["n"] for r in rows], color=COL[mk], marker="o" if i == 0 else "D",
                   zorder=3, label=f"{NAME[mk]} (ECE {main[mk]['all']['point']['ece']:.2f})", edgecolors="white",
                   linewidths=0.3)
    ax.set_xlim(0.2, 1.0)
    ax.set_ylim(0.2, 1.02)
    ax.set_xlabel("Stated confidence (bin mean)")
    ax.set_ylabel("Fraction passing hidden tests")
    ax.legend(loc="upper left", frameon=False, markerscale=0.6)
    ax.text(0.98, 0.03, "10 equal-width bins; sparse low bins pooled to n>=10;\nmarker area ~ items in bin; bars: Wilson 95%", fontsize=5.5, color="0.35", ha="right",
            va="bottom", transform=ax.transAxes)


def flip_panel(ax, main):
    ks = [1, 2, 3]
    for i, mk in enumerate(("haiku", "sonnet")):
        p, ci = main[mk]["all"]["point"], main[mk]["all"]["ci"]
        dx = -0.06 if i == 0 else 0.06
        for key, ls, mkr, lab in (("ftw", "-", "o", "flip to wrong (FTW)"), ("ftr", "--", "s", "flip to right (FTR)")):
            y = [p[f"{key}_{k}"] for k in ks]
            lo = [ci[f"{key}_{k}"][0] for k in ks]
            hi = [ci[f"{key}_{k}"][1] for k in ks]
            errbar(ax, [k + dx for k in ks], y, lo, hi, color=COL[mk], marker=mkr, ls=ls,
                   mfc="white" if key == "ftr" else COL[mk], label=f"{NAME[mk]}, {lab}")
    ax.set_xticks(ks)
    ax.set_xticklabels(TURNS[1:])
    ax.set_xlim(0.7, 3.3)
    ax.set_ylim(-2, 60)
    ax.set_xlabel("Rebuttal")
    ax.set_ylabel("Rate (%)")
    ax.legend(loc="upper left", frameon=False, fontsize=6.5)


def save(fig, stem):
    for ext in ("pdf", "png"):
        fig.savefig(os.path.join(FIG, f"{stem}.{ext}"), bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)
    return stem


def main():
    main_ = load("results.json")
    robust = load("results_robust.json")
    os.makedirs(FIG, exist_ok=True)
    # HERO: (a) claim-defense trajectories, (b) does initial confidence predict holding vs fixing
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.7), gridspec_kw={"width_ratios": [1.75, 1]})
    defense_panel(a, main_, robust)
    link_panel(b, main_)
    for ax, t in ((a, "(a)"), (b, "(b)")):
        ax.text(-0.12, 1.02, t, transform=ax.transAxes, fontsize=8, fontweight="bold", va="bottom")
    fig.tight_layout(w_pad=1.5)
    print(save(fig, "hero"))
    # Reliability diagram + claim-defense (flip-rate) curves, both models side by side
    fig, (a, b) = plt.subplots(1, 2, figsize=(7.0, 2.6))
    reliability_panel(a, main_)
    flip_panel(b, main_)
    for ax, t in ((a, "(a)"), (b, "(b)")):
        ax.text(-0.12, 1.02, t, transform=ax.transAxes, fontsize=8, fontweight="bold", va="bottom")
    fig.tight_layout(w_pad=1.5)
    print(save(fig, "calib_defense"))


if __name__ == "__main__":
    main()
