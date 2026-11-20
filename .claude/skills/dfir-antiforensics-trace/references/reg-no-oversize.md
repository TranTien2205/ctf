# Registry: No oversized-value trick documented

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

The dfir.ru article documents no oversized-value trick — do not claim one. When a technique is not in the cited source, it is not in the corpus.

## Evidence rule

Registry tampering claims need the physical evidence: sequence numbers,
replayed log records, or raw cell bytes — a regedit-level view cannot see
any of the hiding forms.

## Pivot

Hive clean but events show writes -> the write went to the transaction
logs; replay both.
