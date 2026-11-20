# Worked — a DNS tunnel

1. convs → dns dominates.
2. Query names like aAbB.sub.evil.com — chunked.
3. dns_exfil.py --pcap → strips suffix, joins, decodes → flag.
