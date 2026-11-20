# Matrix: Office add-in/template  -  does it survive reboot

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

For the Office add-in/template mechanism, "does it survive reboot" is answered by
from the mechanism's Start/trigger semantics. The record is the add-in DLL / template path; the base module is `misc-office.md`  - 
read it for the field names and the traps before quoting.

## Why this cell exists

Every mechanism answers a different subset of the questions, and each
has its own timestamp semantics  -  the cell pins which artifact answers
THIS question for THIS mechanism so the answer is not guessed from a
neighbouring family.

## Falsifier

If the record named above is absent AND the mechanism's own store is
confirmed readable, the mechanism did not produce this answer  -  record
the negative and move to the next cell or family.
