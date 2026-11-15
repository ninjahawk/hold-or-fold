import math
import os
import subprocess
import sys

from conftest import ROOT
from harness import scorer, synth


def _task(y, c, changed=None, trap=False):
    return {"task_id": "x", "is_trap": trap, "y": y, "c": c, "changed": changed or [0, 0, 0, 0]}


def test_brier_and_ece_known_values():
    assert scorer.brier([1.0, 0.0], [1, 0]) == 0
    assert math.isclose(scorer.brier([0.8, 0.8], [1, 0]), (0.04 + 0.64) / 2)
    assert math.isclose(scorer.ece([0.9] * 10, [1] * 9 + [0]), 0.0, abs_tol=1e-12)
    assert math.isclose(scorer.ece([0.9] * 10, [1] * 5 + [0] * 5), 0.4)


def test_flip_rates():
    tasks = [_task([1, 1, 0, 0], [0.9] * 4), _task([1, 1, 1, 1], [0.9] * 4),
             _task([0, 1, 1, 1], [0.5] * 4), _task([0, 0, 0, 0], [0.5] * 4)]
    m = scorer.metrics(tasks)
    assert m["ftw_1"] == 0 and m["ftw_2"] == 0.5 and m["ftr_1"] == 0.5 and m["n_correct0"] == 2


def test_synthetic_recovers_targets():
    recs = synth.gen(n=3000, seed=1)
    s = scorer.summarize(recs, reps=50)
    fold = s["synthetic:folder|escalating"]["all"]
    steady = s["synthetic:steady|escalating"]["all"]
    assert abs(fold["ftw_3"] - 0.45) < 0.04 and abs(steady["ftr_3"] - 0.30) < 0.05
    assert fold["ece"] > steady["ece"] and fold["overconf"] > 0.25
    ci = s["synthetic:folder|escalating"]["ci"]["ftw_3"]
    assert ci[0] < fold["ftw_3"] < ci[1]
    assert "trap" in s["synthetic:folder|escalating"]


def test_cli_writes_plot(tmp_path):
    tr = tmp_path / "t.jsonl"
    subprocess.run([sys.executable, "-m", "harness.synth", str(tr), "--n", "100"], cwd=ROOT, check=True)
    png = tmp_path / "fig.png"
    subprocess.run([sys.executable, "-m", "harness.scorer", str(tr), "--plot", str(png), "--reps", "50",
                    "--out", str(tmp_path / "s.json")], cwd=ROOT, check=True, capture_output=True)
    assert png.exists() and os.path.getsize(png) > 10000
