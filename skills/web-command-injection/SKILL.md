---
name: web-command-injection
description: >
  Action-oriented depth skill for OS command injection. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: web-ssti.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [web, command-injection, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# OS command injection

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

one benign separator with a command whose output is unmistakable, and a timing variant as a fallback channel

**Falsifier** — the observation that closes this class: the value is passed as a single argv element, never through a shell
## Recognise

First prove the **sink and shell boundary**. In source, distinguish
`execFile`/argument-array execution from `shell=True`, `system`, `popen`, or a
string passed to a shell. In black-box evidence, look for command output or a
shell-specific error, not merely a slow response.

## Confirm

1. Establish one timing baseline with a harmless input.
2. Use one benign separator and a deterministic, non-destructive identity
   command available in the challenge's stated environment.
3. Compare the response body, status, and timing with the baseline.
4. If output is not returned, use a bounded timing channel and record repeated
   baseline/variant measurements. One slow request is inconclusive.

Expected confirmation is an attributable output marker or a repeatable timing
delta caused by the command. A parser error, timeout, or generic 500 is not
confirmation.

## Source decision tree

| Sink | Meaning |
|---|---|
| argument array / `execFile` without shell | command injection is falsified at this layer |
| shell-enabled subprocess or concatenated command string | continue with a read-only probe |
| template expression evaluates | route to `web-ssti`, not shell injection |
| user input only reaches a filename/API argument | inspect traversal or logic instead |

Use one named reference after the sink is confirmed:
`../ctf-web/server-side-exec.md` or `../ctf-web/server-side-2.md`.

## Traps

- Do not use destructive commands, filesystem writes, reverse shells, or broad
  network callbacks for the first probe.
- Character filtering is not the same as shell isolation; conversely, a single
  argv element is not a bypass challenge. Read the call boundary first.
- Output-free injection plus a blocked outbound channel remains inconclusive
  unless the timing delta is repeatable and attributable.

## Routing

Shares signals with: `../web-ssti/`. Check those before committing to this one.

Depth, one named file at a time:

- `../ctf-web/server-side-exec.md`
- `../ctf-web/server-side-2.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
