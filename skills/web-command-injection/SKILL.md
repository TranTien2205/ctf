---
name: web-command-injection
description: >
  OS command injection. Open after the router or tools/classify.py named this class.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [web, command-injection, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
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

A request value reaches a shell. In source that is a shell-enabled subprocess
call, a PHP execution function, or a Node `child_process` call built by
concatenation. In a response it is command output leaking into the page, or an
error from `/bin/sh`.

Distinguish from template injection: template engines evaluate expressions, not
shell syntax. If an arithmetic marker evaluates, it is `../web-ssti/`.

## Confirm

One separator, one command whose output cannot be mistaken for anything else.
If nothing is echoed, use a timing command as the channel — the same discipline
as a blind SQL oracle: measure the baseline first.

## When the obvious separators are filtered

The usual escapes are shell features, not tricks: brace and variable expansion,
positional parameters, quoting that survives the filter, and alternative
separators. The catalogue is in `../ctf-web/server-side-2.md` and
`../ctf-web/server-side-exec.md`.

## Traps

- A filter that blocks a character list is usually bypassable; one that passes
  the value as a single argv element is not. Read the source before spending the
  budget.
- Output-free injection plus an outbound network block leaves only timing. Say so
  rather than claiming the injection failed.

## Routing

Shares signals with: `../web-ssti/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/ctf-web/server-side-exec.md`
- `skills/ctf-web/server-side-2.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
