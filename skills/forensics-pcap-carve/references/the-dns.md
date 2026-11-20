# DNS — the query-name tunnel

Query names chunked under one suffix domain = a DNS tunnel —
dns_exfil.py strips the suffix, joins labels in packet/index order,
tries hex/base32/base64.
