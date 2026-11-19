# Evidence rules — what proves an enumeration oracle

## The claim ladder

| Claim | Evidence required |
|---|---|
| "the form distinguishes" | a repeated, channel-identified delta between known-good and known-bad, with a repeated-bad baseline showing the noise |
| "it's a text oracle" | the two verbatim message excerpts + the noise-masked diff |
| "it's a timing oracle" | median(good) − median(bad) > ~3× jitter, N≥8, interleaved, re-run-confirmed |
| "it's a redirect oracle" | the two verbatim `Location` values, byte-identical across repeats |
| "an account exists" | the oracle's response for that name matches the known-good arm, verbatim |
| "no throttle" | 12+ requests, no 429/captcha/lock/growing-delay — a bounded count, not "I didn't see one" |
| "the limit is X" | the request count where 429/lock first fired |
| "the limit is bypassed" | a spoofed request returning to pre-limit behavior after the limit fired |

## The verbatim rule

A finding carries the response bytes, not a description:

- `"invalid username"` (bad) vs `"invalid password"` (good) — quote both
- `Location: /login?error=2` vs `Location: /login?error=1`
- `{"code":1001}` vs `{"code":1002}`
- timing: `good_med=247ms bad_med=8ms jitter=4ms delta=239ms`

`hooks.py post-probe --verdict confirms --evidence '<excerpt>'
--response '<the response>'` — the excerpt must be a substring of the
response.

## The repeat rule — a single read is not evidence

- the SAME bad username twice → byte-identical (the noise baseline)
- a SECOND different bad name → same as the first bad (it tracks the
  username-class, not the string)
- the known-good → differs on at least one channel

A delta that appears only once is noise; a delta that survives a re-run
with a different bad name is the oracle.

## What is NOT evidence

- a single anomalous response (could be a crash, a CSRF failure, a
  per-request field)
- a delta that does not repeat
- a response that differs only in per-request noise (CSRF, timestamp,
  request-id) — masked before it counts
- "it usually takes longer" — no median, no count
- "I think it locked" — no 423/429 observed

## The negative that counts

A uniform result is a real negative only when measured on all four
channels: body (noise-masked), status+Location, timing (N≥8, median),
and the side-artifact envelope. "I didn't diff" is not a negative.
