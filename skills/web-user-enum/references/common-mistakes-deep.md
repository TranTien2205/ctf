# Common mistakes (deep) — the subtle failures

## Reading the differential backwards

`good` shows `"invalid credentials"`, `bad` shows `"no such user"` — the
REAL account gets the uniform message, the FAKE gets the verbose one.
Read the direction: which arm is verbose tells you which check runs
first. A backwards read inverts the oracle.

## A CSRF token that changes the pair

The pair is unpaired when the CSRF token differs — the `403`/`error`
comes from the missing token, not the username. Re-fetch a fresh token
per request and hold the format constant; a token failure is not a
differential.

## Confusing a crash with an oracle

`500` on the bad-user path is a crash — the code path is user-dependent
but the response is a stack-trace/500, not a clean exists-vs-not. A
repeatable user-dependent crash IS still a differential (it leaks the
branch), but it is a noisier, coarser oracle — record it as such.

## A load-balanced timing read

Requests round-robin across workers with different speeds — the median
is a mix of workers, not a clean good-vs-bad gap. Pin a session cookie
for affinity, or measure the per-worker variance; a worker-mixed delta
is unmeasurable.

## A cached response

A CDN/edge-cached login response makes both arms fast and identical —
the timing oracle is busted. Vary a throwaway param (`&_=rand`) to bust
the cache, or the cache invalidates the measurement.

## A session-carryover

A logged-in session cookie on the `good` arm but not the `bad` arm
confounds the diff — the session itself changes the response. Send both
arms with the same (fresh) session state.

## The "one form clean = app clean" mistake

A fully-uniform `/login` is one cell — register/reset/check-username/
api/graphql are unmeasured. The most-common real bug is a hardened
login + a leaky register or a direct check endpoint.

## Recording "didn't see a 429" as "no throttle"

Absence is a BOUNDED measurement — 8-15 requests, no 429/captcha/lock/
delay, recorded with the count. A few casual probes are not the
measurement.

## The pre-hijack misroute

An email-collision (register the victim's email / SSO auto-link) is
`web-oauth-sso`/`web-logic-flaw`, not the enum oracle — the enum
CONFIRMS the email exists; the collision is the neighbor's exploit.
