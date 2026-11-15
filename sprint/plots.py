"""Figures from real transcripts, in the preexisting style (prebuild/harness/plots.py): reliability diagram +
claim-defense curves, vector PDF + PNG. Uses the frozen scorer's summary format.

  python sprint/plots.py --models haiku sonnet   -> sprint/fig/headline.{pdf,png}, headline_nontrap, headline_trap"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "prebuild")]
from harness import scorer  # noqa: E402
from harness.plots import headline  # noqa: E402

NAMES = {"claude:claude-haiku-5-5": "Haiku 5.5", "claude:claude-sonnet-5-5": "Sonnet 5.5"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--key", default="main")
    a = ap.parse_args()
    sfx = "" if a.key == "main" else f"_{a.key}"
    recs = [r for m in a.models for r in scorer.load(os.path.join(HERE, "out", f"{m}{sfx}.jsonl"))]
    for r in recs:
        r["model"] = NAMES.get(r["model"], r["model"])
    os.makedirs(os.path.join(HERE, "fig"), exist_ok=True)
    for sub, keep in (("", lambda r: True), ("_nontrap", lambda r: not r["is_trap"]), ("_trap", lambda r: r["is_trap"])):
        sub_recs = [dict(r) for r in recs if keep(r)]
        if sub == "_trap":  # the frozen scorer's summarize() crashes on an empty non-trap split; the figure does not use the split
            for r in sub_recs:
                r["is_trap"] = False
        s = scorer.summarize(sub_recs)
        print(headline(s, os.path.join(HERE, "fig", f"headline{sfx}{sub}")))


if __name__ == "__main__":
    main()
