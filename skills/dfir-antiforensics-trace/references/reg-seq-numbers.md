# Registry: regf sequence numbers

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Registry base block: `regf` at 0x00, PRIMARY sequence number at 0x04, SECONDARY at 0x08. Equal = clean hive; unequal, or a bad checksum at 0x1FC, = dirty — writes landed that the primary hive never absorbed, and the .LOG files hold them.

## Evidence rule

Registry tampering claims need the physical evidence: sequence numbers,
replayed log records, or raw cell bytes — a regedit-level view cannot see
any of the hiding forms.

## Pivot

Hive clean but events show writes -> the write went to the transaction
logs; replay both.
