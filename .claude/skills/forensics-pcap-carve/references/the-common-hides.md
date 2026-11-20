# The common hides — where authors put it

## Ranked by frequency

1. An exported HTTP/SMB/TFTP object — the transferred file.
2. A followed TCP stream — the cleartext conversation.
3. A DNS tunnel — chunked query names under one suffix.
4. A field-carve — TTL/IPID/dport/tcpflags/ICMP-payload/len.
5. A UDP/ICMP payload — the datagram bytes.
6. The 'data' protocol — a custom encoding the dissector missed.
7. A credential field — FTP PASS, HTTP auth, SMTP body.
8. A USB/har artifact — the not-network carrier.
9. An RTP audio channel — DTMF/spectrogram after extraction.
10. Timing/sequence — inter-arrival or seq-number encoding.

## The rule

Work the dominant protocol's cheap channel first — objects, then
fields, then streams, then tunnels — and record each negative.
