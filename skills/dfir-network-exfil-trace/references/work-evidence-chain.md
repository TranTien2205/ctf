# Workflow: The evidence chain for one answer

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Worked example end to end: question 'how much left to 185.199.0.7'. 1) `endpoints,ip` row names the host's Tx total. 2) `conv,tcp` row names the peer share and direction pairs. 3) `tcp.len` sum per stream gives payload-accurate figure. 4) `frame.time_epoch` min/max on the stream bounds the window. 5) the report line: 'Between T0 and T1, 9,080 wire bytes (x payload) host->185.199.0.7 over stream N' with rows quoted. Each number traced to a printed row — the chain is the unit of the class.

## Evidence rule

Workflow modules set order and scope; every number they lead to is still
quoted from the tool row that produced it.

## Pivot

`corpus-index` for the family list; `../SKILL.md` Discipline for the budget.
