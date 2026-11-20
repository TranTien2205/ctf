# The checklist

- [ ] Hierarchy counted (io,phs / convs)
- [ ] Dominant protocol named
- [ ] Objects exported (http --out)
- [ ] Field-carves tried (ttl/ipid/dport/tcpflags/icmp/len)
- [ ] Streams followed
- [ ] DNS tunnel checked (dns_exfil)
- [ ] USB/har routed if that's the linktype/format
- [ ] strings on the raw capture
- [ ] The reassembled bytes carry the flag
- [ ] Flag through the hook

## Per-carrier quick checks

- [ ] Format named: classic pcap vs pcapng vs .har vs USB linktype
- [ ] `convs`/io,phs — the dominant protocol named
- [ ] A 'data' proto entry treated as the interesting flow, not noise
- [ ] Objects exported and each file read, not just listed
- [ ] Field-carves tried before a strings pass
- [ ] A DNS tunnel checked under one suffix domain
- [ ] Reassembly order checked: seq vs packet vs index
- [ ] Retransmissions deduplicated on the reassembly
- [ ] A lost/gapped segment noted, not silent
- [ ] The carved bytes decoded (hex/b32/b64/xor as needed)
- [ ] The flag verified inside the reassembled content
- [ ] Every dead channel recorded as a negative
