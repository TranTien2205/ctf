# Evasion — when the app resists the measurement

## The defenses you will meet

### Uniform response (a real defense)

The app returns `"Invalid username or password"` for both arms AND burns
a dummy hash to equalize timing. The honest defense — hunt the residual:
a side-artifact, a variance difference, a second form (register/reset
usually still leaks).

### Rate limiting / lockout / CAPTCHA

The loop-blocker. Measure it (bounded burst), record the threshold, then
`rate-limit-bypass.md` — an `X-Forwarded-For` reset, a fresh session, an
endpoint/method/param rotation. A real (non-bypassable) limit means the
enum loop is bounded; a slow spray under the threshold still works.

### Generic error pages / error swallowing

A catch-all error handler returns `"Something went wrong"` for every
failure — including a crash on the bad-user path. The uniform error may
hide a per-user crash (still a differential); re-send the exact request
and check the status/timing channels.

### Request normalization / WAF

A WAF blocks the enumeration pattern — a rate-of-requests block, a
signature on the `user` field, a CAPTCHA interstitial. Slow the loop,
rotate the param name, use the `web-triage` evasion surface — but the
goal stays a bounded measurement, not a bypassed-wall spray.

### Response padding / normalization

The app pads both arms to the same length or returns a fixed-size error
— the body-length channel is closed; the text/status/timing channels may
still differ.

## The evasion-order rule

When the content channels are equalized:
1. the side-artifact envelope (cookie/header/JSON-field)
2. the timing channel (variance, not just median)
3. a second form (register/reset/check-username)
4. a send side-effect (the email/OTP)
5. accept the closure — a fully-equalized app is a real negative

## What NOT to evade into

- a mass spray under the throttle — it is still a spray
- a lock-bypass that unlocks a victim account you do not own
- a WAF-bypass that turns a measurement into an abuse run

The evasion serves the MEASUREMENT, not an unbounded guess loop.
