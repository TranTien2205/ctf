# Signature: `New-Service` / `Set-Service`

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

PowerShell equivalents; command lines carry `-BinaryPathName` / `-StartupType`. Same 7045 lands; PowerShell history / ScriptBlock 4104 carries the cmdlet verbatim when logging is on.

## Use

The signature names the operator-side action; the artifact modules name
the record it leaves. Pair them: signature in 4688/Sysmon 1 + record in
the mechanism's own store = the chain.

## Pivot

Signature matched -> the corresponding mechanism module.
