# Versioning and Private Backup

`~/ctf` was not a Git repository when this system was audited. Initialize it
locally, commit only reviewed CTF tooling and redacted knowledge, and keep
live credentials, callback logs, caches, and target-specific secrets ignored.

## Local setup

```bash
cd ~/ctf
git init
git add .gitignore PROMPT.md SKILL_GUIDE.md EVIDENCE_POLICY.md SYSTEM_AUDIT.md VERSIONING.md agent ctf.py knowledge skills solved test tests tools
git commit -m "Add CTF solver workflow and regression suite"
```

## GitHub setup

The current machine has no `gh` binary or GitHub token. After authenticating
with a GitHub account that owns the destination, use:

```bash
gh auth login
gh repo create ctf-solver --private --source ~/ctf --remote origin --push
```

For future updates:

```bash
python3 ~/ctf/test/regression.py && python3 -m unittest discover -s ~/ctf/tests -v && python3 ~/ctf/selfcheck.py
git add -A && git commit -m "Describe the update" && git tag -a "vYYYY.MM.DD.N" -m "Verified update" && git push origin HEAD --tags
```

The repository should remain private because solved cards and local challenge
artifacts can contain flags or exploit details. Keep a known-good tag before
each update so a regression can be bisected or restored.
