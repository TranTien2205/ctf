# Deep: TLS record-layer reading

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

`tls.record.length` per record (16K max); app-data records vs handshake records are distinguishable. Summing app-data records outbound approximates plaintext volume minus per-record overhead — the closest honest figure without decryption.

## Evidence rule

These fields corroborate — they sharpen or qualify a volume/direction
answer already grounded in the flow records; none of them is the answer
alone.

## Pivot

Detail settled -> back to the `q-*`/`scen-*` module driving the question.
