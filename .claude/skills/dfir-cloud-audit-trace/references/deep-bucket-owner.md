# Deep dive: Deep: Bucket Owner vs Requester

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

S3 access log field 1 is the BUCKET's owner account, field 5 the requester - cross-account access reads differently than same-account; owner is not the actor.

## Use

Depth for when the row-level module is not enough - cite this file's
field when the claim rests on the decoded detail.

## Pivot

Deep read done -> the scenario (`scen-*`) or the matrix.
