# Question: Any traffic on rare ports

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Procedure

`tcp.dstport`/`udp.dstport` histogram: `-e tcp.dstport` | sort -n | uniq -c | sort -rn. The rare-port flow is a row near the bottom; cross-check its volume in `conv,tcp`. Non-80/443 exfil often rides 4444/53/853/1194 — but a rare port is a lead, not a finding.

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
