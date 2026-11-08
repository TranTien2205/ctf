---
name: misc-constraint-puzzle
description: >
  Action-oriented depth skill for Constraint / speed puzzle. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: misc-interpreter-escape, misc-encoding-carrier.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [misc, constraint-puzzle, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Constraint / speed puzzle

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

connect once and capture the exact protocol before writing a solver — guessing the format from the banner wastes the round budget

**Falsifier** — the observation that closes this class: the service has no interactive protocol at all — a static page or a file, not a socket conversation
## Recognise

A service address (`nc host port`), a socket protocol, and a puzzle that
must be answered fast or in volume — math expressions, mazes, CAPTCHA-ish
parsing, rounds of increasing difficulty. The bug is not in the service; the
challenge is writing a correct, fast client.

## Confirm safely

All work is against the lab service. Evidence is the flag the service emits
when the solver completes the rounds — the solver transcript is the proof.

## Working order

1. Connect once manually (`nc` or a raw socket) and capture the protocol
   verbatim — banner, prompt, expected answer format, terminator, timeout.
2. Write the solver against the CAPTURED format, not the guess: parse
   exactly what arrived, compute, reply exactly as expected.
3. Test on one round, then let it run — log every round so the last failing
   round shows the format edge you missed.
4. Only then optimize: timeouts, buffering, round-trip batching.

`references/protocol-first.md` carries a stdlib client skeleton and the
format edges that break solvers.

## Traps

- TCP is a stream, not messages — a read can return half a puzzle or two
  puzzles at once; buffer until the prompt terminator, never assume one
  recv() is one question.
- The prompt terminator is usually `
`, `> `, or `: ` — capture it verbatim
  on the manual run; guessing it desyncs every later round.
- Late rounds change the format (bigger numbers, new operators, wrapped
  text) — log each round's raw bytes; the failure is a format drift, not
  your math.

## Operational probe

```bash
python3 tools/net_dialog.py host 31337          # banner grab, like nc | head
# scripted rounds once the protocol is captured:
python3 tools/net_dialog.py host 31337 --steps 'wait:> ; send:1\n ; dump'
```

## Routing

Shares signals with: `../misc-interpreter-escape/`, `../misc-encoding-carrier/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/misc-constraint-puzzle/references/README.md`
- `skills/misc-constraint-puzzle/references/protocol-first.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
