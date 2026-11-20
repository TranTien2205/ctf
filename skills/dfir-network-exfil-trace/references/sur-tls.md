# Suricata: event_type=tls

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`tls.sni`, `tls.subject`, `tls.issuerdn`, `tls.fingerprint`, `tls.ja3`/`tls.ja3s` where enabled, `tls.version`, `tls.session_resumed`. Same claim-vs-observation rule: pair `tls.sni` with `dest_ip`.

## Evidence rule

jq output lines are the quotable records — include the `event_type` and the
joining id (`flow_id`, `community_id`) in the excerpt.

## Pivot

flow records for volume; fileinfo for content; alerts for leads. Sensor
drops -> host-side artifacts.
