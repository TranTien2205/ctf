# Reverse DNS — the PTR detail

For IP a.b.c.d, query `d.c.b.a.in-addr.arpa` PTR (IPv6: ip6.arpa
nibble-reversed). A PTR names the host; cross-check with a forward
query.

## Reading it

- A descriptive PTR (`mail.example.com`) names the host's role.
- A generic provider PTR gives little — then it's just a provider.
- Forward-confirm: the PTR's name should resolve back to the IP.
