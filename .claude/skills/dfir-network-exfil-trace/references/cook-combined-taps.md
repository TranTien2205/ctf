# Cookbook: Multiple -z in one pass

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`-z io,phs -z conv,tcp -z endpoints,ip` runs once over the capture — but output order is NOT argument order (measured: endpoints first). Parse by title.

## Verification

Run the filter with `-Y` on the real bundle; quote matching rows verbatim.
A filter that matched nothing is a recorded negative, not a failure.

## Pivot

Filter shape exhausted three variants -> next channel cell or artifact
family.
