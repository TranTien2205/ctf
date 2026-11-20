# Aggregator: Provider capability matrix

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

CloudTrail: control-plane calls (data events off). S3 access log: object reads + auth failures + lifecycle (not in CloudTrail). Flow: bytes only. GuardDuty: summaries -> windows. Entra signIn/audit: sign-ins vs directory changes. M365 UAL: mailbox/sharepoint Operations. Okta: session + policy events. GW: login + admin events.

## Use

An index - open the named family module for the detail; this file
only decides which one.

## Pivot

Index consulted -> the module it names.
