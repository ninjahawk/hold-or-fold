#!/usr/bin/env bash
# Fresh single-commit public export: copy the tree, scan it, init a new repo with one commit, scan again
# (term/regex scan + gitleaks on tree and history). Refuses to finish if any scan finds something.
# usage: AUTHOR_NAME="..." AUTHOR_EMAIL="..." scrub/export.sh <src_dir> <dest_dir> [extra_terms_file]
set -euo pipefail
SRC=$(cd "$1" && pwd); DEST=$2; EXTRA=${3:-}
HERE=$(cd "$(dirname "$0")" && pwd)
: "${AUTHOR_NAME:?set AUTHOR_NAME}"; : "${AUTHOR_EMAIL:?set AUTHOR_EMAIL (public address)}"
[ -e "$DEST" ] && { echo "dest exists: $DEST"; exit 2; }
mkdir -p "$DEST"
rsync -a --exclude .git --exclude .venv --exclude __pycache__ --exclude .pytest_cache --exclude '*.local.*' "$SRC"/ "$DEST"/
ARGS=("$DEST"); [ -n "$EXTRA" ] && ARGS+=(--extra "$EXTRA")
python3 "$HERE/scan.py" "${ARGS[@]}"
cd "$DEST"
git init -q
git add -A
GIT_AUTHOR_DATE="$(date -u +%Y-%m-%dT00:00:00Z)" GIT_COMMITTER_DATE="$(date -u +%Y-%m-%dT00:00:00Z)" \
  git -c user.name="$AUTHOR_NAME" -c user.email="$AUTHOR_EMAIL" commit -q -m "Initial public release"
ARGS=("$DEST" --git-repo "$DEST" --allow-email "$AUTHOR_EMAIL"); [ -n "$EXTRA" ] && ARGS+=(--extra "$EXTRA")
python3 "$HERE/scan.py" "${ARGS[@]}"
if command -v gitleaks >/dev/null; then
  gitleaks detect --source "$DEST" --no-banner --redact
  gitleaks detect --source "$DEST" --no-git --no-banner --redact
else
  echo "WARNING: gitleaks not on PATH; secret scan skipped" >&2
fi
echo "export clean: $DEST ($(git rev-parse --short HEAD))"
