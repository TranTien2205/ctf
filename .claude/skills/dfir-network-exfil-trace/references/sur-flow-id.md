# Suricata: flow_id pivot

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Alerts and flows share `flow_id`. From an alert to its volume: `jq -r 'select(.event_type=="alert")|[.flow_id,.timestamp,.alert.signature]|@tsv' eve.json` then `jq -r --arg f <id> 'select(.event_type=="flow" and (.flow_id|tostring)==$f)|.flow' eve.json`.

## Evidence rule

jq output lines are the quotable records — include the `event_type` and the
joining id (`flow_id`, `community_id`) in the excerpt.

## Pivot

flow records for volume; fileinfo for content; alerts for leads. Sensor
drops -> host-side artifacts.
