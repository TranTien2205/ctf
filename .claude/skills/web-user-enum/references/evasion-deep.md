# Evasion (deep) — the resistant-target playbook

## Defense: a fully-equalized response

The app returns identical text+status+timing+cookies — the honest
defense. The residual hunt order:

1. **the variance** — a fixed dummy-hash has lower stdev than a per-user
   real hash; `stdev(good)` vs `stdev(bad)` may still differ
2. **a second form** — register/reset/check-username/mfa/api leak where
   the login is hardened
3. **the send side-effect** — the email/OTP fires only for a real row
4. **an account-state message** — locked/pending/disabled leaks existence
5. **the lock itself** — a `423` on a real name
6. **accept the closure** — a truly-equalized app is a real negative

## Defense: a hard rate limit

A per-IP/per-account limit that blocks the loop. The bypass order:

1. `X-Forwarded-For`/`X-Real-IP`/`X-Client-IP`/`CF-Connecting-IP`/
   `True-Client-IP`/`Forwarded` — a spoofed source resets a per-IP counter
2. a fresh session/cookie per request — resets a per-session counter
3. endpoint rotation — `/api/login`, `/api/v1/login`, `/auth`, `/token`,
   `/login/`, `/LOGIN` — an aliased, un-limited route
4. method/param rotation — `GET` vs `POST`, form vs JSON
5. username rotation — password-spraying pattern, stays under a
   per-account lock
6. a slow spray under a per-second/per-minute window — the window is
   the measured limit, not a block

The bypass IS the finding — a counter that trusts attacker input
(`X-Forwarded-For`) is broken.

## Defense: a CAPTCHA

A CAPTCHA interstitial after N. The signals: the CAPTCHA's appearance
is a throttle measurement; the content oracle may still fire within the
pre-CAPTCHA window. A CAPTCHA on the register/reset but not the
check-username leaves the direct oracle open.

## Defense: request normalization

A WAF that strips the `user` field, blocks a payload shape, or rate-limits
by request pattern — slow the loop, vary the vector, use a different
surface. The goal stays a bounded measurement, not a wall-bypass spray.

## Defense: a honeypot

A hidden field that, when filled, flags the request — fill only the
visible fields. A honeypot-shaped response is a trap; its response is
not an oracle.

## What NOT to evade into

- a mass spray under a bypassed limit — it is still a spray
- a lock-bypass that unlocks a victim's account
- a WAF-bypass that turns a 3-request measurement into a 10k-request run

The evasion serves the MEASUREMENT.
