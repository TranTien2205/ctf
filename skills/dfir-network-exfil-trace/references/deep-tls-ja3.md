# Deep: JA3/JA3S fingerprints

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

JA3 hashes the client's offer (version, ciphers, extensions, curves, point formats) — a tooling fingerprint: a python-requests or custom TLS client's JA3 differs from a browser's. In tshark: `tls.handshake.ja3` where the build exposes it; in Zeek `ssl.log` ja3 column; Suricata `tls.ja3`. A match to a known-tool JA3 is a lead, still not a finding alone.

## Evidence rule

These fields corroborate — they sharpen or qualify a volume/direction
answer already grounded in the flow records; none of them is the answer
alone.

## Pivot

Detail settled -> back to the `q-*`/`scen-*` module driving the question.
