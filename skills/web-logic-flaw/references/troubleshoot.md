# Troubleshoot — when business-logic probes produce nothing

## "Every field I add gets dropped or rejected"

An allowlist is proven — that's a falsifier, not a stall. Move off mass
assignment onto another mechanism in the alphabet: workflow skip, replay,
numeric boundary. The alphabet exists because logic flaws cluster: an app
with an allowlist on fields may still skip a state check.

## "The workflow skip returns 302 to step 2"

The server tracks state. Check WHERE it tracks it:

- Session cookie carrying a `step` value → modify the cookie's step.
- Server-side session → the state is real; try a parallel session
  sharing an object ID (cross-session state bleed).
- A `state`/`token` param echoed per request → forge the param's value.

A 302 redirect is the state machine working — the falsifier fired.
Different question: does the FINAL endpoint check the state at all?
`/confirm` may redirect while `/flag` checks nothing.

## "Replay returns 200 but nothing changed"

The dedup may live downstream — the endpoint accepts the replay and the
ledger dedups the write. Evidence: `200` twice, balance moved once.
That's a negative on the endpoint layer and a lead on the ledger layer.
Can the ledger be reached directly? Is the dedup keyed on a value you
control (a `request_id` you can vary)?

## "Negative quantities get 400"

The input validator works on this field. Try the boundary alphabet on the
SAME field — `0`, `NaN`, `1e309`, `0x10`, `"1"`, `[]` — each is a
different parser path, not a spelling variant. Then move to the OTHER
numeric fields: `price`, `discount`, `tax`, `shipping`. A validated
`quantity` says nothing about `discount`.

## "I can't tell which layer rejected"

Instrument the rejection shape: send a *malformed* value (string where
int expected) and an *out-of-limit* value, and diff the two rejections.

- Identical errors → the check is the first layer hit; the transform
  (if any) is also checked or absent — falsifier territory.
- Different errors, or a 500 vs a 400 → the transform ran first; the
  second failure is at a deeper layer — that's the gap.

Pachinko: a different-layer rejection for the out-of-limit ID was the
signal the transform ran before the check.

## "The state was already there — I can't prove my request caused it"

Isolate the object: fresh account, fresh cart, fresh order per probe. If
the app won't mint fresh objects cheaply, read-back a baseline field you
didn't touch (`createdAt`, `sequence`) to prove the state is new.

## "It worked once and now doesn't"

- Idempotency key exists but is scoped — vary the key.
- Rate limit — slow down; this is a budget concern, not a mechanism one.
- The object is consumed (one-shot flag, spent coupon) — mint a fresh one.
- Server-side state changed globally — re-run the baseline; if the
  baseline also changed, the world moved, not your exploit.

## "No distinguishing signal across dozens of probes"

Stop. The card's own lesson: a mechanism producing no distinguishing
signal across its variants means the probes are all hitting the same
layer. Change LAYERS — from the field value to the transport (encoding,
content-type), from the endpoint to the state machine, from the request
to the session. `decide.py` after five probes of one class.
