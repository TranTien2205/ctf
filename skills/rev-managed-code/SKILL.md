---
name: rev-managed-code
description: >
  Action-oriented depth skill for Managed runtime decompilation. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: rev-native-check, rev-bytecode-vm.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [rev, rev-managed-code, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Managed runtime decompilation

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

confirm the runtime from the header and quote the bytes -- a PE with a non-zero CLR data directory, or the 0xCAFEBABE magic -- then decompile with what exists here: ilspycmd for .NET, javap plus unzip for Java. jadx, procyon and mono are absent

**Falsifier** — the observation that closes this class: the assembly is a thin native stub and the logic is in an unmanaged module, so no managed decompiler reaches it and the work belongs to rev-native-check
## Recognise

The binary is managed: a PE with a non-zero CLR data directory, a `0xCAFEBABE`
class file, a dex, or a Python-packed executable. Decompilers exist for every
one of these — the job is matching the tool to the runtime.

## Confirm

Prove the runtime from the header **bytes**, quote them, then decompile with
what exists:

| Artifact | Tool family |
|---|---|
| PE + CLR directory | dnSpy / ILSpy / `ilspycmd` — and the binary often still carries unobfuscated metadata |
| `.class` / `.jar` | cfr / procyon / `javap -c` as the always-available floor |
| `.dex` / `.apk` | jadx |
| PyInstaller / py2exe bundle | extract the `.pyc`, then `../rev-bytecode-vm/` |

Confirmation is the deciding check read in decompiled form and replicated —
recompute the accepted input, do not narrate the algorithm.

## Traps

- A managed-looking binary can be a thin native stub: if the CLR directory is
  empty or the jar is only a launcher, the work belongs to `../rev-native-check/`.
- Obfuscators rename everything — follow data flow to the check, not
  identifier names.
- Single-file .NET bundles need the embedded assemblies extracted before the
  decompiler sees real code.

## Operational probe

```bash
file ./chal
rabin2 -I ./chal | grep -i clr     # CLR data directory non-zero?
strings ./chal | grep -iE "dotnet|mscoree|java|kotlin"
```

## Routing

Shares signals with: `../rev-native-check/`, `../rev-bytecode-vm/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/rev-triage/references/managed-code.md`
- `skills/ctf-reverse/languages-platforms.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
