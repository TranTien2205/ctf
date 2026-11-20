# NS — the operators

The authoritative nameservers name the DNS operator — and give
the AXFR targets; a custom NS hostname can itself be a sibling.

## Reading it

- `ns1.cloudflare.com` — the provider.
- `ns1.<the-domain>` — self-hosted, a sibling to query.
- Each NS is an AXFR target — try each.
