---
name: misc-interpreter-escape
description: >
  Action-oriented depth skill for Restricted interpreter escape. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: misc-encoding-carrier.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [misc, misc-interpreter-escape, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Restricted interpreter escape

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

MAP THE FILTER before writing an escape: send single probe characters and short tokens until the blocked bytes, names and node types are known and the layer the check runs at is named, because that mapping is the challenge and the escape is mechanical afterwards

**Falsifier** — the observation that closes this class: the check runs on the parsed AST and rejects every node type that can reach an attribute or a call, so no expression in the remaining grammar reaches a live object
## Recognise

Input is evaluated: a pyjail, a restricted `eval`/`exec`, a filtered shell, or
a REPL that names a blocked word in its error. The error message is the first
map of the filter — read it before writing anything.

## Confirm

Map the filter **before** the escape. Send single characters and short tokens
until you know whether the check is a string blacklist, a parsed-AST rule, or a
sandbox below the interpreter. Each layer has a different escape shape:

| Filter layer | Escape shape |
|---|---|
| string blacklist on names | `getattr`, `getattr(obj, "attr"[::-1])`, `chr()` joins |
| blocked brackets or quotes | f-strings, format specs, `().__class__` chains, `subclasses()` walk |
| AST node rejection | only the grammar the checker forgot: decorators, `with`, exception args |
| shell keyword block | `$IFS`, globs, `${var:offset:1}`, command substitution |

Confirmation is code execution you observe: `id`, a read of the flag path, or
output the jail claims to forbid.

## Traps

- An AST check rejects **node types**, not strings — a blacklisted word can
  still be reachable through `__builtins__`, `getattr`, or an object that
  carries it as an attribute.
- `__subclasses__` walks are index-fragile: enumerate them at run time instead
  of hard-coding an index from a different build.
- A jail that echoes errors is free recon — quote the rejection in your notes;
  it names the exact layer.

## Operational probe

```text
1+1                     # does it evaluate at all?
"".__class__            # attribute access alive?
().__class__.__mro__    # how far does the chain climb?
globals()               # namespace readable?
```

## Routing

Shares signals with: `../misc-encoding-carrier/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/ctf-misc/pyjails.md`
- `skills/ctf-misc/jails-and-shells.md`
- `skills/ctf-misc/bashjails.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
