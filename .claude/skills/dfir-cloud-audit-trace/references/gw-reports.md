# Cloud provider (UNVERIFIED): Google Workspace Reports shape

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

UNVERIFIED bundle shape: `id.time`, `id.applicationName`, `actor.email`, `ipAddress`, `events[].name`/`.type`, `events[].parameters[].name`/`.value`.

## Standing

Vendor-documented fields, not measured here - catalogue-grade claims
only until a real bundle lands.

## Pivot

Provider exhausted -> the host/network classes in `../SKILL.md`
Routing.
