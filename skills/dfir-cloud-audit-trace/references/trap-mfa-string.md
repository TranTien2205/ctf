# Trap: mfaAuthenticated 'false' proves nothing

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

False by design on federated/assumed-role calls - true only for IAM user/root with MFA. A 'no MFA' claim off an assumed-role record is backwards.

## Guard

Check before the claim it protects - each trap is a way to produce a
plausible-looking wrong answer.

## Pivot

Traps clear -> `meth-*` for the next step.
