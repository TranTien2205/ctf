# Class boundary - what SSRF is not

Depth module. Open `../SKILL.md` for the class contract first: first
probe, falsifier, confirm shape, traps. This file is one named piece of
the corpus - never a finding by itself.

SSRF is the SERVER issuing a request the caller chose - the
evidence is an internal response the client could not have reached.
It is NOT: an open redirect (the client follows; nothing internal is
read), a file-read primitive (no fetch - the parameter reaches a
filesystem call directly), or a blind callback (a DNS/HTTP hit on
your listener proves the fetch happened, but the RESPONSE was not
returned - that is blind SSRF, graded differently).

## Evidence chain

1. The parameter reaches a fetcher: internal-IP request returns a
   DIFFERENT response than an external one.
2. Scheme surface: file://, gopher://, dict:// tested one at a time -
   which schemes the fetcher resolves is its capability boundary.
3. Response channel: full-read vs blind (callback only) vs
   error-oracle (status differences) - names which exploit tier
   applies.

## Pivot

Boundary applies -> file-read-primitives (direct file access) or
web-open-redirect (client-side follow).
