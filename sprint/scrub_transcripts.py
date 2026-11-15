"""Published copies of the transcripts: replace local paths in text fields (sandbox temp dirs -> <sandbox>, any
other private absolute path -> <local path>). Metrics fields are untouched; recount.py on the copies must match.

  python sprint/scrub_transcripts.py <in.jsonl> <out.jsonl>"""
import json
import re
import sys

SBX = re.compile(r"/tmp/epi_sbx(/task_[A-Za-z0-9_]+)?")
TMPC = re.compile(r"/tmp/claude-\d+[^\s\"'`)]*")
PRIV = re.compile(r"(?<![\w.])/(?:" + "|".join(["s" + "rv", "m" + "nt", "ho" + "me", "ro" + "ot"]) + r")/[^\s\"'`)]*")


def clean(x):
    if isinstance(x, str):
        return PRIV.sub("<local path>", TMPC.sub("<tmp>", SBX.sub("<sandbox>", x)))
    if isinstance(x, list):
        return [clean(v) for v in x]
    if isinstance(x, dict):
        return {k: clean(v) for k, v in x.items()}
    return x


n = 0
with open(sys.argv[2], "w") as f:
    for line in open(sys.argv[1]):
        r = json.loads(line)
        c = clean(r)
        n += c != r
        f.write(json.dumps(c) + "\n")
print(sys.argv[1], "records changed:", n)
