# RUNBOOK — the first thirty minutes of a jeopardy contest

The sibling of `tools/ad/RUNBOOK.md`, for the other kind of event. Read this on
the day; `tools/contest/selftest.py` proves the logic offline the night before.

The thing this runbook exists to stop: opening one challenge, sinking two hours
into it, and finishing the contest having banked three flags out of twenty when
eight were cheap. Everything below is about allocation, not exploitation.

---

## The measurement every decision here follows from

One subagent costs **7 to 10 minutes spawn-to-report**, and that is a floor, not
a budget — `ORCHESTRATION.md` measured 9.7, 10.2, 7.3 and 10.2 minutes, and it
is the same whatever the task. An easy challenge's whole time-box is 15 to 30
minutes.

Three consequences, and they are not intuitive:

1. **Ten agents on an easy challenge is slower than solving it yourself.** The
   wave spends the entire time-box on spawn latency. Fan out when the surface is
   wide, not when the challenge is cheap.
2. **Parallelism across challenges is free; inside one challenge it is
   governed.** Each challenge has its own `challenges/<name>/state.json` and
   they share no budget, so running three at once trips nothing. The 25-probe
   and 45-minute ceilings bite inside one ledger.
3. **A strong chain card beats every sweep.** It costs no request, it is
   computed offline from the handout, and it hands back a probe already proven
   in this tree. Run `tools/chain_match.py` before you spawn anything.

---

## Minute 0 to 5 — build the board

```bash
cd ~/ctf-v2
python3 selfcheck.py                      # one second, offline; fix any FAIL first
```

Get the roster in. The manual adapter is deliberate: a board you can paste works
at a contest whose API you have not reverse engineered.

```bash
# from a JSON file you pasted or exported
python3 tools/contest/board.py <event> --ingest-json roster.json \
        --ends-at 2026-10-06T18:00:00Z

# or from a CSV with columns id,name,category,points,solves
python3 tools/contest/board.py <event> --ingest-csv roster.csv
```

`--ends-at` is typed in, never computed. Nothing here calls a clock function:
the workflow sandbox has none, and `bfs find` on this box rejects relative
timestamps.

Re-ingesting mid-contest is safe. A row already on the board keeps its status,
flag and timings and takes only fresh points and solve counts, so refreshing the
scoreboard cannot wipe the fact that you already solved something.

## Minute 5 to 10 — rank it

```bash
python3 tools/contest/triage.py <event> --minutes-left 480
```

Read three things in the output:

- `attack_now` — the ids to start, ordered by points per expected minute.
- `why` on each row — the estimate's basis. Argue with it rather than trusting
  it. If a ranking looks wrong, the reasons say which term caused it.
- `category_strength_measured_from_disk` — how strong this toolkit actually is
  per category, read off the tree at runtime. It is honest and often
  uncomfortable: web carries 20 verified classes and 34 chain cards, DFIR
  carries one, and crypto, pwn and rev carry none. That is why a 500-point
  crypto challenge can rank below a 200-point web challenge with a matching
  card.

Anything that cannot finish inside `--minutes-left` is dropped rather than
started, because a challenge begun and abandoned costs the whole wave.

## Minute 10 to 15 — plan the fan-out

```bash
python3 tools/contest/dispatch.py <event> --minutes-left 480
```

It answers how many challenges to start and how wide each gets, bounded by two
real ceilings: the harness caps concurrent agents at `min(16, cpus - 2)`, and
the main thread has to drive a spine of its own rather than sit and wait. A
challenge that would only queue is reported `hold`, not `start` — a queued agent
is serial time wearing a parallel costume.

Expect widths of 3 to 6, and width 1 when a chain card is a strong match.

## Minute 15 onward — run the waves

Per challenge, in its own ledger:

```bash
python3 tools/state.py <id> --category <cat> --target <url> \
        --challenge-name "<real name>" --event "<event>"
python3 tools/chain_match.py --source <handout> --record <id>
python3 tools/decide.py <id>
```

Then spawn what `dispatch.py` named, **in one message so they run
concurrently**. Two kinds of fleet:

- **web and DFIR** split by bug-class family through
  `tools/subagent_fanout.py --web` / `--dfir`. These agents MEASURE; this thread
  records. Method: `skills/web-parallel-sweep/SKILL.md`,
  `skills/dfir-parallel-sweep/SKILL.md`.
- **crypto, pwn, rev, osint and misc** are SOLVER fleets. They may chain all the
  way to a flag themselves and return it. They still never run `tools/hooks.py`
  or `tools/state.py`.

Either way the flag comes back as a **candidate** with its verbatim excerpt, and
this thread alone closes it:

```bash
python3 tools/hooks.py pre-flag <id> --value '<flag>' \
        --source live-response|artifact --evidence '<verbatim excerpt>'
python3 tools/contest/board.py <event> --id <id> --status solved --flag '<flag>'
```

The gate costs seconds and it is what stops a wrong submission. It was never the
thing making this system slow.

## When a challenge stalls

Do not keep probing. `tools/decide.py` now answers `escalate` rather than
`stop_report` when the budget is spent, and it names the next untried strategy:
a chain match, a re-classification, a writeup search, a layer plan, a fleet
sweep, or a solver handoff. Spend the rung, record it, and move on:

```bash
python3 tools/decide.py <id>                     # names the rung
python3 tools/state.py <id> --strategy-used <rung>
```

`stop_report` fires only when every rung is spent. At that point write the kill
map to `knowledge/attempts/<id>.json` so the next attempt does not re-walk dead
layers, and set the board row to `dead`.

---

## Three mistakes this runbook is built around

| Do not | Because |
|---|---|
| Spawn ten agents at an easy challenge | the 7-10 minute floor eats the whole 15-30 minute time-box; solve it inline |
| Spawn and then wait | the main thread is a worker, not a dispatcher; idle time converts parallel back to serial |
| Let a subagent run `hooks.py` or `state.py` | ten parallel writers spend the probe budget in one round, and `decide.py` exists to stop exactly that |

## Scope

Authorized contests only, and only the hosts the event itself supplied. This
plane ranks and allocates; it attacks nothing on its own.
