# Cookbook: Follow with a range

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Syntax `prot,mode,filter[,range]`: `follow,tcp,ascii,0:0-5000` bounds the dump to the first 5000 bytes of stream 0 — keeps giant streams quotable.

## Verification

Run the filter with `-Y` on the real bundle; quote matching rows verbatim.
A filter that matched nothing is a recorded negative, not a failure.

## Pivot

Filter shape exhausted three variants -> next channel cell or artifact
family.
