# CTF Toolkit

An independent toolkit for CTF jeopardy and attack-defense challenges, white-box
and black-box. It does not read or import the red-team machine toolkit under
`~/security-toolkit`.

## Start a session

```bash
# 1. classify
python3 ./ctf.py --json ./challenge-src        # white-box: source scan
python3 ./ctf.py --json "JWT login admin bot"  # black-box: observation route

# 2. dispatch: one router, at most one depth skill
python3 tools/skill_select.py --source ./challenge-src
python3 tools/skill_select.py "JWT login admin bot"

# 3. reuse a chain already solved here
python3 tools/chain_match.py --source ./challenge-src
python3 tools/chain_match.py "Express mongoose /update flag 403"

# 4. open the ledger
python3 tools/state.py <id> --category web --target http://host:port
```

Load `PROMPT.md` at the start of every new session. It is the session contract:
context, role, goal, instructions, constraints, output format, examples.

## Read these in this order

| File | What it settles |
|---|---|
| `PROMPT.md` | the session contract and the output format |
| `CLAUDE.md` | the always-loaded operating rules |
| `skills/INDEX.md` | which skill to open, and when to stop opening |
| `HYPOTHESIS_PROTOCOL.md` | changing direction without losing a branch |
| `EVIDENCE_POLICY.md` | what may be claimed, and what may not |
| `test/README.md` | the gate every change passes before it is accepted |
| `test/cases/system_eval.json` | offline actionability cases for every update |
| `VERSIONING.md` | saving and restoring a working version |
| `EXTERNAL_SOURCES.md` | importing outside material without importing noise |
| `TRAINING.md` | the complete blind/source/guided training and learning protocol |

## Layout

```
ctf.py                 fast router: source scan, observation route, writeup search
skills/                INDEX.md + registry.json + one directory per skill
knowledge/chains/      chains verified here, matchable, flags redacted
knowledge/cards/       reviewed writeup cards and the FTS index
tools/                 dispatcher, chain matcher, ledger, probe and import tools
test/                  the update gate
scripts/               repository setup and version saving
challenges/            challenge inputs and artifacts (git-ignored)
solved/                the full prose notes each chain card was derived from
cache/                 disposable web and search cache
```

## The three rules

1. **One router, one depth skill.** The depth corpus is roughly 622,000 tokens
   across 190 files. Opening it early both burns the context window and anchors
   the next hypothesis. `tools/skill_select.py` enforces the order.
2. **Park, do not delete.** A direction that looks wrong is usually unfinished.
   `--deprioritize` keeps it open at priority 0; `--revive` brings it back when
   new evidence arrives. `HYPOTHESIS_PROTOCOL.md` has the scale.
3. **Nothing is invented.** No endpoint, function, field, credential, payload,
   path, CVE or number that was not observed. Unknown stays unknown. A timeout is
   not a success. A flag is a hypothesis until it is read from a live response or
   a supplied artifact.

## Before accepting any change

```bash
bash test/run_all.sh
bash scripts/save_version.sh "what changed"
```

The gate has two layers. The legacy regression suite protects behavior that
already worked. The required offline system evaluation checks whether the
classifier, dispatch policy, skill contracts, and decision controller still
produce useful actions. Both layers must pass; a structural pass alone is not a
claim that the system solves a challenge.

The controller is fail-closed: a hypothesis must name a taxonomy class, every
probe must identify that hypothesis and class, and a recorded response clears
the previous next action. This keeps a weak model from repeating stale commands
or upgrading a merely successful HTTP response into proof of the wrong class.

Review local learning separately:

```bash
python3 tools/learning_report.py
python3 tools/classify_solve.py --review
```

`proposed` notes are unreviewed observations. `confirmed` notes are the only
local experience an operator should treat as reusable evidence. Catalogue skills
remain catalogue until a verified chain and human review promote them.

The gate checks that the registry, the index and `ctf.py` still agree; that
`PROMPT.md` keeps its seven sections and the no-invention rule; that the control
plane stays English; that documentation never names a tool that does not exist;
that routing and dispatch still produce the expected answers for shapes this
toolkit has already met; that every chain card still matches the evidence that
produced it and carries no flag; that a parked hypothesis survives a redirect;
and that no count regressed below `test/baseline.json`.

## Honest limits

- Routing is heuristic. Keyword scores are not proof of exploitability, and a
  generic term can still outrank a specific one.
- A chain match is a candidate, never proof. Preconditions are plain language and
  no tool checks them for you.
- Source scanning finds candidate sinks; it cannot prove a sink is reachable.
- `tools/run.py` logs commands with timeouts. It is not a sandbox: a command can
  reach the filesystem and the network.
- There is no autonomous solver and no automatic flag submission. The operator
  runs the probes and verifies the flag.
- `tests/test_foundation.py` needs `jsonschema` and `tornado`; without them the
  gate reports SKIPPED rather than failing, so a missing package is never
  mistaken for a broken system.
- Writeup search depends on network access and on search-engine quality.

Authorized CTF and lab use only. If an event forbids AI assistance, this system
is for practice beforehand, not for use during the event.
