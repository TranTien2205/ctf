# Registry: Null-byte value names

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

dfir.ru, Hiding data in the registry: a NULL BYTE embedded in a value name via the native API — `regedit.exe` and `reg.exe` cannot open it because the Win32 API treats the null as a terminator. `RegDelNull` 'scans the registry for null embedded entries'; an OFFLINE hive parser reading raw name bytes sees the name regardless — the hiding only works through the Win32 view.

## Evidence rule

Registry tampering claims need the physical evidence: sequence numbers,
replayed log records, or raw cell bytes — a regedit-level view cannot see
any of the hiding forms.

## Pivot

Hive clean but events show writes -> the write went to the transaction
logs; replay both.
