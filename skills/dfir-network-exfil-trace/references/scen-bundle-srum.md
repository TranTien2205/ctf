# Scenario: Bundle with SRUDB.dat

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

SRUM is the volume oracle when there is no capture: `BytesSent`/`BytesRecvd` per app per hour in the Network Data Usage table. Needs an ESE reader (esedbexport/libesedb — absent here; install route in dfir-sherlock-triage/toolchain.md). Resolve `AppId` through `SruDbIdMapTable` before naming the app; the raw index is never the answer. Timestamps are OLE Automation dates — `timeline_merge.py` tier handling or convert before joining.

## Evidence rule

Each stage quotes its own row. The final answer names: direction, unit
(wire vs payload), window, and the source artifact for every number.

## Pivot

Any stage dry three shapes -> `meth-budget` ordering; process questions ->
`dfir-execution-trace`.
