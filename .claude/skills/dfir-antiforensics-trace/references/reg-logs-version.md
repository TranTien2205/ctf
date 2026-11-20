# Registry: Which .LOG holds the deleted value

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

THE common statement is wrong for a Sherlock host. Vista through Windows 8 use `.LOG1` normally and switch to `.LOG2` only after a write error to the primary; Windows 8.1 and later 'regularly swap the transaction log file being used (.LOG1 to .LOG2 and vice versa)', and recovery applies entries from BOTH logs, earliest first (msuhanov, Windows registry file format specification). On Windows 10/11 never replay .LOG1 alone and conclude the value is gone.

## Evidence rule

Registry tampering claims need the physical evidence: sequence numbers,
replayed log records, or raw cell bytes — a regedit-level view cannot see
any of the hiding forms.

## Pivot

Hive clean but events show writes -> the write went to the transaction
logs; replay both.
