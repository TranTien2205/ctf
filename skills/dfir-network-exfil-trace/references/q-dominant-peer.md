# Question: Which external peer took the bulk

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Procedure

`-z conv,tcp` and `-z conv,udp`, rank by the `->` column away from the internal host (the SECOND byte pair — `tap-conv-tcp` documents the direction trap). A peer under a CDN edge IP needs SNI/`http.host` for naming; ground the answer on `ip.dst`.

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
