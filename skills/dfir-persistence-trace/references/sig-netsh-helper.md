# Signature: `netsh add helper`

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`netsh add helper <dll>`  -  writes SOFTWARE `Microsoft\Netsh` value; the netsh invocation in 4688 is the signature; fires whenever ANY netsh runs  -  an ambient mechanism.

## Use

The signature names the operator-side action; the artifact modules name
the record it leaves. Pair them: signature in 4688/Sysmon 1 + record in
the mechanism's own store = the chain.

## Pivot

Signature matched -> the corresponding mechanism module.
