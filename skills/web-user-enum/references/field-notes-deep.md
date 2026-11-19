# Field notes (deep) — the recorded patterns and what they mean

## What a solved enum challenge looks like

The pattern across the local and published cases:

1. the bundle/recon names a `check-username`/REST `users` endpoint —
   a direct oracle recovered before any probe
2. or the login's `verify()` short-circuit produces a bcrypt-timing gap
   that a masked content-diff cannot find but a 10-sample median can
3. or the register's `"taken"` leaks on a hardened-login app — the
   build-to-reveal check is the structural oracle
4. or the reset's send-side queues only for a real row — a `{"emails"}`
   field or the actual send
5. or the lockout writes only to a real row — a `423` on the real arm

The common thread: a uniform MESSAGE is the defense's goal; the other
channels are the defense's blind spots. The pass measures all of them.

## The field-tested truths

- **the bundle names the cheapest oracle** — `web-source-map` recovers
  the `check-username`/`available` AJAX call the register page makes;
  one request to it confirms the class
- **register/reset/check leak first** — a hardened login coexists with
  a leaky register in nearly every app; probe the secondary forms
  before concluding the class is closed
- **a uniform message is one channel** — the timing/envelope/send/lock
  almost always remain; a uniform text is a defense, not a closure
- **timing needs a real baseline** — jitter is 10-50ms; a single
  request is noise. N>=8 interleaved medians, session-pinned, a jitter
  baseline. A bcrypt gap (100-300ms) is easy; PBKDF2 50k (10-40ms)
  needs the baseline
- **a `500`/crash is a differential** — a `user.hash`-on-`None` crash
  is a repeatable, user-dependent branch — a noisy oracle, record it
- **the lock is the oracle** — a `423` on real vs `"invalid"` on fake
  IS the exists-oracle; record `locks at N` + the name, never spray
- **a `429`-reset is the finding** — an `X-Forwarded-For`/fresh-session
  that clears `429` means the counter trusts attacker input; record
  the reset, not the spray
- **coverage, not the headline** — a `/login`-only read is one cell;
  check-username/register/reset/api/graphql leak first
- **the enum is a measurement, not the exploit** — the class produces a
  verified name + a throttle finding; the chain moves to the neighbor

## The recorded failures

- a uniform-login app called "clean" — the register leaked; the
  coverage matrix caught it on re-pass
- a timing call on a single request — jitter; re-measured N=12 medians
- a `429` treated as "the control won" — an XFF reset was the finding
- a seeded list that missed — the bundle's `currentUser` fixture named
  the real account
- a `404` on `admin@x.c` read as a fake-user — a FORMAT error; the
  `admin` (no-at) form was the live slot
