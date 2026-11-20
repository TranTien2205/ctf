# Cookbook: Set membership filters

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`in {a b c}` / `in {a .. z}` — `dns.qry.type in {10,16}`, `tcp.dstport in {4444 53 853}` — cleaner than OR chains and the brace syntax is the documented one.

## Verification

Run the filter with `-Y` on the real bundle; quote matching rows verbatim.
A filter that matched nothing is a recorded negative, not a failure.

## Pivot

Filter shape exhausted three variants -> next channel cell or artifact
family.
