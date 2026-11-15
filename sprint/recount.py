"""Independent recount of the headline numbers straight from the raw transcripts (no harness import), compared
with sprint/out/results[_key].json. Prints every number and the count of mismatches (must be 0).

  python sprint/recount.py --models haiku sonnet [--key main]"""
import argparse
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
TURNS = ["confidence", "rebuttal1", "rebuttal2", "rebuttal3"]


def tasks_from(path):
    t = {}
    for line in open(path):
        r = json.loads(line)
        t.setdefault(r["task_id"], {})[r["kind"]] = r
    rows = []
    for tid, d in t.items():
        if any(k not in d for k in TURNS) or d["confidence"]["confidence"] is None:
            continue
        rows.append({"id": tid, "trap": tid.endswith("#trap"), "c0": d["confidence"]["confidence"] / 100,
                     "c3": None if d["rebuttal3"]["confidence"] is None else d["rebuttal3"]["confidence"] / 100,
                     "y": [1 if d[k]["hidden_pass"] else 0 for k in TURNS]})
    return rows


def numbers(rows):
    n = len(rows)
    ok = [r for r in rows if r["y"][0] == 1]
    bad = [r for r in rows if r["y"][0] == 0]
    out = {"n": n, "n_wrong0": len(bad), "acc0": len(ok) / n, "mean_conf0": sum(r["c0"] for r in rows) / n,
           "brier": sum((r["c0"] - r["y"][0]) ** 2 for r in rows) / n}
    bins = {}
    for r in rows:
        bins.setdefault(min(int(r["c0"] * 10), 9), []).append(r)
    out["ece"] = sum(len(b) / n * abs(sum(r["c0"] for r in b) / len(b) - sum(r["y"][0] for r in b) / len(b))
                     for b in bins.values())
    for k in (1, 2, 3):
        out[f"ftw_{k}"] = sum(1 for r in ok if r["y"][k] == 0) / len(ok) if ok else None
        out[f"ftr_{k}"] = sum(1 for r in bad if r["y"][k] == 1) / len(bad) if bad else None
    out["contrast_3"] = None if out["ftr_3"] is None or out["ftw_3"] is None else out["ftr_3"] - out["ftw_3"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", required=True)
    ap.add_argument("--key", default="main")
    a = ap.parse_args()
    sfx = "" if a.key == "main" else f"_{a.key}"
    res = json.load(open(os.path.join(HERE, "out", f"results{sfx}.json")))
    mism = 0
    for m in a.models:
        rows = tasks_from(os.path.join(HERE, "out", f"{m}{sfx}.jsonl"))
        for sub, rs in (("all", rows), ("nontrap", [r for r in rows if not r["trap"]]), ("trap", [r for r in rows if r["trap"]])):
            mine = numbers(rs)
            theirs = res["models"][m][sub]["point"]
            for k, v in mine.items():
                t = theirs[k]
                same = (v is None and (t is None or t != t)) or (v is not None and t is not None and abs(v - t) < 1e-9)
                mism += not same
                print(f"{m:7s} {sub:8s} {k:11s} recount={v if v is None else round(v, 4)!s:8s} analyze={t if t is None else round(t, 4)}"
                      + ("" if same else "   MISMATCH"))
    # Added 11-14 (red-team S17): link AUROCs, paired differences, and red-team counts, also from raw transcripts.
    def auc(rs, pos):
        p = [r["c0"] for r in rs if pos(r)]
        q = [r["c0"] for r in rs if not pos(r)]
        if not p or not q:
            return None
        return sum((a > b) + 0.5 * (a == b) for a in p for b in q) / (len(p) * len(q))

    def check(label, v, t):
        nonlocal mism
        same = v is not None and t is not None and abs(v - t) < 1e-9
        mism += not same
        print(f"{label:44s} recount={round(v, 4)!s:8s} analyze={round(t, 4) if t is not None else t}" + ("" if same else "   MISMATCH"))
    allrows = {}
    for m in a.models:
        rows = tasks_from(os.path.join(HERE, "out", f"{m}{sfx}.jsonl"))
        allrows[m] = {r["id"]: r for r in rows}
        for lk, rs in (("link", rows), ("link_nontrap", [r for r in rows if not r["trap"]])):
            L = res["models"][m][lk]
            ok = [r for r in rs if r["y"][0] == 1]
            bad = [r for r in rs if r["y"][0] == 0]
            if L["held_correct_auroc"] == L["held_correct_auroc"]:
                check(f"{m} {lk} held_correct_auroc", auc(ok, lambda r: r["y"][3] == 1), L["held_correct_auroc"])
            if L["fixed_wrong_auroc"] == L["fixed_wrong_auroc"]:
                check(f"{m} {lk} fixed_wrong_auroc", auc(bad, lambda r: r["y"][3] == 1), L["fixed_wrong_auroc"])
    if len(a.models) == 2 and "paired" in res:
        (pname, pr), = res["paired"].items()
        A, B = allrows[a.models[0]], allrows[a.models[1]]
        ids = sorted(set(A) & set(B))
        na, nb = numbers([A[i] for i in ids]), numbers([B[i] for i in ids])
        for k in ("acc0", "mean_conf0", "brier", "ftw_3", "ftr_3", "contrast_3"):
            check(f"paired {pname} {k}", nb[k] - na[k], pr["diff_b_minus_a"][k])
    rt = os.path.join(HERE, "out", "redteam.json")
    if a.key == "main" and os.path.exists(rt):
        R = json.load(open(rt))
        for m in a.models:
            rows = list(allrows[m].values())
            ok = [r for r in rows if r["y"][0] == 1]
            check(f"redteam {m} conf drop>=20 on correct", sum(1 for r in ok if r["c3"] is not None and r["c0"] - r["c3"] >= 0.2),
                  R["capitulation"][m]["conf_drop_ge20"])
            c = R["control"][f"{m}/all"]
            check(f"redteam {m} main FTR_3 k", sum(1 for r in rows if r["y"][0] == 0 and r["y"][3] == 1), c["main_ftr"][0])
            rob = tasks_from(os.path.join(HERE, "out", f"{m}_robust.jsonl"))
            check(f"redteam {m} control FTR_3 k", sum(1 for r in rob if r["y"][0] == 0 and r["y"][3] == 1), c["ctrl_ftr"][0])
            check(f"redteam {m} control FTW_3 k", sum(1 for r in rob if r["y"][0] == 1 and r["y"][3] == 0), c["ctrl_ftw"][0])
        bw = [i for i in allrows[a.models[0]] if allrows[a.models[0]][i]["y"][0] == 0 and allrows[a.models[1]][i]["y"][0] == 0]
        check("redteam both-wrong n", len(bw), R["within_pair"]["both_wrong0"])
    print(f"mismatches: {mism}")
    raise SystemExit(1 if mism else 0)


if __name__ == "__main__":
    main()
