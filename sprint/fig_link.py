"""Calibration-defense link figure (sprint): for each model, P(held after rebuttal 3 | originally correct) and
P(fixed after rebuttal 3 | originally wrong) by initial-confidence band (<80, 80-89, >=90; bands fixed before the
Sonnet data were seen), with Wilson 95% intervals and n per point. Style as prebuild/harness/plots.py.

  python sprint/fig_link.py --models haiku sonnet  -> sprint/fig/link.{pdf,png} + sprint/out/link_bands.json"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "prebuild"), HERE]
import matplotlib  # noqa: E402

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from analyze import wilson  # noqa: E402
from harness import scorer  # noqa: E402
from harness.plots import G, MARKERS, PALETTE, STYLE  # noqa: E402

BANDS = [("<80", 0, .80), ("80-89", .80, .90), (">=90", .90, 1.01)]
NAMES = {"haiku": "Haiku 5.5", "sonnet": "Sonnet 5.5"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    a = ap.parse_args()
    out = {}
    with plt.rc_context(STYLE):
        fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.6), sharey=True)
        for i, m in enumerate(a.models):
            groups, _ = scorer.per_task(scorer.load(os.path.join(HERE, "out", f"{m}.jsonl")))
            (_, tasks), = groups.items()
            out[m] = {}
            for ax, (cls, y0, want) in zip(axes, (("held | originally correct", 1, 1), ("fixed | originally wrong", 0, 1))):
                xs, ys, lo, hi, ns = [], [], [], [], []
                for j, (lab, a0, a1) in enumerate(BANDS):
                    s = [t for t in tasks if t["y"][0] == y0 and a0 <= t["c"][0] < a1]
                    k = sum(1 for t in s if t["y"][3] == want)
                    out[m][f"{cls} {lab}"] = {"k": k, "n": len(s), "rate": k / len(s) if s else None, "wilson": wilson(k, len(s))}
                    if s:
                        w = wilson(k, len(s))
                        xs.append(j + (i - .5) * .12); ys.append(k / len(s)); lo.append(k / len(s) - w[0]); hi.append(w[1] - k / len(s)); ns.append(len(s))
                col, mk = PALETTE[i], MARKERS[i]
                ax.errorbar(xs, ys, yerr=[lo, hi], color=col, marker=mk, ms=3.5, lw=.9, capsize=2, label=NAMES.get(m, m))
                for x, y, n in zip(xs, ys, ns):
                    ax.annotate(f"n={n}", (x, y), textcoords="offset points", xytext=(-16, -10) if i == 0 else (4, 5),
                                fontsize=6, color=col)
                    if n < 5:  # 11-14 (red-team J3/S18): tiny bands drawn hollow
                        ax.plot([x], [y], marker=mk, ms=5, mfc="white", color=col, ls="none", zorder=4)
                ax.text(-0.12, 1.02, "(a)" if y0 else "(b)", transform=ax.transAxes, fontsize=8, fontweight="bold")
                ax.set_ylabel(f"P({cls.split(' |')[0]} after rebuttal 3)" if y0 else "P(fixed after rebuttal 3)")
                ax.set_xticks(range(len(BANDS)), [b[0] for b in BANDS])
                ax.set_xlabel("Initial stated confidence")
                ax.set_ylim(0, 1.05)
                ax.spines[["top", "right"]].set_visible(False)
        axes[1].tick_params(labelleft=True)
        axes[0].set_xlabel("Initial stated confidence (originally correct)")
        axes[1].set_xlabel("Initial stated confidence (originally wrong)")
        axes[0].legend(fontsize=7, loc="lower right")
        fig.tight_layout()
        stem = os.path.join(HERE, "fig", "link")
        fig.savefig(stem + ".pdf"); fig.savefig(stem + ".png", dpi=200)
        plt.close(fig)
    json.dump(out, open(os.path.join(HERE, "out", "link_bands.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
