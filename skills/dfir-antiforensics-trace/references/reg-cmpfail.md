# Registry: CmpFailPrimarySave=3

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Setting `CmpFailPrimarySave` to 3 forces writes into the transaction logs only — invisible to any offline parser that does not replay them (dfir.ru). The primary hive looks untouched while the real data sits in .LOG1/.LOG2.

## Evidence rule

Registry tampering claims need the physical evidence: sequence numbers,
replayed log records, or raw cell bytes — a regedit-level view cannot see
any of the hiding forms.

## Pivot

Hive clean but events show writes -> the write went to the transaction
logs; replay both.
