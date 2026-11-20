# Worked — an ICMP split flag

A capture is mostly ICMP echo — no objects, no streams.

## 1. Hierarchy

    pcap_parse cap convs   → icmp dominates

## 2. The field

The ICMP payload byte per packet — one byte per echo:

    pcap_parse cap fields --field icmp

## 3. Reassemble

The per-packet payload bytes join in packet order to the flag.

## 4. Verify

The reassembled string IS the flag — through the hook.

## The shape named

`shape-one-byte-per` + `fld-icmp` — the one-value-per-packet
carrier on the ICMP payload.
