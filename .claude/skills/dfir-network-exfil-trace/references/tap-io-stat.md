# Tap: -z io,stat,<secs>,<filter>

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## What it answers

Volume or count per fixed interval — the beacon rate and the burst pattern
without pandas.

## Commands

```bash
tshark -r capture.pcapng -q -z io,stat,60,"SUM(frame.len)frame.len and ip.src==10.10.10.5"
tshark -r capture.pcapng -q -z io,stat,1,"COUNT(dns.qry.name)dns.qry.name"
```

## The SUM filter trap — measured

`SUM(<field>)<filter>` silently returns 0 in every interval unless `<field>`
appears inside the filter string too. `SUM(frame.len)ip.src==10.10.10.5`
prints all zeros; `SUM(frame.len)frame.len and ip.src==10.10.10.5` works.
tshark(1) documents it; the silent-zero shape is measured here.

## Reading for beaconing

A near-constant per-interval count (e.g. `908, 908, 908`) is the periodicity
signature. Compare against the browsing baseline in the same capture — the
beacon's coefficient of variation sits an order of magnitude below organic
traffic.

## Evidence rule

Quote the interval column plus the interval width you chose. Changing
`<secs>` reshapes the answer; the quoted excerpt must carry the parameter.

## Pivot

Flat per-interval flow -> `beacon-*` modules for the cadence arithmetic.
