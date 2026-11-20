# VPC flow: bytes are per-interval

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

start/end are Unix seconds over the aggregation interval (10 min default, 1 min on Nitro) - egress volume is a SUM: `awk '$13=="ACCEPT" {b[$5]+=$10} END{for(i in b) print i, b[i]}'` (bytes to each dstaddr).

## Evidence rule

A flow row is field-verbatim; a byte total is a sum over named fields -
show the fields, then the sum.

## Pivot

Wire mapped -> `api-*` for what the host was doing in the account.
