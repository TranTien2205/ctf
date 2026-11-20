# Cookbook: Fields that repeat per packet

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`http.*`/`dns.*` fields can appear multiple times in one frame (pipelined requests, multi-answer responses): `-E occurrence=a|f|l` controls all/first/last. Default varies by version — set it explicitly.

## Verification

Run the filter with `-Y` on the real bundle; quote matching rows verbatim.
A filter that matched nothing is a recorded negative, not a failure.

## Pivot

Filter shape exhausted three variants -> next channel cell or artifact
family.
