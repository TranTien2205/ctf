# Workflow: When tshark is absent

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`pcap_triage.py`/`pcap_parse.py` (stdlib) cover conversations, DNS list, stream follow, HTTP objects, per-packet fields. `scapy` PcapReader covers anything else in a script. The taps are convenience; every tap answer has a stdlib path — slower to type, identical evidence.

## Evidence rule

Workflow modules set order and scope; every number they lead to is still
quoted from the tool row that produced it.

## Pivot

`corpus-index` for the family list; `../SKILL.md` Discipline for the budget.
