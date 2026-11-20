# Matrix: systemd unit/timer/generator  -  which account it runs as

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

For the systemd unit/timer/generator mechanism, "which account it runs as" is answered by
AccountName/ObjectName/UserId/LogonType  -  the run-as, not the creator. The record is ExecStart line; the base module is `lnx-systemd-dirs.md`  - 
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
