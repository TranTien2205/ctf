# Question: Question: full path of the binary run at logon

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

The logon-fired mechanisms: HKLM/HKCU Run, Winlogon Userinit append, startup-folder files, LogonTrigger tasks, `LogonType` InteractiveToken tasks. The path must be the one the RECORD names  -  quote `ImagePath`/`<Command>`/value data, not a file you found by browsing.

## Answer shape

Name the mechanism, quote the record field verbatim, give the timestamp
with its artifact and offset provenance.

## Pivot

Question not answerable in this family -> the matrix (`mx-*`) names the
next family for the question shape.
