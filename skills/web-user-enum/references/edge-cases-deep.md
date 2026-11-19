# Edge cases (deep) — the odd shapes, fully worked

## The case-only differential

`Admin` exists, `admin` does not — a case-sensitive lookup treats them
as different. The oracle leaks the CASE, not the existence. Probe the
case variants to map the normalization; record the exact-case name.

## The whitespace/normalization differential

` admin`/`admin `/`admin\t` — a trim-normalizing app treats them as one
account; a non-normalizing one does not. A `404` on ` admin` that
`admin` does not trigger reveals the trim behavior and the existence.

## The unicode/homoglyph differential

`admin` vs `dmin` (a Cyrillic ``) — a unicode-normalizing app treats
them as one; the homoglyph probes the normalization and may bypass a
blocklist or confirm the lookup is byte-exact.

## The multi-tenant differential

`user@tenantA` real, `user@tenantB` not — the oracle is tenant-scoped.
Carry the tenant field identically; the existence is (tenant,user), not
user.

## The pending/invited differential

An invited-but-unactivated account returns `"awaiting verification"`
or `"check your email"` — a distinct state that confirms the row exists
before it is usable. A state-aware oracle enumerates
active/pending/locked/deleted.

## The honeypot trap

A hidden `username`/`email`/`website` field — when filled, the app
silently accepts but ignores the request (a bot honeypot) or returns a
fake differential. Fill only the visible fields; a honeypot-shaped
response is a trap, not an oracle.

## The CAPTCHA-on-second-try differential

The first request is unguarded; the second triggers a CAPTCHA — the
CAPTCHA's APPEARANCE is itself a signal (the app distinguishes the
attempt count) and a partial oracle if it only appears for real users.

## The federated/SAML differential

`user@external-idp.com` vs `user@local.com` — a different
`SAMLRequest`/redirect for a federated vs a local account leaks which
directory holds the user.

## The disabled-account-as-oracle

`"account disabled"` on a real name vs `"invalid"` on a fake — a
disabled row is still a row; the distinct message confirms existence.
