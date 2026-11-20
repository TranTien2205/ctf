# Suricata: eve.json layout

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

One JSON object per line keyed by `event_type`. Documented values: `alert`, `flow`, `dns`, `http`, `tls`, `fileinfo`, `ftp`, `ftp_data`, `smb`, `ssh`, `anomaly`, `stats` (Suricata eve-json-format). Parse with jq per `event_type`, never as a flat array.

## Evidence rule

jq output lines are the quotable records — include the `event_type` and the
joining id (`flow_id`, `community_id`) in the excerpt.

## Pivot

flow records for volume; fileinfo for content; alerts for leads. Sensor
drops -> host-side artifacts.
