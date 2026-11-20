# Signature: `sc create` / `sc config`

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

cmdline `sc \\<host> create <name> binpath= <path> start= auto`  -  Sysmon 1/4688 ParentImage cmd.exe or the operator shell; pairs with the 7045 that lands seconds later. `sc config <name> start= auto` is the start-type flip -> also a 7040.

## Use

The signature names the operator-side action; the artifact modules name
the record it leaves. Pair them: signature in 4688/Sysmon 1 + record in
the mechanism's own store = the chain.

## Pivot

Signature matched -> the corresponding mechanism module.
