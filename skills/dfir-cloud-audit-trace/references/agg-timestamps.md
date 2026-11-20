# Aggregator: Timestamp index

Depth module for `dfir-cloud-audit-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus - never a finding by itself.

eventTime UTC ISO; S3 Time `[%d/%b/%Y:%H:%M:%S %z]`; flow start/end Unix seconds over the interval; finding eventFirstSeen/LastSeen; Entra createdDateTime; Okta published; GW id.time - all UTC, normalise before merge.

## Use

An index - open the named family module for the detail; this file
only decides which one.

## Pivot

Index consulted -> the module it names.
