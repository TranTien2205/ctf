# VPC flow: action + log-status

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`action` ACCEPT/REJECT; `log-status` OK/NODATA/SKIPDATA - NODATA means no flow captured in the window (a gap statement), SKIPDATA means capacity-skipped records.

## Evidence rule

A flow row is field-verbatim; a byte total is a sum over named fields -
show the fields, then the sum.

## Pivot

Wire mapped -> `api-*` for what the host was doing in the account.
