# Question: What left inside DNS queries

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Procedure

Outbound query names only: `-Y 'dns.flags.response==0' -e dns.qry.name`. Then `python3 tools/forensics/dns_exfil.py --pcap cap [--domain suffix]` reassembles chunks — it handles the label decode and retransmission de-dup. For a `--names` file of harvested qnames the same tool applies. The raw labels alone are the evidence; the reassembled bytes answer 'what'.

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
