# The pcap-carve workflow — protocol-hierarchy first

A .pcap/.pcapng is the handout; the flag lives in the traffic — a
followed stream, an exported object, a protocol field, or data
reassembled across packets.

## The order

0. `tshark -r cap -q -z io,phs` or
   `python3 tools/forensics/pcap_parse.py cap.pcap convs` — the
   protocol hierarchy says which channel dominates; start there.
1. `--export-objects http` or `pcap_parse.py cap http --out objs/` —
   reassembled files are the commonest flag carrier.
2. Field-carve: `tshark -Y <proto> -T fields -e <field>` or
   `pcap_parse cap fields --field ttl|ipid|dport|tcpflags|icmp|len` —
   the one-value-per-packet split-flag carriers.
3. `pcap_parse cap follow N` or `tshark -z follow,tcp,ascii,N` —
   the surviving flow's reassembled bytes.
4. `strings` the raw capture for what the dissector missed.

## The rule

Evidence = the reassembled bytes quoted verbatim — a filter that
looks interesting is a lead, not evidence.

## Per-carrier detail

- **Hierarchy.** `tshark -q -z io,phs` or `pcap_parse cap convs` —
  the dominant protocol and the 'data' flow name where to dig.
- **Objects.** `--export-objects http,smb,tftp` or
  `pcap_parse cap http --out objs/` — reassembled files.
- **Fields.** `pcap_parse cap fields --field X` or
  `tshark -Y p -T fields -e f` — ttl/ipid/dport/tcpflags/icmp/len,
  one value per packet.
- **Streams.** `pcap_parse cap follow N` or `follow,tcp,ascii,N` —
  the reassembled flow.
- **Tunnels.** `dns_exfil --pcap` strips the suffix, joins labels,
  tries hex/base32/base64.
- **USB.** linktype 189/220 → usb_hid keys/mouse — not a network
  flow.
- **Media.** RTP streams → rtp_extract → WAV → dtmf/spectrogram.
- **.har.** JSON not a pcap — har_dump inventories it.
- **Raw pass.** `strings` on the whole capture for what the
  dissector missed.

## The stop

The reassembled bytes carrying the flag, verified through the hook.
