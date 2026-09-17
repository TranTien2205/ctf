# Versioning and Private Backup

Every version that is saved is a version that passed the gate. That is what makes
a bad update recoverable: `git checkout <tag>` returns to a state that worked.

## First time

```bash
bash ~/ctf/scripts/repo_init.sh
```

It runs `test/run_all.sh`, initialises the repository, commits, tags `v0.1.0`,
and creates a **private** GitHub repository. Authentication, in order:

1. `gh` already logged in — used directly
2. `gh` installed but not logged in — the script runs `gh auth login`
3. no `gh`, but `GITHUB_TOKEN` exported with the `repo` scope — the repository is
   created over the API

With none of those, the local repository and the tag are still created and the
script prints the two commands that add the remote later. Choose the repository
name with `REPO_NAME=my-ctf bash ~/ctf/scripts/repo_init.sh`.

## Every update after that

```bash
bash ~/ctf/scripts/save_version.sh "what changed"
```

Gate, then commit, then tag `vYYYY.MM.DD.N`, then push. If the gate fails,
nothing is committed and the script prints the last known-good tags.

```bash
SKIP_PUSH=1 bash ~/ctf/scripts/save_version.sh "local only"
```

## Rolling back

```bash
git -C ~/ctf tag --list 'v*'          # every saved version
git -C ~/ctf checkout v2026.09.11.1   # return to one
git -C ~/ctf checkout main            # come back
```

To find which update broke something, `git bisect` across the tags and run
`bash test/run_all.sh` at each step.

## Keep it private

Solved notes, chain provenance and challenge artifacts can contain flags and
exploit detail. The repository is created private and must stay private.

`.gitignore` keeps out: caches, per-run directories, per-challenge state,
vendored binaries such as `tools/ghidra-dist/`, media, and anything matching a
secret pattern. `challenges/` is ignored as a whole; `scripts/repo_init.sh`
force-adds only the Weather App source, which the white-box regression needs.
Track another challenge deliberately:

```bash
git -C ~/ctf add -f "challenges/<name>"
```

Never commit live target tokens, event credentials or private flags, not even to
a private repository.

## What a good commit message says

What changed, why, and which gate group covers it. If a test case was added, say
which real challenge shape it came from. If a case was removed, say why it is
obsolete — that is the one change the gate cannot catch on its own.
