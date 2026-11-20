# Question: How large were the POST bodies

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Procedure

`-Y 'http.request.method=="POST"' -e http.content_length -e http.request.full_uri -e ip.dst`. `content_length` is the claim on the wire. For the real bytes use `--export-objects http` and `ls -l` the exported files, or `tcp.len` summed per stream.

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
