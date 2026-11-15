"""Plumbing stats from smoke transcripts: per-backend turn latency, tokens, CONFIDENCE parse failures,
backend errors, and a projection of the planned batch. Never accuracy or flip numbers (n=5 is plumbing).

  python -m harness.smoke_stats out/smoke/*.jsonl [--items 300] [--parallel 4] [--json out/smoke/stats.json]"""
import argparse
import json
import statistics
from collections import defaultdict

TOK = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")


def stats(paths):
    by = defaultdict(list)
    for p in paths:
        for line in open(p, encoding="utf-8"):
            r = json.loads(line)
            by[r["model"]].append(r)
    out = {}
    for model, recs in sorted(by.items()):
        secs = [r["seconds"] for r in recs if r.get("seconds")]
        asked = [r for r in recs if r["kind"] != "solve"]
        u = [r.get("usage") or {} for r in recs]
        tok = {k: sum(x.get(k, 0) or 0 for x in u) / max(len(recs), 1) for k in TOK}
        items = {r["task_id"] for r in recs}
        cost = [r["cost_usd"] for r in recs if r.get("cost_usd") is not None]
        out[model] = {
            "items": len(items), "traps": len({r["task_id"] for r in recs if r["is_trap"]}), "turns": len(recs),
            "turn_s_mean": statistics.mean(secs) if secs else None,
            "turn_s_median": statistics.median(secs) if secs else None,
            "turn_s_max": max(secs) if secs else None,
            "item_s_mean": sum(secs) / len(items) if secs else None,
            "tokens_per_turn": tok,
            "api_usd_equiv_per_turn": (sum(cost) / len(cost)) if cost else None,
            "confidence_parse_fail": sum(r["confidence"] is None for r in asked), "confidence_asked": len(asked),
            "backend_errors": sum(bool(r.get("backend_error")) for r in recs),
            "exec_errors": sorted({r["exec_error"] for r in recs if r.get("exec_error")})[:5],
        }
    return out


def project(s, n_items, turns=5, parallel=1):
    if not s.get("item_s_mean"):
        return None
    t = s["tokens_per_turn"]
    return {"items": n_items, "turns": n_items * turns, "parallel": parallel,
            "wall_h": s["item_s_mean"] * n_items / parallel / 3600,
            "tokens_M": {k: v * n_items * turns / 1e6 for k, v in t.items()},
            "api_usd_equiv": (s["api_usd_equiv_per_turn"] or 0) * n_items * turns}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--items", type=int, default=300)
    ap.add_argument("--parallel", type=int, default=1)
    ap.add_argument("--json")
    a = ap.parse_args()
    s = stats(a.paths)
    res = {m: {"smoke": v, "projection": project(v, a.items, parallel=a.parallel)} for m, v in s.items()}
    print(json.dumps(res, indent=1))
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1)


if __name__ == "__main__":
    main()
