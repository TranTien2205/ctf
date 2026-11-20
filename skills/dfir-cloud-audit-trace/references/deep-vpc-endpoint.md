# Deep dive: Deep: AwsVpceEvents

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: start probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

VPC endpoint policy evaluations produce AwsVpceEvents - a denied endpoint call can leave the vpce record plus a denied trail record; both are 'it was refused' evidence.

## Use

Depth for when the row-level module is not enough - cite this file's
field when the claim rests on the decoded detail.

## Pivot

Deep read done -> the scenario (`scen-*`) or the matrix.
