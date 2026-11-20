# VPC flow: Flows are bytes, not content

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

A flow log answers who-talked-how-much, never what-was-said - the DNS name, the API call, the object name all live elsewhere (trail, access log, resolver logs).

## Evidence rule

A flow row is field-verbatim; a byte total is a sum over named fields -
show the fields, then the sum.

## Pivot

Wire mapped -> `api-*` for what the host was doing in the account.
