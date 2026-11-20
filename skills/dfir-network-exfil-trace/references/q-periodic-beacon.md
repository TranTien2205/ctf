# Question: Is the traffic periodic (beaconing)

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Procedure

`-z io,stat,60,"SUM(frame.len)frame.len and ip.src==H"` for the interval series, or the pandas delta-CV arithmetic from `../SKILL.md` (beacon cv=0.054 vs browsing cv=0.546 measured). A jittered beacon still separates by an order of magnitude on cv. Quote the interval series or the computed (n, median, mad, cv) row.

## Evidence rule

Quote the tool line(s) that carry the number — the row, the field, the
interval parameter — verbatim through `post-probe --response`. A retyped
number fails the substring gate.

## Falsifier note

If the artefact shows the clean shape (no dominant peer, no periodicity, no
channel tells), record the quoted negative — the falsifier of this question
is evidence too.

## Pivot

Answered -> stop. Three shapes inside the same artifact family with no new
record -> change family per `../SKILL.md` Discipline.
