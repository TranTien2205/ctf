# Deep dive: Deep: organization trails

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`AWSLogs/<O-ID>/` prefix - delivers EVERY member account's records; `.recipientAccountId` (or the path account) is the per-record account column; dedupe on eventID.

## Use

Depth for when the row-level module is not enough - cite this file's
field when the claim rests on the decoded detail.

## Pivot

Deep read done -> the scenario (`scen-*`) or the matrix.
