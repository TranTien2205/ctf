# Summary (deep) — the class, completely

## The core

An auth endpoint's response is a function of whether the account exists
— on the text, the status, the redirect, the timing, the cookies, the
send, the lock. Equalizing all of them is the (rare) defense; missing
one is the bug. The class also covers the dual: is the guessing loop
bounded (the throttle) or bypassable?

## The mechanism set

- **text/code** — the error names account-vs-password; a code/class/
  field differs
- **status/redirect** — a code or `Location` parameter differs
- **timing** — `verify()` runs only for real users
- **variance** — a fixed dummy-hash has lower stdev
- **side-artifact** — a cookie, a send, a lock, a JSON field
- **direct** — a check-exists endpoint's boolean
- **register/reset/unlock/mfa/invite** — the per-form leaks
- **throttle** — absent / threshold / bypassed

## The protocol

1. known-good vs known-bad vs repeated-bad, other fields constant
2. noise-baseline (`bad1`==`bad2`), then masked diff on every channel
3. confirm: a second bad name + a re-run tracks the username-class
4. the bounded burst (8-15) for the throttle
5. a bounded candidate list on a scoped target → the verified names
6. record verbatim per (form × channel); route the names; record negatives

## The four rules

- a differential is a **repeated, channel-identified** delta
- mask per-request noise before diffing
- **never spray** — the oracle is 3 requests; the list is bounded/scoped
- a lock/crash/state-message is still an oracle — record it

## The route

A confirmed name → `web-auth-session` (spray/reset/MFA) / `web-idor`
(the object) / `web-logic-flaw` (reset-flow) / `web-oauth-sso` (email
collision). A no-throttle/bypass → `web-auth-session`'s credential loop.

## The honest status

**Catalogue** — no local solve. `../../field-notes.md` accumulates real
measurements; a confirmed chain-solve promotes the class.
