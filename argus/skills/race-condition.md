# Race condition (TOCTOU)

**When:** check-then-act on a limited resource. Signals: coupon/voucher
redeem, balance transfer, one-time token, vote/like limits, withdraw/spend,
seat/quota allocation, file upload uniqueness.

## The measurement that matters

A race is proven by OVERLAP, not by count. Send N near-simultaneous
requests and compare against a SERIAL baseline:

1. Serial: fire the same request N times one-by-one - the app should accept
   exactly K (usually 1). This is the expected outcome.
2. Parallel: fire N requests inside the same ~50ms window
   (single-packet/last-byte sync beats naive thread starts: hold the
   connection, send the final byte together).
3. Accepted > K in parallel while serial stays at K = TOCTOU confirmed.

A response that "looks duplicated" but also appears serially is NOT a race.

## Where window width matters

- Same-session races often serialize per-session server-side: use two
  sessions for the same account if one-session tests fail.
- Optimistic-locking/atomic-counters defeat it: accepted count stays K.
- Long transactions widen the window: a slow endpoint (large body first)
  is easier to interleave.

## Tooling honesty

`run_external` cannot send single-packet-synchronized bursts by itself;
construct the overlap with raw sockets via http_request's recorded path
only if the harness supports it - otherwise note the limitation, run the
serial-vs-parallel comparison, and report the anomaly as a strong lead.

## Falsifier

Parallel and serial accept counts match across ~3 bursts, or the server
serializes the operation (queue/lock response timing shows it).

## Severity guide

Financial/asset duplication: high-critical. Limit bypass (rate, vote,
quota) with bounded impact: medium. Email/token duplication: low-medium.
