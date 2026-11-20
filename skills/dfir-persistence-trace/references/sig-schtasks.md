# Signature: `schtasks /create`

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`/tn <name> /tr <command> /sc onlogon|onstart|daily /ru <acct>`  -  the flags name the trigger and account; pairs with 4698/106. `/xml` imports a prepared task file  -  the temp XML may itself be findable.

## Use

The signature names the operator-side action; the artifact modules name
the record it leaves. Pair them: signature in 4688/Sysmon 1 + record in
the mechanism's own store = the chain.

## Pivot

Signature matched -> the corresponding mechanism module.
