# Entra ID (UNVERIFIED bundle shape): AADSTS error code map

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

Verified against the Microsoft Entra error reference: 50126 InvalidUserNameOrPassword; 50053 IdsLocked (repeated bad attempts OR malicious-IP block); 50055 InvalidPasswordExpiredPassword; 50057 UserDisabled; 50074 UserStrongAuthClientAuthNRequiredInterrupt (did not pass MFA); 50076 UserStrongAuthClientAuthNRequired; 50079 UserStrongAuthEnrollmentRequired; 50158 external security challenge not satisfied; 53003 BlockedByConditionalAccess; 700016 UnauthorizedClient_DoesNotMatchRequest.

## Standing

Vendor-documented fields, not measured here - label claims from this
family catalogue-grade unless a real Entra bundle lands.

## Pivot

Entra question -> `m365-*` for the unified audit Operations.
