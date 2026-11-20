# Suricata: event_type=alert

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

An alert names a SIGNATURE (`alert.signature`, `alert.category`, `alert.severity`), not a byte count. It is a lead pointing at a flow_id — never report it as the exfiltration itself.

## Evidence rule

jq output lines are the quotable records — include the `event_type` and the
joining id (`flow_id`, `community_id`) in the excerpt.

## Pivot

flow records for volume; fileinfo for content; alerts for leads. Sensor
drops -> host-side artifacts.
