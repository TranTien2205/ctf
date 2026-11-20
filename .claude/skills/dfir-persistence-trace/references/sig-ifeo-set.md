# Signature: IFEO set via reg/powershell

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`reg add 'HKLM\...\Image File Execution Options\<exe>' /v Debugger /d <payload>`  -  the target exe name is the tell (sethc/utilman/osk/narrator/magnify = sticky-keys shape).

## Use

The signature names the operator-side action; the artifact modules name
the record it leaves. Pair them: signature in 4688/Sysmon 1 + record in
the mechanism's own store = the chain.

## Pivot

Signature matched -> the corresponding mechanism module.
