# Channel: DoH / DoT concealment

Depth module for `dfir-network-exfil-trace`. Open `../SKILL.md` for the
class contract first: first probe, falsifier, confirm shape, traps. This file
is one named piece of the corpus — never a finding by itself.

## Detection

DoT = port 853 (TLS'd DNS wire format). DoH = HTTPS to a resolver — indistinguishable from web traffic except by `ip.dst`/SNI to a known resolver (cloudflare-dns.com, dns.google, mozilla.cloudflare-dns.net). The ABSENCE of UDP/53 while the host clearly resolves names is the secondary tell.

## Evidence rule

Name the channel from a measured protocol (`io,phs` leaf, `conv,*` row,
field presence) — never from the port number alone. Quote the row or filter
result that demonstrated it.

## Pivot

Channel confirmed -> the matching `q-*` module for the question. Channel
shape absent after three filter shapes -> next channel or next artifact
family.
