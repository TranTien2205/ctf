# Signature: `launchctl load` shape

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`launchctl load -w <plist>`  -  the `-w` writes the disable override OFF; file creation in LaunchAgents/Daemons is the on-disk record.

## Use

The signature names the operator-side action; the artifact modules name
the record it leaves. Pair them: signature in 4688/Sysmon 1 + record in
the mechanism's own store = the chain.

## Pivot

Signature matched -> the corresponding mechanism module.
