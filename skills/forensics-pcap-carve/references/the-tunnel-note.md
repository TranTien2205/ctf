# The tunnel note — the DNS/ICMP pattern

## DNS tunnel

Query names chunked under one suffix domain — each label a chunk:

    pcap_parse cap dns                  # the query names
    dns_exfil --pcap cap.pcap           # strip suffix, join, decode

## ICMP tunnel

The ICMP payload carries bytes — field-carve the payload, join in
order.

## The tell

A high volume of queries/echoes to one endpoint with varying
names/payloads — the tunnel's shape.
