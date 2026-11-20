# VPC flow: interface-id joins

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

eni-* joins flows to the instance/asset - ENI attachment records (or the account's inventory) name which workload produced the flow.

## Evidence rule

A flow row is field-verbatim; a byte total is a sum over named fields -
show the fields, then the sum.

## Pivot

Wire mapped -> `api-*` for what the host was doing in the account.
