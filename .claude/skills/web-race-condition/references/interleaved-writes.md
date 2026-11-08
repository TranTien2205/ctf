# Interleaved writes: the read-modify-write window

The exploitable race is almost never "send fast twice". It is a
read-modify-write whose *read* and *write* are separated — a verification
token, a balance check, a uniqueness check — so two in-flight requests each see
the pre-write state.

## Probe shape that worked (ApexSurvive, twice)

Send two interleaved profile updates and observe which address receives which
token:

```text
A: POST /profile  {email: a@x}      # begins, generates token for a@x
B: POST /profile  {email: b@y}      # begins before A commits
```

Expected: the token generated for one address is delivered to the *other*
in-flight update's address — the token-generation and the send/read steps are
not atomic, so whichever request commits last binds the earlier token.
Falsifier: each token reaches only its own address on every ordering; the
sequence is serialized.

## The delivery mechanics that matter

- Interleave, don't burst: hold request A open (partial body, slowloris-style
  pause, or a last-byte stall) while B lands in the window — a blind parallel
  burst usually serializes anyway. `tools/web/race_probe.py` exists for the
  burst form; the interleave form needs the stall.
- The observable is *crossed* state: token to the wrong mailbox, credit to the
  wrong account, the second redeem accepted after the first.

## The check-then-act alphabet

| Pattern | Window |
|---|---|
| email/phone change + verify token | token generated, address swapped |
| redeem/transfer/limit | balance or count read pre-write |
| registration uniqueness | two usernames pass the check together |
| OTP / code attempt | per-attempt counter read pre-increment |

## Timing-oracle variant (PhantomFeed)

When the write path itself is safe, a pathological input can still win by
*stalling* the check: `email=a@` + 26 chars + `!` against a regex made the
verification window measurably wider than a normal email — the timing
difference between arms is itself the signal that a window exists.

## Falsifier

No attributable before/after state change: record inconclusive and stop — do
not flood. Every repeat must still pair a named request shape with a named
crossed-state outcome.
