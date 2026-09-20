#!/usr/bin/env bash
# Save a working version of the system: run the gate, commit, tag, push.
# Nothing is committed unless the gate passes, so every tag is a state that
# worked. That is what makes a bad update recoverable.
#
#   bash scripts/save_version.sh "what changed"
#   SKIP_PUSH=1 bash scripts/save_version.sh "local only"
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
MESSAGE="${1:-}"

say() { printf '\n[%s] %s\n' "$1" "$2"; }

if [ -z "$MESSAGE" ]; then
  say ERROR "Describe the change: bash scripts/save_version.sh \"what changed\""
  exit 2
fi
if [ ! -d "$ROOT/.git" ]; then
  say ERROR "Not a git repository yet. Run scripts/repo_init.sh first."
  exit 2
fi

say STEP "Update gate"
if ! bash "$ROOT/test/run_all.sh"; then
  say ABORT "The gate failed. Nothing was committed."
  echo "Either fix the failure, or return to the last known-good tag:"
  git tag --list 'v*' | tail -5 | sed 's/^/    git checkout /'
  exit 1
fi

say STEP "Changes to be saved"
git add -A
if git diff --cached --quiet; then
  say SKIP "Nothing changed since the last commit"
  exit 0
fi
git --no-pager diff --cached --stat

DATE="$(date +%Y.%m.%d)"
N=1
while git rev-parse -q --verify "refs/tags/v$DATE.$N" >/dev/null; do
  N=$((N + 1))
done
TAG="v$DATE.$N"

git commit -q -m "$MESSAGE"
git tag -a "$TAG" -m "Gate passing: $MESSAGE"
say DONE "Committed and tagged $TAG"

if [ -n "${SKIP_PUSH:-}" ]; then
  say SKIP "SKIP_PUSH is set; not pushing"
  exit 0
fi
if git remote get-url origin >/dev/null 2>&1; then
  say STEP "Pushing to origin"
  git push -q origin HEAD --tags
  say DONE "Pushed $TAG"
else
  say NOTE "No remote configured. Run scripts/repo_init.sh to add one."
fi

cat <<EOF

Restore this version later with:
    git -C $ROOT checkout $TAG
List every saved version with:
    git -C $ROOT tag --list 'v*'
EOF
