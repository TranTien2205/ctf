#!/usr/bin/env bash
# One-time setup: turn this tree into a git repository and push it to a PRIVATE
# GitHub repository. Run it once, from the machine that holds the tree. The root
# is derived from this script's own location, so it works wherever the tree sits.
#
#   bash scripts/repo_init.sh                 # default name: ctf-solver
#   REPO_NAME=my-ctf bash scripts/repo_init.sh
#
# Authentication, in order of preference:
#   1. gh, already logged in            -> gh auth status
#   2. gh, not logged in                -> the script runs gh auth login for you
#   3. no gh, but GITHUB_TOKEN exported -> the repository is created over the API
# The repository is created private. Do not make it public: solved notes and
# challenge artifacts can contain flags and exploit detail.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_NAME="${REPO_NAME:-ctf-solver}"
cd "$ROOT"

say() { printf '\n[%s] %s\n' "$1" "$2"; }

if ! command -v git >/dev/null 2>&1; then
  say ERROR "git is not installed. Install it and run this script again."
  exit 1
fi

say STEP "Running the update gate before the first commit"
if ! bash "$ROOT/test/run_all.sh"; then
  say ERROR "The gate failed. Fix it before creating the repository."
  exit 1
fi

if [ -d "$ROOT/.git" ]; then
  say SKIP "$ROOT is already a git repository"
else
  say STEP "Initialising the repository"
  git init -q
  git symbolic-ref HEAD refs/heads/main
fi

if [ -z "$(git config user.email || true)" ]; then
  say NOTE "git user.email is not set for this repository. Set it with:"
  echo "    git -C $ROOT config user.email you@example.com"
  echo "    git -C $ROOT config user.name  'Your Name'"
fi

say STEP "Staging tracked content (.gitignore keeps caches, runs and state out)"
git add -A
# The Weather App source is the white-box regression fixture: without it a fresh
# clone can only run the rest of the suite. Media inside it stays ignored.
if [ -d "challenges/Weather App" ]; then
  git add -f "challenges/Weather App" 2>/dev/null || true
fi
if git diff --cached --quiet; then
  say SKIP "Nothing new to commit"
else
  git commit -q -m "CTF solver system: dispatcher, chain reuse, hypothesis protocol, update gate"
  say DONE "Created the initial commit"
fi

if git rev-parse -q --verify refs/tags/v0.1.0 >/dev/null; then
  say SKIP "Tag v0.1.0 already exists"
else
  git tag -a v0.1.0 -m "First verified snapshot: update gate passing"
  say DONE "Tagged v0.1.0 as the first known-good state"
fi

if git remote get-url origin >/dev/null 2>&1; then
  say SKIP "A remote named origin already exists: $(git remote get-url origin)"
  say STEP "Pushing"
  git push -u origin HEAD --tags
  say DONE "Pushed. Future updates: bash scripts/save_version.sh \"message\""
  exit 0
fi

if command -v gh >/dev/null 2>&1; then
  if ! gh auth status >/dev/null 2>&1; then
    say STEP "Logging in to GitHub (choose HTTPS and authenticate in the browser)"
    gh auth login
  fi
  say STEP "Creating the PRIVATE repository $REPO_NAME and pushing"
  gh repo create "$REPO_NAME" --private --source "$ROOT" --remote origin --push
  git push -q origin --tags
  say DONE "Pushed. Future updates: bash scripts/save_version.sh \"message\""
  exit 0
fi

if [ -n "${GITHUB_TOKEN:-}" ]; then
  say STEP "gh is not installed; creating the PRIVATE repository over the API"
  owner="$(curl -sS -H "Authorization: Bearer $GITHUB_TOKEN" \
           -H "Accept: application/vnd.github+json" \
           https://api.github.com/user | sed -n 's/.*"login": *"\([^"]*\)".*/\1/p' | head -1)"
  if [ -z "$owner" ]; then
    say ERROR "GITHUB_TOKEN did not authenticate. Check the token and its scopes (repo)."
    exit 1
  fi
  curl -sS -o /dev/null -w 'HTTP %{http_code}\n' \
    -X POST -H "Authorization: Bearer $GITHUB_TOKEN" \
    -H "Accept: application/vnd.github+json" \
    https://api.github.com/user/repos \
    -d "{\"name\":\"$REPO_NAME\",\"private\":true,\"description\":\"Private CTF solver system\"}"
  git remote add origin "https://github.com/$owner/$REPO_NAME.git"
  say STEP "Pushing (git will ask for a password: paste the token)"
  git push -u origin HEAD --tags
  say DONE "Pushed to https://github.com/$owner/$REPO_NAME (private)"
  exit 0
fi

say NOTE "No GitHub client available. The local repository and tag v0.1.0 are ready."
cat <<'EOF'

To add the remote later, pick one:

  # A. GitHub CLI
  sudo apt install gh && gh auth login
  gh repo create ctf-solver --private --source "$PWD" --remote origin --push

  # B. Personal access token with the repo scope
  export GITHUB_TOKEN=ghp_...
  bash scripts/repo_init.sh

Keep the repository PRIVATE: solved notes and challenge artifacts can contain
flags and exploit detail.
EOF
