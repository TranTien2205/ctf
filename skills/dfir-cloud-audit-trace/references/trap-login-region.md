# Trap: ConsoleLogin region is not geography

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Root lands us-east-1/2, us-west-2; IAM user global endpoint lands us-east-2/eu-north-1/ap-southeast-2 with an alias cookie, us-east-1 without - a 'logged in from X' claim off awsRegion is wrong.

## Guard

Check before the claim it protects - each trap is a way to produce a
plausible-looking wrong answer.

## Pivot

Traps clear -> `meth-*` for the next step.
