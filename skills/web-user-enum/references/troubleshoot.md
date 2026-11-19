# Troubleshoot — when the measurement won't cooperate

## "the diff is all noise"

Every response differs — CSRF token, timestamp, request-id, a rotating
banner. Measure `bad1` vs `bad2` to find the noise; mask it
(`sed 's/csrf[^<"]*//g'`); then diff. If the noise still swallows it,
normalize harder (strip all `value="..."`, all timestamps) or switch to
the status/side channel.

## "the timing is uniform but I expected a hash gap"

- a weak hash (sha256/md5) — real but sub-jitter; no usable oracle
- a time-equalized app — the bad arm burns a dummy hash; hunt the side
  channel or the variance difference
- a load balancer — different workers; pin a session cookie
- a cached response — vary a throwaway param to bust the cache
- jitter > delta — more samples, a local baseline, or drop to content

## "I get 403/CSRF on every request"

A missing/invalid CSRF token returns `403` on BOTH arms — re-fetch a
fresh token per request and include it, or the pair is unpaired. The
403 is a form error, not a differential.

## "the account locked and I can't probe anymore"

The lock IS an oracle (a real row carries it) but it kills the account —
use YOUR known-good account and stop before its threshold. Record the
lock-threshold as a finding; do not burn a victim's account to prove it.

## "the response is identical but I still suspect a leak"

- check the FULL envelope (`-sv`) — a cookie, a header, a JSON field
- check the send side-effect — the email/OTP only fires for a real row
- check the timing VARIANCE — a fixed dummy-hash has lower variance
- check a second form — register/reset may leak where login does not
- accept it may be closed — record the uniform measurement and move on

## "enum_probe reports uniform but manual curl differs"

The tool holds the fields constant; a manual request may differ in a
header, a cookie, a token. Match the tool's request exactly — the tool's
uniform result across controlled arms is the reliable read.

## "the throttle fires but resets too fast to measure"

A per-request window (e.g. 1 req/sec) is not a loop-blocker — measure
the window, record the rate, and note that a slow spray still passes it.
A `429` that a `Retry-After` header bounds is a measured limit, not a
block.
