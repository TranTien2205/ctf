# Cloud provider (UNVERIFIED): M365 unified audit Operations

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

UNVERIFIED bundle shape: `UserLoggedIn`, `UserLoginFailed`, `New-InboxRule` (the mail-forwarding persistence), `Set-Mailbox`, `Add-MailboxPermission`, `MailItemsAccessed` (the read event), `FileDownloaded`, `SharingInvitationCreated`, `Add-Member`, `Send`, `SendAs`, `SendOnBehalf`.

## Standing

Vendor-documented fields, not measured here - catalogue-grade claims
only until a real bundle lands.

## Pivot

Provider exhausted -> the host/network classes in `../SKILL.md`
Routing.
