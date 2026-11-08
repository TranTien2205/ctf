# Enumeration differentials

The enumeration oracle is whatever differs between a real account and a fake
one, measured on the SAME form with the SAME other fields.

## Channels, cheapest first

1. **Body text.** Diff the raw bodies — renderers hide whitespace, hidden
   inputs, `data-*` attributes, JS booleans. A uniform "invalid credentials"
   message still leaks if the success/error block differs by a byte.
2. **Status and redirect.** 200 vs 302 vs 401, or a different Location on the
   two arms. Login responses that redirect to `/login?e=1` vs `/login?e=2` are
   enumerated by the parameter, not the page.
3. **Timing.** Password hashing runs only when the user exists. Baseline both
   arms alternately (good, bad, good, bad) — medians of 8+ samples, not one
   shot. A bcrypt round count makes real users ~50-300ms slower.
4. **Side artifacts.** Set-Cookie differences, a "reset sent" that only fires
   for real accounts, a register form that rejects taken usernames (the
   registration path often leaks what login does not).

## Throttling as the finding

Absence of rate limiting is reportable on its own, but prove absence, not
just non-observation:

- A bounded burst (8-15 requests) with no 429, no CAPTCHA, no growing delay is
  the signal — stop there; more is a brute-force run, not a measurement.
- A locked account is evidence FOR the control. If the account locks at N,
  record N as the threshold; the finding is about what happens before it.
- Check where the limit lives: per-IP, per-account, per-session. Rotating one
  parameter (source IP header is common: `X-Forwarded-For`) sometimes resets
  the counter — that bypass IS the finding.

## Traps

- An app-level error page (`"Something went wrong"`) on the bad user can be a
  crash, not a differential — re-send the exact bad request once to confirm it
  repeats.
- Timing oracles break under load balancing: requests may hit different
  workers. Alternate good/bad in the same session to keep affinity.
