# Question: Question: does it survive a reboot

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

Answer from the mechanism's semantics: service Start 0-2 yes, Start 3-4 needs a starter; BootTrigger/CalendarTrigger tasks yes; Run keys yes at next logon; RunOnce fires once then deletes  -  survives only if the value is still there; WMI permanent subscriptions yes.

## Answer shape

Name the mechanism, quote the record field verbatim, give the timestamp
with its artifact and offset provenance.

## Pivot

Question not answerable in this family -> the matrix (`mx-*`) names the
next family for the question shape.
