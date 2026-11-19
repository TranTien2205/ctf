# Glossary — the terms

- **enumeration oracle** — a channel that differs between a real and a
  fake account on the same endpoint
- **known-good / known-bad / repeated-bad** — the three request arms: a
  real account, a provably-fake name, and the fake again for a noise
  baseline
- **differential** — a measurable difference between the two arms on one
  channel
- **channel** — one of body / status+redirect / timing / side-artifact
- **timing oracle** — the hash-work asymmetry (hash runs only for real
  users) read as a response-time delta
- **noise mask** — removing per-request-varying fields (CSRF, timestamp,
  request-id) before the diff
- **median delta** — the timing difference computed on medians, not means
- **jitter / noise floor** — the transport variance a real delta must
  exceed (~3x) to count as signal
- **throttle** — a bound on the guessing loop: rate limit, lockout,
  CAPTCHA, progressive delay, IP ban
- **lockout** — an account freeze after N failed attempts; itself an
  exists-oracle (only a real row locks)
- **rate-limit bypass** — a reset of the counter: `X-Forwarded-For`, a
  fresh session, an endpoint/method/param rotation
- **password spray** — one common password across many accounts, staying
  under a per-account lockout
- **credential stuffing** — leaked username:password pairs replayed
- **check-username / availability endpoint** — a direct exists-oracle,
  usually unauthenticated
- **the send side-effect** — an email/OTP that fires only for a real row
- **pre-hijack** — registering a victim's email before they do / an SSO
  auto-link on an email match
- **account state** — active/locked/pending/disabled/deleted; each may
  leak existence through a distinct response
- **session affinity** — pinning requests to one worker (a cookie) so
  timing is comparable
- **catalogue** — no local verified solve; standard knowledge, not
  experience
