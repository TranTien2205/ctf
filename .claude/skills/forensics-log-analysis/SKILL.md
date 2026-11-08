---
name: forensics-log-analysis
description: >
  Action-oriented depth skill for Log file analysis. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: dfir-authentication-trace, forensics-pcap-carve.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [forensics, log-analysis, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Log file analysis

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

wc -l and head/tail first — bracket the timeframe and count the volume before greping, so a count claim has a baseline

`tools/log_summary.py` does that opening without awk on the box:
`summary FILE` gives line count, first/last lines, detected timestamp
range, per-hour histogram, and top-N counts of IPs / users / paths /
status codes plus any flag-like lines; `field --regex` runs a custom
distribution, `window --around N` prints the context lines.

**Falsifier** — the observation that closes this class: the log is syntactically uniform — every line the same shape, no outlier entry, no anomaly against its own baseline
## Recognise

Log files are the handout (access.log, auth.log, syslog, a web or app log)
and the question is a fact inside them: an IP, a user, a request, a command,
the moment something happened. Extraction-shaped — find the line, quote it.

## Confirm safely

All reads are local. The evidence is the verbatim log line plus the count or
baseline that makes it anomalous — one weird line among N normal ones.

## Working order

1. `wc -l` + `head`/`tail` — volume and timeframe, so every later claim has
   a denominator.
2. Distribution first, lines second: `cut`/`awk` the field of interest
   (source IP, status, path, user-agent) into `sort | uniq -c | sort -rn` —
   the anomaly is almost always a count outlier.
3. `grep` the specific question terms (flag, admin, path, user) after the
   distribution shows where normal lives.
4. Reconstruct the sequence around the hit: `grep -n` gives line numbers;
   read ±20 lines for the surrounding session.

`references/pattern-order.md` maps question shape to the field to cut.

## Traps

- A timestamp-only grep misses the timezone story — check which zone the log
  records before answering "when".
- One log line rarely proves intent — the line before it (referer, prior
  request) carries the context the question usually wants.
- Rotated/compressed siblings (`*.log.1`, `*.log.gz`) hold the earlier
  window — `zgrep`/`zcat` them; a single-file baseline can hide the anomaly
  in a file you never read.

## Operational probe

```bash
wc -l access.log && head -1 access.log && tail -1 access.log
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head
awk '{print $9}' access.log | sort | uniq -c | sort -rn | head
```

## Routing

Shares signals with: `../dfir-authentication-trace/`, `../forensics-pcap-carve/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/forensics-log-analysis/references/README.md`
- `skills/forensics-log-analysis/references/pattern-order.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
