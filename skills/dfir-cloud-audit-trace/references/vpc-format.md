# VPC flow: VPC flow log - 14 fields

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Default format (measured `awk '{print NF}'` = 14): version, account-id, interface-id, srcaddr, dstaddr, srcport, dstport, protocol, packets, bytes, start, end, action, log-status. Custom formats exist - check NF before assuming positions.

## Evidence rule

A flow row is field-verbatim; a byte total is a sum over named fields -
show the fields, then the sum.

## Pivot

Wire mapped -> `api-*` for what the host was doing in the account.
