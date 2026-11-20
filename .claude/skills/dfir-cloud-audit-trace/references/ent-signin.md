# Entra ID (UNVERIFIED bundle shape): Entra signIn fields

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

UNVERIFIED as a bundle shape here - vendor-doc content: createdDateTime (UTC), userPrincipalName (always lowercase; guests stored as user@homedomain, not the #EXT# form), appDisplayName, appId, ipAddress, location.city/state/countryOrRegion, clientAppUsed, conditionalAccessStatus, authenticationRequirement, resourceDisplayName, correlationId, deviceDetail; status.errorCode 0 on success, AADSTS code on failure with status.failureReason.

## Standing

Vendor-documented fields, not measured here - label claims from this
family catalogue-grade unless a real Entra bundle lands.

## Pivot

Entra question -> `m365-*` for the unified audit Operations.
