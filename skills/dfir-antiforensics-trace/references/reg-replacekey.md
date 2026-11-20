# Registry: RegReplaceKeyA hive swap

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`RegReplaceKeyA()` swaps a hive's backing file — the edited replacement takes effect only at reboot; the on-disk primary can disagree with what the live system uses until then. For an offline bundle, the file IS the evidence; the reboot question only matters for live analysis.

## Evidence rule

Registry tampering claims need the physical evidence: sequence numbers,
replayed log records, or raw cell bytes — a regedit-level view cannot see
any of the hiding forms.

## Pivot

Hive clean but events show writes -> the write went to the transaction
logs; replay both.
