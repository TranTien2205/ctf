# Falsifiers — the observations that close this class

## The class falsifier

**Identical response text, status, and timing distribution for
known-good, known-bad, and repeated-bad attempts — including the timing
of the password-verification path.** When all four channels are uniform
across a repeated, noise-masked, multi-sample measurement, the endpoint
does not enumerate and this route is closed.

## Per-channel falsifiers

| Channel | Closed when |
|---|---|
| body | the same bad username twice → byte-identical (after noise-mask), and good==bad |
| status+redirect | the same bad twice → identical code + `Location`; good==bad |
| timing | median(good)−median(bad) within ~1× jitter, N≥8, repeated across a second bad name |
| side-artifact | identical `Set-Cookie`/headers/JSON-fields across both arms |

## The "one anomalous read" falsifier

A response that differs once but does not repeat is NOT a differential —
it is a crash, a CSRF failure, a per-request field, or a load-balanced
worker variant. Re-send the exact bad request; if the anomaly does not
reappear, the channel is closed.

## The "uniform because noise-masked" trap

If the diff is masked by per-request noise (CSRF, timestamp), the channel
is not closed — it is unmeasured. Re-fetch a fresh token per request and
mask the noise before reading the diff; a real measurement separates
noise from signal.

## The throttle-presence falsifier

A `429`, a CAPTCHA, a `423 Locked`, or a growing delay IS a control —
the "no throttle" claim is falsified. Record the threshold instead.

## The per-form falsifier

Each form is falsified independently — a hardened login does NOT close
the register or reset. A form is closed only when ITS channels are all
uniform; the class is closed when EVERY account-touching form is closed.

## The endpoint-coverage falsifier

Probing only `/login` and calling the class closed misses
`/api/login`, `/register`, `/reset`, `/check-username`. The class is
falsified only when the full account-touching surface is measured
uniform — `form-surface.md` is the coverage list.

## When to stop

- every account-touching form measured uniform on all four channels →
  record `enum: all forms uniform` and close the class
- an oracle is found but the account list is not needed for the chain →
  record the oracle + the confirmed name; the enum's job is done
- a repeated-bad pair is byte-identical on all channels → that channel
  is measured-dead
