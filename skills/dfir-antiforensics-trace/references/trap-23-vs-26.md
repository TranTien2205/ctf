# Trap: 23 archives, 26 does not

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Sysmon 23 copies the deleted file into ArchiveDirectory; 26 only logs. A bundle carrying only 26 means the events exist and the BYTES do not — don't spend the budget carving for an archive that never happened.

## Defence

Pair every tamper signal with the check that distinguishes it from its
benign twin, and quote the distinguishing field in the answer.

## Related

`../SKILL.md` Traps section for the class-level list.
