# Common mistakes — the failures that cost a session

## Claiming a differential from a single read

One anomalous response is a crash, a CSRF failure, or per-request noise —
not an oracle. Re-send the exact bad request; if it does not repeat, the
channel is closed. A differential is a repeated, channel-identified
delta, not a one-off.

## Diffing the rendered page

The browser hides the leak — whitespace, comments, hidden inputs,
`data-*`, inline booleans. Diff the RAW body bytes and the full `-sv`
envelope, not what the page shows.

## Ignoring per-request noise

A CSRF token/timestamp/request-id differs on EVERY response — it fakes
a differential AND masks a real one. Measure `bad1` vs `bad2` first to
find the noise; mask it; then diff.

## Probing only the login

The login is the most hardened form — the register, reset, check-username,
and API endpoints leak first. A uniform `/login` is not "the app does not
enumerate"; coverage is per-form (`form-surface.md`).

## One-shot timing

A single `curl -w '%{time_total}'` is noise — network jitter is 10-50ms.
Use N≥8 interleaved samples, compare medians, control for jitter, and
re-run. A sub-jitter delta is not an oracle.

## Spraying a wordlist

A mass-username spray on a shared/victim target is the brute-force run
the throttle stops — it trips the lock, burns the target, and proves
nothing a 3-request oracle doesn't. The oracle is proven with
known-good + known-bad; the list is bounded and scope-gated.

## Confusing absence-of-signal with no-signal

"I didn't see a rate limit" is not "there is no rate limit" — a bounded
burst (8-15) with no 429/lock/delay is the measurement; below that is
unmeasured.

## Missing the lockout-as-oracle

A `"account locked"` response on a real name vs `"invalid"` on a random
name IS an exists-oracle — the lock fires only on a real row. Record
it, don't discard it as "the control won".

## Routing to enum when it is auth-session

A uniform-login target with a session/JWT/token bug is `web-auth-session`,
not this class. Enum needs a differential OR a throttle finding; a clean
auth path is the neighbor class.
