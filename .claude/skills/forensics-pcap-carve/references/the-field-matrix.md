# The field matrix — every one-value-per-packet carrier

## The fields worth splitting

- `ttl` — IP time-to-live, a byte per packet.
- `ipid` / `ip.id` — the IP identification, 16 bits.
- `dport` / `sport` — the ports, 16 bits.
- `tcpflags` — the flag bits, a bit-carrier.
- `icmp` — the ICMP payload byte.
- `len` / `frame.len` — the packet length.
- `ts` / `frame.time_delta` — timing deltas.
- `seq` / `ack` — the TCP counters.
- `winsize` — the TCP window.
- `ip.tos` — the ToS/DSCP byte.
- `vlan.id` — the VLAN tag.
- `icmp.seq` — the echo sequence.

## The carve

    pcap_parse cap fields --field ttl
    tshark -r cap -Y ip -T fields -e ip.ttl

The per-packet values join in packet order — decode (hex/b32/b64)
if needed.
