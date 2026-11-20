# Signature: `wmic` subscription creation

Depth module for `dfir-persistence-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus  -  never a finding by itself.

`wmic /NAMESPACE:\\root\subscription PATH __EventFilter CREATE` and the CommandLineEventConsumer + __FilterToConsumerBinding triplet  -  three wmic calls or one mofcomp; Sysmon 19-21 land in sequence.

## Use

The signature names the operator-side action; the artifact modules name
the record it leaves. Pair them: signature in 4688/Sysmon 1 + record in
the mechanism's own store = the chain.

## Pivot

Signature matched -> the corresponding mechanism module.
