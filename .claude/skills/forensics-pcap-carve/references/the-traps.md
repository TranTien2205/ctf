# The traps

- `strings` the whole capture finds the easy flag, misses the split.
- Follow-stream is TCP-only — UDP/ICMP/DNS need field extraction.
- A 'data' protocol entry IS usually the interesting flow.
- A USB linktype isn't a network flow.
- Reassembly order matters — out-of-order packets need the index.

## More traps

- A retransmission duplicates bytes — dedup on reassembly or the
  flag reads doubled.
- A lost segment leaves a gap — a "garbled" flag may just be
  missing a packet.
- An exported object never opened is a lead, not a solve.
- A `strings` hit on the raw capture catches the flag's bytes but
  not the split flag's order — reassemble anyway.
- The 'data' protocol entry is where custom encodings hide — the
  dissector's failure is the signal.
- A USB/har file isn't a network flow — route by linktype/format
  before protocol-hierarchy work.
- A TLS/QUIC flow's payload is encrypted — the flag isn't in it;
  the metadata (SNI/cert) is.
- A "the flag is chunked" guess without the reassembly is a lead.
- pcapng blocks vs classic pcap — pcap_parse reads both; the
  format names which.
