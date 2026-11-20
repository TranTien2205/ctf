# Format: crypto over a capture

Routing module for `crypto-triage`. The router maps one observable
to one named attack, its seconds-fast falsifier, one
`tools/crypto_attack.py` invocation, and one depth file. It never
derives the mathematics - `../ctf-crypto/` owns that.

TLS or a custom protocol in a pcap - the negotiation
parameters are the observable.

## Pivot

Attack confirmed -> the depth file; falsifier fired -> re-observe.
