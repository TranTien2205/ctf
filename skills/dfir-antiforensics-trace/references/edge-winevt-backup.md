# Edge: wevtutil epl backups

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Exported .evtx archives (wevtutil epl, 'archive the log' checkbox) are backup copies, not tamper artifacts — but their identifiers restart per export, so a gap check on a backup file produces phantom results. Know the file's provenance first.

## Pivot

`corpus-index.md`; `meth-falsifier` when every shape is benign.
