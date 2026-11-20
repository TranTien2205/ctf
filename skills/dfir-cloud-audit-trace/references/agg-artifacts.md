# Aggregator: Artifact index

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

AWSLogs/<acct>/CloudTrail/<region>/<Y>/<M>/<D>/*.json.gz (+ Insight/NetworkActivity/Aggregated prefixes, org O-ID variant); S3 server access log lines (27 fields); VPC flow log rows (14 default); GuardDuty finding JSON; Entra signIn/audit; M365 UAL; Okta System Log; GW Reports - the last four are UNVERIFIED bundle shapes here.

## Use

An index - open the named family module for the detail; this file
only decides which one.

## Pivot

Index consulted -> the module it names.
