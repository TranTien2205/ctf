# Signature: Profile file write

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

A write to `Documents\WindowsPowerShell\profile.ps1` or the System32 AllUsers path  -  Sysmon 11 on the profile path, or the file itself; every console start fires it.

## Use

The signature names the operator-side action; the artifact modules name
the record it leaves. Pair them: signature in 4688/Sysmon 1 + record in
the mechanism's own store = the chain.

## Pivot

Signature matched -> the corresponding mechanism module.
