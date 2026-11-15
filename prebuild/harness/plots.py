"""Headline figure, plain paper style (serif, vector PDF + PNG; same fonts/palette as the last sprint's figures):
(a) reliability diagram of initial confidence vs hidden-test pass,
(b) claim-defense curves: flip-to-wrong on originally-correct items (solid) and flip-to-right on
originally-wrong items (dashed) after rebuttal 1..3, with bootstrap CIs.

  python -m harness.plots <summary.json> <out_stem> [--label SYNTHETIC]   -> <out_stem>.pdf and <out_stem>.png"""
import argparse
import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

STYLE = {"font.family": "STIXGeneral", "mathtext.fontset": "stix", "font.size": 9, "axes.linewidth": .6,
         "xtick.major.width": .6, "ytick.major.width": .6, "legend.frameon": False, "pdf.fonttype": 42}
C1, C2, G = "#1f4e79", "#b5523b", "#8c8c8c"
PALETTE = [C1, C2, "#636363", "#bdbdbd"]
MARKERS = ["o", "s", "D", "^"]


def headline(summary, path, label=None):
    """Writes <stem>.pdf and <stem>.png (path may end in .png/.pdf or be a bare stem). Returns the stem."""
    stem = os.path.splitext(path)[0] if path.lower().endswith((".png", ".pdf")) else path
    with plt.rc_context(STYLE):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.5, 2.6))
        ax1.plot([0, 1], [0, 1], color=G, lw=.6, ls="--")
        for i, (key, v) in enumerate(summary.items()):
            col, mk = PALETTE[i % len(PALETTE)], MARKERS[i % len(MARKERS)]
            name = key.split("|")[0]
            rel = v["reliability"]
            ax1.plot([r["conf"] for r in rel], [r["acc"] for r in rel], marker=mk, color=col, lw=.9, ms=3.5,
                     label=f"{name} (ECE {v['all']['ece']:.2f})")
            m, ci = v["all"], v["ci"]
            xs = [0, 1, 2, 3]
            for kind, ls in (("ftw", "-"), ("ftr", "--")):
                ys = [0.0] + [m[f"{kind}_{k}"] for k in (1, 2, 3)]
                lo = [0.0] + [ci[f"{kind}_{k}"][0] for k in (1, 2, 3)]
                hi = [0.0] + [ci[f"{kind}_{k}"][1] for k in (1, 2, 3)]
                ax2.plot(xs, ys, ls, color=col, marker=mk, ms=3.5, lw=.9,
                         mfc=col if kind == "ftw" else "white",
                         label=f"{name}, {'flip-to-wrong' if kind == 'ftw' else 'flip-to-right'}")
                if None not in lo and None not in hi:
                    ax2.fill_between(xs, lo, hi, color=col, alpha=.10, lw=0)
        ax1.set(xlabel="Stated confidence (hidden tests pass)", ylabel="Fraction passing hidden tests",
                xlim=(0, 1), ylim=(0, 1))
        ax1.set_title("(a) Reliability", fontsize=9)
        ax2.set(xlabel="Rebuttal level (0 = original claim)", ylabel="Rate", ylim=(0, 1), xticks=[0, 1, 2, 3])
        ax2.set_title("(b) Claim-defense curves", fontsize=9)
        for ax in (ax1, ax2):
            ax.spines[["top", "right"]].set_visible(False)
        ax1.legend(fontsize=7, loc="upper left")
        ax2.legend(fontsize=6.5, loc="upper left")
        if label:
            for ax in (ax1, ax2):
                ax.text(.98, .04, label, transform=ax.transAxes, ha="right", va="bottom", fontsize=11,
                        color=C2, alpha=.6, fontweight="bold")
        fig.tight_layout()
        fig.savefig(stem + ".pdf")
        fig.savefig(stem + ".png", dpi=200)
        plt.close(fig)
    return stem


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("summary")
    ap.add_argument("out_stem")
    ap.add_argument("--label")
    a = ap.parse_args()
    with open(a.summary, encoding="utf-8") as f:
        s = json.load(f)
    os.makedirs(os.path.dirname(os.path.abspath(a.out_stem)), exist_ok=True)
    print(headline(s, a.out_stem, a.label))


if __name__ == "__main__":
    main()
