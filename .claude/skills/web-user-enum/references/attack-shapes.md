# Attack shapes — the enumeration primitives, named

## Shape: the direct text oracle

`"no such user"` vs `"wrong password"`. The naive shape — one request
per candidate. Detect: `diff` the error text. Rare in production, common
in CTF.

## Shape: the code/class oracle

Same message, different `error_code`, CSS class, `data-`, hidden input,
comment, or JSON sub-field. Detect: noise-masked raw-byte diff.

## Shape: the redirect-parameter oracle

`302 /login?e=1` vs `?e=2`, `?error=user` vs `?error=pass`. Detect: read
`Location`, never follow.

## Shape: the status oracle

`404` vs `401`, `200` vs `302`, `422` vs `401`. Detect: `-w '%{http_code}'`.

## Shape: the timing oracle

`verify()` runs only for real users → a 50-300ms gap on memory-hard
hashes. Detect: N≥8 interleaved median delta.

## Shape: the side-artifact oracle

A `Set-Cookie`, an email/OTP sent, a lock set, an `attempts_remaining`
field, an audit row. Detect: the `-sv` envelope + the send side-effect.

## Shape: the direct-exists endpoint

`/check-username`, `/available`, `/user-exists`, `/api/users/{name}` →
`{"available":false}` / `200`/`404`. The unauthenticated direct oracle —
the cheapest when present.

## Shape: the register-taken oracle

`POST /register` → `"username already taken"` / a `409`. The form BUILT
to reveal availability.

## Shape: the reset-send oracle

`POST /forgot-password` → the send fires only for a real row, read via
timing, a `{"emails_sent"}` field, or the send itself.

## Shape: the lockout oracle

`423 "account locked"` after N on a real name, `"invalid"` forever on a
random name — the lock itself enumerates.

## Shape: the throttle findings

- **absent** — a 15-req burst, no 429/lock/delay
- **threshold** — `429`/`423` at N
- **bypassed** — `X-Forwarded-For`/session/endpoint/method reset

## The shape-to-channel map

Every shape resolves to one of the four channels — a shape is a
*pattern*, the channel is the *measurement*. The corpus's per-channel
files are the protocol; these are the named instances.
