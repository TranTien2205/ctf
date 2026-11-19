# Common questions — the operator FAQ

## "Isn't a uniform 'invalid credentials' always safe?"

No — a uniform message equalizes ONE channel (text). The timing (hash
asymmetry), the side-artifacts (a cookie, an email, a lock), and the
OTHER forms (register/reset/check-username) usually still leak. A uniform
message is a defense, not a guarantee.

## "How many timing samples do I need?"

N≥8 per arm, interleaved good/bad, compare medians. A single shot is
noise (10-50ms jitter). A bcrypt gap (100-300ms) needs fewer; a PBKDF2
50k gap (10-40ms) needs more and a jitter baseline.

## "Can I just spray a username list?"

Not on a shared/victim target — that is the brute-force run the throttle
stops. The ORACLE is proven with known-good + known-bad + repeated-bad
(3 requests). The LIST is bounded, on an owned/lab/scoped target, and
bounded by the throttle measurement. Never spray to "test".

## "The account locked — dead end?"

No — a `423 "account locked"` on a real name vs `"invalid"` on a random
name IS an exists-oracle (the lock only fires on a real row). Record
`locks at N` + the confirmed account. Just do not burn a victim's account
to prove it — use your own known-good.

## "Both arms are 200 with identical JSON — closed?"

Only if ALL four channels are uniform: body (masked), status, timing
(N≥8 median), AND the envelope (cookies, headers, JSON sub-fields,
the send side-effect). A uniform body does not close a timing or
cookie oracle.

## "The bad user gets 'server error' — a differential?"

Maybe — a per-user crash IS a differential (the code path is
user-dependent). Re-send the exact bad request; if the `500` repeats
only on bad users, it is a real (if noisy) oracle. If it is a one-off,
it is a crash, not a channel.

## "Does rate limiting close the class?"

It bounds the loop but is the class's SECOND finding — a limit at N is
itself reportable, and a bypass (`X-Forwarded-For`, fresh session,
endpoint rotation) reopens it. The throttle measurement is part of the
class, not a stop.

## "What is the cheapest oracle to try first?"

`GET /api/username-available?u=` or `/check-username` — a direct
exists-boolean, unauthenticated, no credential. If it exists, the class
is confirmed in one request.
