# Suricata: Direction in eve.json

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`toserver`/`toclient` fields are written from the SENSOR's view of the session initiator, matching the alert's src->dest. Verify with `src_ip`/`dest_ip` — a flow the external host opened TO the internal host still has its bytes in `bytes_toserver` where 'server' is the internal one. Read `src_ip` first.

## Evidence rule

jq output lines are the quotable records — include the `event_type` and the
joining id (`flow_id`, `community_id`) in the excerpt.

## Pivot

flow records for volume; fileinfo for content; alerts for leads. Sensor
drops -> host-side artifacts.
