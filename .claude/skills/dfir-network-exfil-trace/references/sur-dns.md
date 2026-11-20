# Suricata: event_type=dns

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

v2 format groups under `dns.rrname`, `dns.rrtype`, `dns.rcode`; grouped answers under `dns.answers`/`dns.grouped`. Histogram `rrname` parents and `rrtype` for the tunnel shape.

## Evidence rule

jq output lines are the quotable records — include the `event_type` and the
joining id (`flow_id`, `community_id`) in the excerpt.

## Pivot

flow records for volume; fileinfo for content; alerts for leads. Sensor
drops -> host-side artifacts.
