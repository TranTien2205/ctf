# Cloud provider (UNVERIFIED): user.session.start scope

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Fires after the FIRST factor - a session.start with no auth_via_mfa follow-up is a primary-auth success, not a full MFA pass; do not read it as 'logged in fully'.

## Standing

Vendor-documented fields, not measured here - catalogue-grade claims
only until a real bundle lands.

## Pivot

Provider exhausted -> the host/network classes in `../SKILL.md`
Routing.
