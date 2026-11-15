"""Scan a tree (and optionally a git history) for identifying strings before publishing.

Checks:
  1. Regexes: email addresses, Windows user paths, Unix home/server/mount paths.
  2. Private term list stored as SHA-256 hashes of lowercased words (`terms.sha256`), so the list itself can
     be published. Every word token in the scanned text is hashed and looked up. Add terms with make_terms.py.
  3. Optional plaintext extra terms file (--extra), never committed.
Exit code 1 if anything is found.

usage: python scan.py <dir> [--git-repo REPO --git-path PATH] [--extra FILE]"""
import argparse
import hashlib
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Patterns are assembled from pieces so this file does not match itself.
SEP = "\\\\"
PATTERNS = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "windows_user_path": re.compile(r"[A-Za-z]:(?:" + SEP + r"|/)+Users(?:" + SEP + r"|/)", re.I),
    "unix_private_path": re.compile(r"(?<![\w.])/(?:" + "|".join(["s" + "rv", "m" + "nt", "ho" + "me", "Us" + "ers", "ro" + "ot"]) + r")/"),
}
ALLOW_EMAIL = {"noreply@" + "example.com"}
SKIP_DIRS = {".git", "__pycache__", ".venv", ".pytest_cache"}
TOKEN = re.compile(r"[A-Za-z0-9_\-]+")


def load_hashes(path):
    if not os.path.exists(path):
        return set()
    return {l.split()[0] for l in open(path, encoding="utf-8") if l.strip() and not l.startswith("#")}


def h(word):
    return hashlib.sha256(word.lower().encode()).hexdigest()


def scan_text(text, where, hashes, extra):
    hits = []
    for name, rx in PATTERNS.items():
        for m in rx.finditer(text):
            if name == "email" and m.group(0).lower() in ALLOW_EMAIL:
                continue
            hits.append((where, name, m.group(0)[:80]))
    seen = set()
    for tok in TOKEN.findall(text):
        for w in {tok, *re.split(r"[_\-]", tok)}:
            if not w or w.lower() in seen:
                continue
            seen.add(w.lower())
            if h(w) in hashes:
                hits.append((where, "private_term", w[:2] + "***"))
    for t in extra:
        if t.lower() in text.lower():
            hits.append((where, "extra_term", t[:2] + "***"))
    return hits


def scan_tree(root, hashes, extra):
    hits = []
    for dp, dns, fns in os.walk(root):
        dns[:] = [d for d in dns if d not in SKIP_DIRS]
        for fn in fns:
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, root)
            hits += scan_text(rel, f"path:{rel}", hashes, extra)
            try:
                with open(p, "rb") as f:
                    raw = f.read()
            except OSError:
                continue
            if b"\0" in raw[:4096]:
                continue  # binary (png): skipped, listed by --list-binary
            hits += scan_text(raw.decode("utf-8", "replace"), rel, hashes, extra)
    return hits


def scan_git(repo, path, hashes, extra):
    """Scan every commit message, author line and diff in history. Diff hunks are attributed to their file
    path (so allow.txt applies per file); headers and messages to 'git:meta'."""
    cmd = ["git", "-C", repo, "log", "-p", "--all", "--format=commit %H%nauthor %an <%ae>%n%B"]
    if path:
        cmd += ["--", path]
    out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    chunks, cur, buf = [], "git:meta", []
    for line in out.splitlines():
        if line.startswith("diff --git "):
            chunks.append((cur, buf))
            cur, buf = line.split(" b/", 1)[-1], [line]
        elif line.startswith("commit ") and len(line) == 47:
            chunks.append((cur, buf))
            cur, buf = "git:meta", [line]
        else:
            buf.append(line)
    chunks.append((cur, buf))
    hits = []
    for where, lines in chunks:
        if path and where != "git:meta" and where.startswith(path.rstrip("/") + "/"):
            where = where[len(path.rstrip("/")) + 1:]
        hits += scan_text("\n".join(lines), where, hashes, extra)
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--git-repo")
    ap.add_argument("--git-path")
    ap.add_argument("--extra")
    ap.add_argument("--allow-email", action="append", default=[])
    ap.add_argument("--allow", default=os.path.join(HERE, "allow.txt"),
                    help="lines: <relative path>\t<finding kind>  (verified false positives, e.g. public dataset text)")
    ap.add_argument("--terms", default=os.path.join(HERE, "terms.sha256"))
    a = ap.parse_args()
    hashes = load_hashes(a.terms)
    ALLOW_EMAIL.update(e.lower() for e in a.allow_email)
    extra = [l.strip() for l in open(a.extra, encoding="utf-8")] if a.extra else []
    extra = [e for e in extra if e and not e.startswith("#")]
    hits = scan_tree(a.dir, hashes, extra)
    if a.git_repo:
        hits += scan_git(a.git_repo, a.git_path, hashes, extra)
    allow = set()
    if os.path.exists(a.allow):
        for l in open(a.allow, encoding="utf-8"):
            if l.strip() and not l.startswith("#"):
                path, kind = l.rstrip("\n").split("\t")[:2]
                allow.add((path, kind))
    allowed = [x for x in hits if (x[0], x[1]) in allow]
    hits = [x for x in hits if (x[0], x[1]) not in allow]
    if allowed:
        print(f"allowed (listed in {os.path.basename(a.allow)}): {len(allowed)}", file=sys.stderr)
    for w, kind, s in hits:
        print(f"{kind}\t{w}\t{s}")
    print(f"scan: {len(hits)} finding(s); {len(hashes)} hashed terms, {len(extra)} extra terms", file=sys.stderr)
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
