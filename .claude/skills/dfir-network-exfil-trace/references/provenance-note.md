# Provenance and quoting discipline

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Why the quoting rule is this strict

DFIR answers are re-derivable by a reviewer: '9,080 bytes' means nothing
until the reviewer runs the same command on the same artifact. So every
answer in this class carries enough to reproduce it: the tool, the flags,
the artifact path, and the verbatim row.

## What counts as the record

- A `-z` tap row with its table title.
- A `-T fields` line with `-E header=y` enabled.
- A `follow` chunk including its direction header.
- An `evtx_query.py` row or `--answer` output.
- A Zeek/Suricata line grep'd verbatim.
- A file listing line for an exported object, plus the file's own hash.

## What does not

- A sum computed in your head across rows.
- A filename treated as proof of content.
- A 'typically/usually' statement where a row exists.
- Anything retyped; `--answer` exists so values are never retyped.
