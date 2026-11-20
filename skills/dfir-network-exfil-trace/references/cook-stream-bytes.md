# Cookbook: Per-stream payload bytes

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`-T fields -e tcp.stream -e tcp.len` piped to `awk '{s[$1]+=$2}END{for(k in s)print k,s[k]}'|sort -k2 -nr` — data-only volume per stream.

## Verification

Run the filter with `-Y` on the real bundle; quote matching rows verbatim.
A filter that matched nothing is a recorded negative, not a failure.

## Pivot

Filter shape exhausted three variants -> next channel cell or artifact
family.
