# Error — NXDOMAIN

NXDOMAIN = the name doesn't exist — vs an empty answer (NODATA)
= the name exists but not that type. The distinction matters for
subdomain hunting.

## Reading it

- NXDOMAIN → the hostname isn't registered — not a sibling.
- NODATA → the host exists but no TXT (say) — try another type.
- An answer → the host is real — the candidate.
An NODATA host is still a lead — it exists.
