# Using this tree from Claude Code

The tree was built for an agent that reads `AGENTS.md` and a plain `skills/`
directory. Claude Code looks in neither place: it reads `CLAUDE.md`, and it
discovers skills only under `.claude/skills/`. Three small pieces of wiring make
one tree serve both, with no second copy of anything.

## What is wired

| Piece | What it is | Why |
|---|---|---|
| `.claude/skills` | a relative symlink to `../skills` | Claude Code discovers skills only under `.claude/skills/<name>/SKILL.md`; the symlink puts all 46 there without duplicating a file |
| `@AGENTS.md` at the top of `CLAUDE.md` | an import line | Claude Code reads `CLAUDE.md` and never `AGENTS.md`; the import pulls the bootstrap contract in |
| `.claude/commands/*.md` | five slash commands | the workflows that are easy to skip: starting a challenge, classifying, deciding the next step, closing the learning loop, running the gate |

The symlink is **relative**, so it keeps working wherever the tree is checked
out and it survives being moved, renamed, or packed into an archive. It points
inside the same tree, so Claude Code does not treat it as an external import.

## Start a session

```bash
cd <this tree>
claude
```

`CLAUDE.md` loads automatically and pulls in `AGENTS.md` with it. Then:

```
/ctf-start <challenge-name> <target-url-or-source-path>
```

## The five commands

| Command | Does |
|---|---|
| `/ctf-start` | selfcheck, open the ledger, classify, match chains, pick one skill |
| `/ctf-classify` | run the three routers on an observation or a source directory |
| `/ctf-next` | ask `tools/decide.py` for the next step, and record verdicts through the hooks |
| `/ctf-solved` | the six-step learning loop after a verified flag |
| `/ctf-gate` | run `test/run_all.sh` before accepting any change |

## Verify the wiring

Inside a Claude Code session:

```
/skill-doctor      # lists discovered skills and reports frontmatter errors
/context           # shows which memory files loaded
```

From a shell, without starting a session:

```bash
ls .claude/skills/*/SKILL.md | wc -l    # expect 46
readlink .claude/skills                  # expect ../skills
grep -c '@AGENTS.md' CLAUDE.md           # expect 1
python3 test/regression.py               # includes the wiring checks
```

`test/regression.py` fails if the symlink is missing or broken, if a skill on
disk is not reachable through `.claude/skills/`, if the import line is gone, or
if a command file names a tool that does not exist.

## Things that differ from opencode

- **Skill loading is not automatic in the way the load-order rule assumes.**
  Claude Code makes every skill's `description` visible and decides from it,
  which is close to what `tools/skill_select.py` does but not identical. The
  discipline still holds: run `skill_select.py`, open the one skill it names, and
  do not let a broad description pull in a second one.
- **`allowed-tools` in a skill's frontmatter is honoured by Claude Code** as a
  pre-approval list. The skills here carry it from the original port; check it
  before widening anything.
- **Commands are the older mechanism**; Claude Code now prefers skills. The five
  here are deliberately thin — they run tools and state the rules, they do not
  carry knowledge. Knowledge lives in the skills.

## If a skill does not appear

1. `readlink .claude/skills` — if it prints nothing, the symlink was lost. This
   happens when the tree is copied with a tool that dereferences or drops
   symlinks. Recreate it:
   ```bash
   ln -sfn ../skills .claude/skills
   ```
2. `/skill-doctor` reports frontmatter parse errors; every skill here needs at
   least `name` and `description`.
3. Unknown frontmatter keys are ignored, not rejected, so `budget`,
   `environment` and `tags` are harmless.
