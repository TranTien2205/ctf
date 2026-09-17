# test/ — the update gate

Every change to this system passes through here before it is committed. The
suite answers one question: **does the system still do what it did before the
change?**

```bash
bash ~/ctf/test/run_all.sh
```

Everything is offline. No network, no live target, no challenge artifact is
executed. Only controlled Python snippets run.

## What each group protects

| Group | Protects against |
|---|---|
| A. structure | a renamed or deleted skill turning a route into a dead link; a skill existing on disk but invisible to the dispatcher; the registry and `ctf.py` drifting apart |
| B. contract | `PROMPT.md` losing one of its seven sections; the no-invention rule disappearing; Vietnamese or corrupted text re-entering the control plane; documentation naming a tool that does not exist |
| C. routing | a change to `ctf.py` silently misclassifying a shape this toolkit has already met |
| D. dispatch | opening two routers, opening a large depth corpus before a signal, or guessing a category instead of reporting that the input is unclassified |
| E. chain reuse | a chain card losing a field, storing a flag, pointing at a deleted note, or no longer matching the evidence that produced it |
| F. ledger | a redirect deleting a hypothesis instead of parking it; revival losing the history |
| G. capability | a change that quietly reduces the number of skills, routers, chain cards or passing routing cases |

## Files

| File | Role |
|---|---|
| `regression.py` | the suite itself, 31 checks in seven groups |
| `cases/routing.json` | observation to expected category; each case comes from a real challenge shape |
| `cases/dispatch.json` | expected router, forbidden skills, and expected chain match, black-box and white-box |
| `baseline.json` | the capability floor the suite refuses to fall below |
| `capability_report.py` | prints the current snapshot; `--write` records a new floor |
| `run_all.sh` | the gate: required checks, optional checks, result |

## Adding a case

When a real challenge routes wrongly, or a new chain card is added, add a case to
`cases/`. Never delete or weaken a case to make a change pass — that is the one
move this directory exists to prevent. If a case is genuinely obsolete, say so in
the commit message and record why.

## Raising the baseline

`test/capability_report.py --write` refuses to lower any metric. Record a new
floor only after `run_all.sh` reports PASS.

## Optional dependencies

`tests/test_foundation.py` needs `jsonschema` and `tornado`. Without them the
gate reports SKIPPED rather than failing, so a missing package is never mistaken
for a broken system. Install them to run the full set:

```bash
pip install --break-system-packages jsonschema tornado
```

## If the gate fails

Do not commit. Either fix the failure or return to the last known-good tag:

```bash
git -C ~/ctf tag --list 'v*' | tail -5
git -C ~/ctf checkout <tag>
```
