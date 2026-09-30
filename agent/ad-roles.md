# The attack-defense subagents

Five narrow subagents for an **authorized** attack–defense event. Each is started
by name, does one job, and owns nothing: not the priorities, not the clock, not
availability, and not the submission. The incident commander reads this file to
pick one in ten seconds; nothing here decides anything on its own.

They are defined in `.claude/agents/ad-*.md`. Claude Code discovers that directory;
**other runners do not**, and they read `AGENTS.md` and from there this file — which
is why the job of each agent is written out here rather than only in its own file.
A runner without subagent support can still use them: the body of each file is a
prompt, and pasting it with the named input attached does the same work.

`python3 tools/ad/agent_lint.py` checks that every one still carries a restricted
tool list, a declared write capability and the prohibition block. Exit 0 means the
five files still say what they must.

## The agents

| Agent | Job | Writes? | Input | Stop condition |
|---|---|---|---|---|
| `ad-service-read` | the flag store, every route that reaches it, the auth boundary, three falsifiable hypotheses, one patch per mechanism | no | the service source | patches written, or two of three hypotheses have no falsifier |
| `ad-traffic-watch` | the three most likely stolen exploits out of your own capture, replay command copied verbatim | no | the saved `traffic_mine` JSON plus both capture directories | one mined file read, one report |
| `ad-patch-bracket` | the bracket around a patch: before/after commands, the rollback written first, LIVE or NOT LIVE | no | the health spec plus the newest saved run | one patch for one service, with its bracket |
| `ad-sla-triage` | which of three causes turned a check red, with the excerpt that decides it | no | the bracket's `before`/`after` runs and the t0 run | one cause named, or the no-t0 sentence written |
| `ad-host-survey` | what looks planted in the identical starting image, ranked, each with its line and its confidence | no | a read-only host dump plus its manifest | every collector read, every finding carrying its line |

## Why none of them can write

All five carry exactly `tools: Read, Grep, Glob`. That is the enforcement, and the
prose is only the explanation: an agent with no `Bash` cannot send a request,
cannot restart a service and cannot run a patch, whatever its prompt says. An agent
with no `Edit` cannot change a file in the estate or in this repository.

`ad-patch-bracket` is the one that looks like it should be different, and it is
worth stating why it is not. It was designed with `Edit` plus a scoped
`Bash(python3 tools/ad/sla_check.py:*)` so the write would always be bracketed. Two
things argued it back to read-only:

- `test/regression.py::test_no_subagent_can_write_to_this_repository` is a
  **required gate** and it refuses any file in `.claude/agents/` that declares
  `Write`, `Edit` or `NotebookEdit`. Weakening that test to excuse a filename
  prefix would re-create exactly the blind spot it exists to close.
- the same argument that keeps a restart away from an agent keeps an edit away
  from one. Availability is scored continuously and cannot be won back; two
  minutes of a human applying a one-line patch is cheaper than any run where an
  agent applied the wrong one.

So the agent writes the patch, the bracket and the rollback in full, and the
operator applies it. Whether a scoped `Bash(...)` entry is **enforced** or merely
enables the tool was never proved here, which is a second reason not to build the
safety argument on one.

## The run directory

Every prompt refers to this layout. It **does not exist in a fresh checkout** —
preflight creates it. `.gitignore` line 22 is `**/runs/`, so everything under
`runs/` is uncommittable by default, which is the point: a farm's `.seen` file
holds real flags, and `*.seen` is ignored nowhere else in this tree. A farm config
kept outside `runs/` puts flags into git.

| Path | Holds |
|---|---|
| `runs/<service>/ledger.json` | the tick ledger `tools/ad/tick.py` reads and records into |
| `runs/<service>/sla-spec.json` | the health spec for this service |
| `runs/<service>/sla/` | every saved `sla_check` run, including `t0-before-rotation.json` |
| `runs/<service>/baseline/` | the checker-only capture, split into one request per file |
| `runs/<service>/live/` | the live capture, split the same way |
| `runs/<service>/mined/` | `traffic_mine` output, one file per run |
| `runs/<service>/farm.json` | the `flag_farm` config: team list, flag regex, submit dialect |
| `runs/<service>/farm.seen` | flags the scoreboard really accepted. Never leaves the box |
| `runs/<service>/farm.pending` | flags held because the scoreboard did not accept them yet |
| `runs/<host>/survey/` | a host dump plus its manifest, for `ad-host-survey` |
| `runs/reports/<agent>-<n>.md` | one agent report per file, so nothing is overwritten |

## What they are not for

- Deciding what to do next. That is `python3 tools/ad/tick.py <ledger>`, and it is
  deterministic on purpose.
- Submitting a flag. Only `tools/ad/flag_farm.py` does that.
- The first thirty minutes. That is `tools/ad/RUNBOOK.md`, read by a human.
- Anything on a host that is not listed individually in the team list.

The prohibitions every one of them carries are in `agent/ad-prohibitions.md`, and
they are copied into each file verbatim rather than referenced, because a rule an
agent has to go and fetch is a rule it can reason its way past.
