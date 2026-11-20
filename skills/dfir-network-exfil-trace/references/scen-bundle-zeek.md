# Scenario: Bundle with Zeek logs

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

1) `head -8 conn.log` — read `#fields` for THIS file. 2) `zeek-cut ts uid id.orig_h id.resp_h orig_bytes resp_bytes conn_state service` — the flow table. 3) Rank `orig_bytes` (payload!) desc. 4) Pivot `uid` into `http.log`/`ssl.log`/`dns.log`/`files.log` for content. 5) `missed_bytes`/`capture_loss.log` qualify every number. conn_state SF only for completed transfers.

## Evidence rule

Each stage quotes its own row. The final answer names: direction, unit
(wire vs payload), window, and the source artifact for every number.

## Pivot

Any stage dry three shapes -> `meth-budget` ordering; process questions ->
`dfir-execution-trace`.
