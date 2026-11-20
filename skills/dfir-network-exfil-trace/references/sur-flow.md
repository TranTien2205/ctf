# Suricata: event_type=flow

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Volume lives here: `bytes_toserver`, `bytes_toclient`, `pkts_toserver`, `pkts_toclient`, `start`, `end`, `age`. Rank: `jq -r 'select(.event_type=="flow")|[.flow.start,.src_ip,.dest_ip,.dest_port,.flow.bytes_toserver,.flow.bytes_toclient]|@tsv' eve.json | sort -k5 -nr | head`. `toserver` is the client-to-server direction — outbound when the host is the client.

## Evidence rule

jq output lines are the quotable records — include the `event_type` and the
joining id (`flow_id`, `community_id`) in the excerpt.

## Pivot

flow records for volume; fileinfo for content; alerts for leads. Sensor
drops -> host-side artifacts.
