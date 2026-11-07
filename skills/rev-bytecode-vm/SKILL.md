---
name: rev-bytecode-vm
description: >
  Action-oriented depth skill for Script bytecode or custom VM. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: rev-managed-code, misc-encoding-carrier.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [rev, rev-bytecode-vm, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Script bytecode or custom VM

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

for a .pyc read the header magic and name the python version before running any decompiler, falling back to the stdlib dis module on the unmarshalled code object when uncompyle6 refuses; for a custom VM recover the OPCODE TABLE before reading one instruction of its program

**Falsifier** — the observation that closes this class: the dispatch loop is data-driven from a table that is itself generated at run time, so a static table recovery is incomplete and the program must be traced instead
## Recognise

The logic lives in bytecode: a `.pyc`, a `.class`, a serialised code object, or
a custom VM with its own dispatch loop. The bytecode is the program — disassemble
it, then replicate the check.

## Confirm

For `.pyc`, read the header magic and name the Python version **before** running
any decompiler — the marshal format is version-locked and a wrong-version load
crashes or silently misreads. The stdlib `dis` module on the unmarshalled code
object is the floor that always works.

| Bytecode | Route |
|---|---|
| `.pyc` matching your interpreter | `marshal.loads` past the header, then `dis.dis` |
| `.pyc` for another version | a version-matched decompiler, or read the magic and fetch that interpreter |
| custom VM | recover the opcode table from the dispatch loop, then trace |

Confirmation is the accepted input produced from the disassembly — a table you
recovered but never inverted is recon, not a solve.

## Traps

- A dispatch loop driven by a table generated **at run time** makes static table
  recovery incomplete — trace the program instead of reading the table.
- `uncompyle6`/`decompyle3` cover old Python versions only; `dis` covers the one
  installed, and the magic word says which that should be.
- `.pyc` headers are 12 or 16 bytes depending on version — skip the wrong count
  and `marshal.loads` fails before the code object even parses.

## Operational probe

```bash
python3 -c "import importlib.util,struct; d=open('x.pyc','rb').read(); print(d[:4].hex(), 'header', 16 if importlib.util.MAGIC_NUMBER!=d[:4] else 'check')"
python3 - <<'PY'
import dis, marshal
d = open('x.pyc','rb').read()
dis.dis(marshal.loads(d[16:]))
PY
```

## Routing

Shares signals with: `../rev-managed-code/`, `../misc-encoding-carrier/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/rev-triage/references/vm-analysis.md`
- `skills/ctf-reverse/patterns-runtime.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
