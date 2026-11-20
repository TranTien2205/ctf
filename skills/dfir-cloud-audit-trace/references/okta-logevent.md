# Cloud provider (UNVERIFIED): Okta System Log shape

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

UNVERIFIED bundle shape: `eventType`, `outcome.result` (SUCCESS/FAILURE), `outcome.reason`, `actor`, `client`, `published`, `displayMessage`, `severity`, `securityContext`, `target`, `transaction`.

## Standing

Vendor-documented fields, not measured here - catalogue-grade claims
only until a real bundle lands.

## Pivot

Provider exhausted -> the host/network classes in `../SKILL.md`
Routing.
