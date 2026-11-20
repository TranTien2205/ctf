# The field carve — one value per packet

A flag split one byte/field per packet — ttl, ipid, dport,
tcpflags, icmp, len — reassembled across the sequence. fields
--field splits them out.
