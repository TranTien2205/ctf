# Question: How many bytes left this host

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Procedure

`tshark -r cap -q -z endpoints,ip` — read the `Tx Bytes` column for the internal host. Measured fixture: `10.10.10.5 48 11776 28 9896 20 1880`; Tx=9896 is the answer, Bytes=11776 is both directions and is not. Fallback when tshark is unavailable: `pcap_triage.py --input cap --challenge <name> --class dfir-network-exfil-trace` answers the same question offline with stdlib code.

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
