import json
import subprocess
import sys

from conftest import DATA, ROOT


def test_oracle_pipeline_on_real_items(tmp_path):
    out = tmp_path / "t.jsonl"
    for f in ("mbppplus.jsonl", "traps.jsonl"):
        subprocess.run([sys.executable, "-m", "harness.run", "--backend", "oracle", "--items", f"{DATA}/{f}",
                        "--n", "3", "--out", str(out)], cwd=ROOT, check=True, capture_output=True)
    recs = [json.loads(l) for l in open(out, encoding="utf-8")]
    assert len(recs) == 30 and all(r["hidden_pass"] for r in recs)
    assert sum(r["is_trap"] for r in recs) == 15
    s = subprocess.run([sys.executable, "-m", "harness.scorer", str(out), "--reps", "20"], cwd=ROOT,
                       check=True, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    assert "oracle|escalating: n=6 acc0=1.00" in s
