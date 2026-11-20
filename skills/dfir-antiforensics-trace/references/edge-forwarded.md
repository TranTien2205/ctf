# Edge: Forwarded/central logging

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

WEF forwarding copies records to a collector channel (ForwardedEvents) — a cleared source log can still exist in the forwarder's copy. Check whether the bundle ships the collector channel; its records carry the source machine name.

## Pivot

`corpus-index.md`; the falsifier block for clean bundles.
