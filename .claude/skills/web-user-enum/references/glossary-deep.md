# Glossary (deep) — the terms, defined precisely

## The measurement terms

- **enumeration oracle** — a channel `C` where `C(f(known_good)) !=
  C(f(known_bad))` repeatedly; the `exists` bit read through `C`
- **the three arms** — `R(KNOWN, *)` / `R(FAKE, *)` / `R(FAKE, *)` —
  good, bad, repeated-bad; the last is the noise baseline
- **noise mask** — `mask(r)` removing per-request-varying fields so
  `bad1==bad2` after masking
- **differential** — `masked(good) != masked(bad)` on a channel;
  the residual after masking
- **median delta** — `median(good_times) - median(bad_times)`, the
  timing signal
- **jitter / noise floor** — `stdev(pooled_times)`; the floor a delta
  must exceed (~3x) to count
- **session affinity** — pinning requests to one worker (a cookie) for
  a comparable timing read

## The channel terms

- **text oracle** — the error body names the failing field
- **code oracle** — a `error_code`/CSS-class/`data-`/JSON-field differs
- **status oracle** — the HTTP code differs
- **redirect oracle** — the `Location` parameter differs
- **timing oracle** — the hash-work gap
- **variance oracle** — a fixed dummy-hash's lower stdev
- **cookie oracle** — a `Set-Cookie` on one arm
- **send oracle** — the email/OTP fires only for real
- **lock oracle** — `423` only on a real row
- **direct oracle** — a check-exists endpoint's boolean

## The throttle terms

- **throttle** — the bound on the guessing loop: rate-limit, lockout,
  CAPTCHA, progressive delay, IP ban
- **rate limit** — `N per T` per IP/session/account
- **lockout** — an account freeze at N; itself an exists-oracle
- **per-IP / per-account / per-session / per-endpoint** — the counter's key
- **throttle bypass** — a reset of the counter (XFF, fresh session, alias)
- **password spray** — one password across many accounts, under the lock
- **credential stuffing** — leaked pairs replayed
- **the window** — a per-T limit that bounds but does not block

## The account-state terms

- **active / locked / pending / invited / disabled / deleted** — the
  states a real row can carry; each a distinct response
- **pre-hijack** — registering the victim's email first / SSO auto-link
- **homoglyph** — a unicode look-alike probing normalization
- **multi-tenant** — existence is (tenant, user), not user

## The discipline terms

- **cell** — a (form × channel) measurement unit
- **a measured negative** — a cell proven uniform, not "didn't check"
- **a bounded burst** — 8-15 requests; the throttle measurement
- **verbatim excerpt** — the response bytes, quoted, not paraphrased
- **catalogue** — no local verified solve
