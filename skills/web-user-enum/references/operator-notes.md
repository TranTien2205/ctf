# Operator notes — the field-tested lessons

## The bundle names the cheapest oracle

The `check-username`/`available`/`user-exists` endpoint is usually an
AJAX call in the register page's JS — not a visible link. `web-source-map`
recovers it; grep the bundle for `check|available|exists|username`. One
request to it confirms the whole class.

## The register leaks before the login

The signup form is BUILT to tell a user a name is taken — that check is
the oracle, structural not accidental. A hardened login coexists with a
leaky register in nearly every real app. Probe register/reset/check
first.

## A uniform message is not a clean endpoint

`"invalid credentials"` equalizes ONE channel. The timing (the bcrypt
gap), the envelope (a cookie/header), the send (the email), the lock —
the others almost always remain. A uniform message is a defense, not a
closure.

## Timing needs a real baseline

One `curl -w '%{time_total}'` is noise — jitter is 10-50ms. N>=8
interleaved samples, medians not means, session-pinned, a jitter
baseline. A bcrypt gap (100-300ms) is easy; a PBKDF2 50k (10-40ms)
needs the baseline.

## A `500`/crash is still a differential

A `user.hash`-on-`None` crash is a repeatable, user-dependent branch —
it leaks `exists` coarsely. Re-send the exact request; if the `500`
repeats only on bad users, it is a noisy oracle — record it.

## The lock is the oracle, not the dead end

A `423 "locked"` on a real name vs `"invalid"` on a fake IS the
exists-oracle — the lock only writes to a real row. Do not discard it
as "the control won"; record `locks at N` + the confirmed name. But
never lock a victim's account — use your own.

## A `429`-reset is the finding

An `X-Forwarded-For`/`fresh-session` that resets a `429` means the
counter trusts attacker input — the bypass IS the reportable weakness,
not a license to spray. Record the reset; do not run the spray.

## Coverage, not the headline

The single most common miss: probing only `/login` and calling the app
"clean". check-username/register/reset/api/graphql leak first. The
coverage matrix is `per-form × per-channel`; a `/login`-only read is
one cell.

## The enum is a measurement, not the exploit

The class produces a verified account name + a throttle finding — the
chain moves to `web-auth-session`/`web-idor`/etc. A confirmed name is
the output; the spray is the neighbor's budget, not this class's.
