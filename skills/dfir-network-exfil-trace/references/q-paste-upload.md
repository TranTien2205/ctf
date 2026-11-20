# Question: Upload to a paste/sharing site

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Procedure

`http_req,tree` for hostnames like pastebin, transfer.sh, file.io; volume via `conv,tcp`. The service name is a hint — the bytes are the proof.

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
