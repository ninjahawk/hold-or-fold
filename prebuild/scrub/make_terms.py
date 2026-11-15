"""Append SHA-256 hashes of private terms (one word per line on stdin) to terms.sha256.
usage: printf 'word1\nword2\n' | python make_terms.py"""
import hashlib
import os
import sys

p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "terms.sha256")
have = set(l.split()[0] for l in open(p, encoding="utf-8")) if os.path.exists(p) else set()
with open(p, "a", encoding="utf-8") as f:
    for w in sys.stdin.read().split():
        d = hashlib.sha256(w.lower().encode()).hexdigest()
        if d not in have:
            f.write(d + "\n")
            have.add(d)
print(f"{len(have)} terms")
