# Suricata: event_type=anomaly

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Decoder/parser anomalies per packet or flow — protocol-mismatch and crafted-packet tells. Names the anomaly type and the layer.

## Evidence rule

jq output lines are the quotable records — include the `event_type` and the
joining id (`flow_id`, `community_id`) in the excerpt.

## Pivot

flow records for volume; fileinfo for content; alerts for leads. Sensor
drops -> host-side artifacts.
