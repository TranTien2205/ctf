# Entra ID (UNVERIFIED bundle shape): clientAppUsed - the MFA skip

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

`Browser`, `modern clients`, and the LEGACY set `Exchange ActiveSync`, `IMAP`, `MAPI`, `SMTP`, `POP`, `other clients` - a legacy value on a SUCCESS record is how MFA was skipped (legacy protocols do not do modern auth).

## Standing

Vendor-documented fields, not measured here - label claims from this
family catalogue-grade unless a real Entra bundle lands.

## Pivot

Entra question -> `m365-*` for the unified audit Operations.
