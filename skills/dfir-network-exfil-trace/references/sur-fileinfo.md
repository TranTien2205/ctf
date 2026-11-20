# Suricata: event_type=fileinfo

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Per seen file: `fileinfo.filename` (a claim), `fileinfo.size`, `fileinfo.md5`/`sha256`, `fileinfo.stored`, `fileinfo.magic`. `stored=true` means the file was saved — carve path is the bundle's file store.

## Evidence rule

jq output lines are the quotable records — include the `event_type` and the
joining id (`flow_id`, `community_id`) in the excerpt.

## Pivot

flow records for volume; fileinfo for content; alerts for leads. Sensor
drops -> host-side artifacts.
