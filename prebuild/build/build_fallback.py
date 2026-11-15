"""Fallback option (eval-framing) data: ARC-Challenge test and MMLU-Pro test -> JSONL with one shape:
{task_id, source, question, choices: [str], labels: [str], answer_index: int, answer_label: str, category}.
Items with a missing/invalid answer are dropped (counts printed and in fallback_stats.json).
Framings and paraphrases are NOT built here (sprint work).

usage: python -m build.build_fallback <raw_dir> <out_dir>"""
import json
import os
import sys

import pyarrow.parquet as pq

LETTERS = "ABCDEFGHIJ"


def arc(raw):
    rows = pq.read_table(os.path.join(raw, "ai2_arc", "ARC-Challenge", "test-00000-of-00001.parquet")).to_pylist()
    for r in rows:
        labels, texts = list(r["choices"]["label"]), list(r["choices"]["text"])
        if r["answerKey"] not in labels:
            yield None
            continue
        yield {"task_id": f"arc_challenge/{r['id']}", "source": "arc_challenge", "question": r["question"],
               "choices": texts, "labels": labels, "answer_index": labels.index(r["answerKey"]),
               "answer_label": r["answerKey"], "category": None}


def mmlu_pro(raw):
    rows = pq.read_table(os.path.join(raw, "mmlu_pro", "data", "test-00000-of-00001.parquet")).to_pylist()
    for r in rows:
        opts = list(r["options"])
        idx = r["answer_index"]
        if idx is None or not (0 <= idx < len(opts)) or LETTERS[idx] != r["answer"]:
            yield None
            continue
        yield {"task_id": f"mmlu_pro/{r['question_id']}", "source": "mmlu_pro", "question": r["question"],
               "choices": opts, "labels": list(LETTERS[:len(opts)]), "answer_index": idx,
               "answer_label": r["answer"], "category": r["category"]}


def main(raw, out):
    stats = {}
    for name, gen in (("arc_challenge", arc), ("mmlu_pro", mmlu_pro)):
        items = list(gen(raw))
        kept = [i for i in items if i]
        with open(os.path.join(out, f"{name}.jsonl"), "w", encoding="utf-8") as f:
            for i in kept:
                f.write(json.dumps(i) + "\n")
        stats[name] = {"kept": len(kept), "dropped": len(items) - len(kept)}
    with open(os.path.join(out, "fallback_stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=1)
    print(json.dumps(stats))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
