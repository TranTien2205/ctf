---
name: forensics-pcap-carve
description: >
  Action-oriented depth skill for Capture carving / protocol extraction. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: dfir-network-exfil-trace, misc-encoding-carrier.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [forensics, pcap-carve, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Capture carving / protocol extraction

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

protocol-hierarchy count first, then follow the protocol that dominates — the flag rides the busiest channel

**Falsifier** — the observation that closes this class: every exported object and followed stream is accounted for as normal traffic
## Recognise

A `.pcap`/`.pcapng` capture is the handout and the answer lives in the traffic:
a followed stream, an exported object, a protocol field, or data reassembled
across packets. The first question is which protocol carries it.

## Confirm safely

All reads are local. The flag usually sits inside one flow — quoting the
reassembled bytes verbatim is the evidence; a filter that merely LOOKS
interesting is a lead.

## Extraction order

0. No tshark on the box? `tools/forensics/pcap_parse.py` covers the same
   order with stdlib — classic pcap **and** pcapng (Wireshark's default
   save format): `convs` for the protocol-hierarchy answer, `dns`
   for the query-name carve, `ascii` for the strings pass, `follow N`
   for one stream per direction, `http --out objs/` for the
   export-objects equivalent — the most common flag carrier — and
   `fields cap.pcap --field ttl|ipid|dport|tcpflags|icmp|len` for the
   one-value-per-packet split-flag carriers (the `-T fields -e` trick).
   Its own output says where it is weaker than tshark (seq-overlap not
   verified).
1. `tshark -r cap -q -z io,phs` — the protocol hierarchy tells you which
   channel dominates; start there, not with a global strings run.
2. `--export-objects` for HTTP/SMB/TFTP — reassembled files are the most
   common flag carrier.
3. `tshark -Y <proto> -T fields -e <field>` for field-carved data: DNS labels,
   ICMP payload, TCP flags, packet lengths, timing.
4. `tshark -z follow,tcp,ascii,N` on the surviving flow; then `strings` the
   raw capture for anything the dissector missed.

`references/extraction-order.md` maps carrier shape -> commands per protocol.

## Traps

- `strings` on the whole capture finds the easy flag and misses the split
  one — a flag chunked one-byte-per-packet needs field reassembly, not grep.
- Follow-stream decodes TCP only; UDP/ICMP/DNS channels need field extraction.
- A "data" protocol entry in the hierarchy usually IS the interesting flow —
  dissectors fail on custom encodings, which is exactly where authors hide.

## Operational probe

```bash
tshark -r cap.pcap -q -z io,phs
tshark -r cap.pcap --export-objects http,./objs
tshark -r cap.pcap -Y dns -T fields -e dns.qry.name | sort -u | head
```

Queries that look like chunked data under one suffix domain are a DNS
tunnel — reassemble with `tools/forensics/dns_exfil.py --pcap cap.pcap`
(strips the suffix, joins labels in packet or index order, tries
hex/base32/base64). Also accepts `--names queries.txt`.

A USB capture (linktype 189/220, the `usb.capdata` staple) is not a
network flow at all — decode interrupt-in reports with
`python3 tools/forensics/usb_hid.py cap.pcap keys` for typed keystrokes
or `mouse` for pen-stroke points; `--raw hexlines.txt` works on
exported report hex too.

## Routing

Shares signals with: `../dfir-network-exfil-trace/`, `../misc-encoding-carrier/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/forensics-pcap-carve/references/README.md`
- `skills/forensics-pcap-carve/references/extraction-order.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
