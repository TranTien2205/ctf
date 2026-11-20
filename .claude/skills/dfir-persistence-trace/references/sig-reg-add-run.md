# Signature: `reg add ...\Run`

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`reg add HKLM\...\CurrentVersion\Run /v <name> /d <cmd>`  -  Sysmon 13 catches the value-set even when the command line is missed; the 4688 names the operator.

## Use

The signature names the operator-side action; the artifact modules name
the record it leaves. Pair them: signature in 4688/Sysmon 1 + record in
the mechanism's own store = the chain.

## Pivot

Signature matched -> the corresponding mechanism module.
