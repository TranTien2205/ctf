# Deep: PSReadLine history deletion trail

Depth module for `dfir-antiforensics-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Deleting `ConsoleHost_history.txt` leaves a $J 0x200 naming it (T1070.003), and transcripts (`EnableTranscripting`, `OutputDirectory`) may hold the same commands elsewhere. The history file's absence + its delete record = the wiped answer.

## Evidence rule

Format detail supports the record — the quotable evidence is still the
probe output, not the layout itself.

## Pivot

`corpus-index.md` for the family list.
