# Worked — a TTL-field flag

A TCP flow's payload is normal — the flag rides the TTL.

## 1. Hierarchy

convs → tcp dominates; the followed stream is benign.

## 2. The field

Each packet's TTL differs — a byte-per-packet carrier:

    pcap_parse cap fields --field ttl

## 3. Reassemble

The TTL sequence in packet order decodes to the flag.

## 4. Verify

The decoded bytes → the flag → the hook.

## The shape named

`shape-one-field-per` + `fld-ttl` — the IP-header field carrier.
