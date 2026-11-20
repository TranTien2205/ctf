# Edge: Log-local vs UTC times

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

EVTX stores UTC; pfirewall.log, MPLog, some text logs are local. A 'gap' between two differently-zoned records is arithmetic, not deletion — normalise before gap arithmetic (`tools/forensics/timeline_merge.py` tiers).

## Pivot

`corpus-index.md`; the falsifier block for clean bundles.
