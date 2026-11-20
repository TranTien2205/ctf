# Cloud provider (UNVERIFIED): Okta event types

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Confirmed against Okta's own System Log guidance: `user.session.start` (display 'User login to Okta' - raised after the FIRST factor only), `user.authentication.auth_via_mfa`, `user.account.lock`, `system.api_token.create`, `application.user_membership.add`, `user.mfa.factor.activate`, `policy.lifecycle.update`.

## Standing

Vendor-documented fields, not measured here - catalogue-grade claims
only until a real bundle lands.

## Pivot

Provider exhausted -> the host/network classes in `../SKILL.md`
Routing.
