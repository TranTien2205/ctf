# Question: Does the SNI match the destination

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Procedure

`-e tls.handshake.extensions_server_name -e ip.dst -e tcp.stream` per ClientHello. SNI is a client claim; `ip.dst` is the observation. A mismatch (SNI a popular CDN, dst an unrelated VPS) is the domain-fronting tell. ECH/ESNI hides SNI entirely — then only `ip.dst` exists.

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
