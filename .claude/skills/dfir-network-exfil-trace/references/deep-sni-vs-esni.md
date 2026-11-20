# Deep: ECH/ESNI hidden SNI

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

Encrypted ClientHello hides the real SNI inside the outer CH — the outer SNI is then a cover name by design. `tls.handshake.extensions_server_name` shows the outer claim; the inner is unreachable. The consequence is 'SNI absent/implausible + real ip.dst' — report what each field said rather than 'no SNI'.

## Evidence rule

These fields corroborate — they sharpen or qualify a volume/direction
answer already grounded in the flow records; none of them is the answer
alone.

## Pivot

Detail settled -> back to the `q-*`/`scen-*` module driving the question.
