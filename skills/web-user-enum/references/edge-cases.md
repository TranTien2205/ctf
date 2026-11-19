# Edge cases — the odd shapes that still leak or fool

## The "uniform" that is not

- identical body, identical status — but a `Set-Cookie` on one arm, a
  `data-` attribute, a hidden `<input>`, a `<!-- -->` comment, a JSON
  sub-field. Diff the raw bytes + the full envelope, not the page.
- identical render — but the error block's CSS class / `aria-*` differs
- a generic "Something went wrong" — an app crash on one arm is a
  differential too (the crash path is user-dependent)

## Timing edge cases

- a load-balanced app — requests hit different workers; pin a session
  cookie for affinity
- a cached response — a warm cache makes both arms fast; send distinct
  requests (vary a throwaway param) to bust it
- a weak hash (sha256) — a real but sub-jitter delta; not a usable oracle
- a time-equalized app that still leaks variance — the bad arm's fixed
  dummy-hash has lower variance than the good arm's per-user hash

## Account-state edge cases

- a locked/disabled/unverified account returns a DIFFERENT response than
  an active one — `"account disabled"` vs `"invalid"` is still a
  exists-oracle (a real row carries the state)
- a pending/invited account — `"awaiting verification"` reveals existence
- a deleted/banned account — `"account removed"` reveals it existed

## The honeypot / decoy field

A hidden `username`/`email`/`honeypot` field that, when filled, marks the
request as bot — the app may return a fake differential to waste
enumerator time, or silently ignore. Fill ONLY the visible fields.

## The CSRF-token confounder

A per-request CSRF token makes the pair unpaired — re-fetch a fresh
token for EACH request, or the token difference fakes a differential.
A token that is required-but-missing returns a `403` that looks like a
differential but is a form error.

## The multi-tenant edge

`user@tenantA` exists, `user@tenantB` does not — the oracle is
tenant-scoped; the username alone is not the discriminator. Carry the
tenant field identically on both arms.

## The case-sensitivity edge

`Admin` vs `admin` — a case-insensitive lookup treats them as one
account; a case-sensitive one does not. Probe the case variant to map
the normalization.
