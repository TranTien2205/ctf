# Channel: DNS exfil inside query names

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Detection

The classic carrier: payload hex/base32/base64-encoded into labels under an attacker-controlled zone. Detection stack: `dns.qry.name.len > 50`, `dns,tree` Label Stats `4th Level or more`, parent-domain histogram showing ONE suffix owning most queries, alphabet regex `matches "^[0-9a-f]{16,}[.]"` for hex (use `[.]` not `\.` — tshark 4.0.7 rejects the latter). Reassembly: `tools/forensics/dns_exfil.py --pcap cap` handles label decode + retransmission de-dup. The per-chunk header shape and last-byte-of-name variants are in `skills/ctf-forensics/network-advanced.md:423-457` and `:111-181` — working code, do not restate it.

## Evidence rule

Name the channel from a measured protocol (`io,phs` leaf, `conv,*` row,
field presence) — never from the port number alone. Quote the row or filter
result that demonstrated it.

## Pivot

Channel confirmed -> the matching `q-*` module for the question. Channel
shape absent after three filter shapes -> next channel or next artifact
family.
