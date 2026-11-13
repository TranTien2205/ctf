---
name: forensics-memory-analysis
description: >
  Action-oriented depth skill for Memory image analysis. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: dfir-execution-trace, forensics-pcap-carve.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [forensics, memory-analysis, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Memory image analysis

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

identify the image profile before any plugin — volatility3 imageinfo/pslist against an unidentified image lies silently

**Falsifier** — the observation that closes this class: process list, command lines, network connections and file scans all account for the image's normal workload
## Recognise

A memory image is the handout (`*.raw`, `*.vmem`, `*.mem`, `*.dmp`, hiberfil)
and the answer is what the machine was doing: a running process, a typed
command, an open file, a password or key in memory, injected code.

## Confirm safely

All reads are local. The evidence is the plugin output itself — a `pslist`
row, a `cmdline` hit, a `filescan` path, dumped bytes containing the flag —
quote it verbatim.

## Extraction order

1. Identify the image: volatility3 `windows.info` (or `banners` on Linux
   images). A wrong-profile `pslist` produces garbage that LOOKS like a
   process list — the profile step is the falsifier of the whole session.
2. `pslist`/`pstree` — the odd process names the suspect.
3. `cmdline`, `netscan`, `filescan` — what it ran, talked to, and opened.
4. `memmap`/`dumpfiles`/`procdump` on the suspect — the flag is usually in
   the process's own memory or the file it had open.
5. `malfind`/`hivescan` only after a process lead exists.

`references/plugin-order.md` maps the goal to the plugin and the one-liner.

## Traps

- `volatility2` vs `volatility3` flag syntax differs completely — check which
  is installed before copying a writeup command.
- Windows Defender often deleted the suspicious binary from disk but the
  evidence survives in memory — `filescan` the path, `memmap` the process.
- A `pslist` full of svchosts is normal; sort by start-time and look at the
  tail — challenge processes run late and alone.

## Operational probe

```bash
vol -f mem.raw windows.info
vol -f mem.raw windows.pslist
vol -f mem.raw windows.cmdline | grep -v svchost
```

volatility absent? `python3 tools/forensics/crashdump.py mem.dmp`
reads the PAGE/DU64 header directly — bugcheck code + 4 params
(answers "why did it crash"), machine type, DTB / PFN database /
PsLoadedModuleList / PsActiveProcessHead kernel pointers, and
recognises minidumps (`MDMP`). Content extraction then falls back
to `tools/forensics/ioc_scan.py mem.dmp --utf16` — strings, paths,
URLs and flag tokens with byte offsets.

## Routing

Shares signals with: `../dfir-execution-trace/`, `../forensics-pcap-carve/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/forensics-memory-analysis/references/README.md`
- `skills/forensics-memory-analysis/references/plugin-order.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
