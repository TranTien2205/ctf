# Deep dive: Deep: anonymous records

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

sourceIPAddress still populated; userIdentity.type can be absent/'-' shapes on anonymous calls; Requester `-` in S3 access logs - anonymous != invisible.

## Use

Depth for when the row-level module is not enough - cite this file's
field when the claim rests on the decoded detail.

## Pivot

Deep read done -> the scenario (`scen-*`) or the matrix.
