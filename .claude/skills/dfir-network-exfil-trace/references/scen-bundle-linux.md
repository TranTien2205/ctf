# Scenario: Bundle is Linux logs

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

iptables `LOG`/`AUDIT` lines in syslog/kern.log: `SRC= DST= LEN= PROTO= SPT= DPT=` — sum `LEN` per `DST`. journald `journalctl --file <dir> -o short-iso-precise` keeps ISO timestamps for merging. Captured `ss -tunap`/`netstat -anp` = point-in-time only. auth.log/wtmp belong to `dfir-authentication-trace`.

## Evidence rule

Each stage quotes its own row. The final answer names: direction, unit
(wire vs payload), window, and the source artifact for every number.

## Pivot

Any stage dry three shapes -> `meth-budget` ordering; process questions ->
`dfir-execution-trace`.
