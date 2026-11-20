# Method: Budget and pivot

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`stuck_threshold: 3`, `on_stuck: pivot` (frontmatter). In practice: three filter shapes per artifact family, then move — pcap taps -> Sysmon -> SRUM/firewall -> Zeek/Suricata -> Linux logs. The five-probe class budget in decide.py counts across families.

## Why this order

Cheapest reliable measurement first; every stage emits a recordable row.
Skipping ranking to go straight to payload carving is how sessions spend
the budget on the wrong peer.

## Pivot

Next unmeasured family per `../SKILL.md` Discipline; escalate per
`tools/decide.py` when every family is dry.
