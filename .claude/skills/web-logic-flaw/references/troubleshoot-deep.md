# Troubleshoot deep — the stalls and what they're actually telling you

## Stall 1 — "Nothing works and I don't know which layer rejects"

The rejection is a locator, not a wall. Build the layer map:

```
probe family          → response           → layer
malformed JSON        → 400 parse error     → transport
valid JSON, extra key → 400 unknown field   → schema/binder
valid fields, bad val → 400 validation      → field validator
valid all, wrong step → 302/409             → state machine
valid all, replay     → 409 dedup           → ledger
valid all, crashes    → 500                 → sink/transform
```

Send one probe per family, bucket the responses — five requests maps
the whole rejection stack. Any family that DOESN'T produce its expected
rejection got further than expected: that's the layer gap.

## Stall 2 — "The skip works but the state won't stick"

`/confirm` returned 200 but the GET shows `pending`. Possibilities:

- the endpoint accepted and a background worker performs the transition —
  poll the GET a few times;
- the 200 was a no-op path — the handler early-returns success for
  missing preconditions (a "soft" skip that looks like a bypass but does
  nothing);
- the transition needs a side-effect the skipped step produces — the
  `pay` step minted a token `confirm` consumes.

The soft-skip case is a common trap: `200` is not the forbidden state —
read back the OBJECT, not the status code.

## Stall 3 — "Replay succeeded but the ledger deduped"

`200` twice, effect once — the dedup lives downstream. The key question:
what does the dedup key cover?

- key = `(user, code)` → cross-USER replay: consume as A, replay as B.
- key = `(requestId)` → same action, different requestId.
- key = `(endpoint)` → the same action through a different path —
  `/redeem` vs `/claim` vs an admin path.
- key = `(code)` → a second code with the same effect.

Each is a different probe — and the dedup key's coverage is the actual
mechanism boundary.

## Stall 4 — "The boundary value is accepted but nothing breaks"

`quantity=-1` accepted, cart shows `-1`, total correct at `-50` — but
checkout re-validates. The boundary dead-ends at a second validator.
That's the two-validator pattern: finding it means the question shifts —
does the second validator check the SAME things? A `quantity=-1` the
checkout re-checks says nothing about `price=-1` it may not.

Also: is the negative state itself the goal? In challenge design the
forbidden value often IS the sink — a `total=-50` the system credits
back to you.

## Stall 5 — "I found the gap but can't reach the flag"

The confirm is an edge, not the path. Map what the new state reaches:

- `role: admin` → enumerate role-gated routes from the bundle — the flag
  is a FIELD in an admin view, rarely a `/flag` path.
- `balance: 200` → what does the shop sell at >200? the flag is often an
  item priced above legit max.
- skipped confirm → the terminal STATE'S payload, not the endpoint —
  the flag renders inside the confirmed order.

The chain walk: for each confirm, list the endpoints that state unlocks
(grep the bundle/source for the role/state check), probe each.

## Stall 6 — "Probes get slower / errors after a few requests"

Rate limiting — a budget concern, not a mechanism result. Space the
probes; run the cheap ones (GETs) during cooldowns. A `429` is not a
rejection-shape datapoint — exclude it from the layer map.

## Stall 7 — "It worked against my test account but not the real flow"

Scope-check: the test object may have different state (a cart you
created vs the challenge's seeded order). Re-run the probe on the
seeded object; if it fails there, the difference IS the mechanism —
find which field differs between your object and the seeded one.

## Stall 8 — "The transform math doesn't close"

`off + id*S mod 2^w` doesn't reach the target for any `id < LIMIT`:

- wrong `S` — re-derive the scale from source or from two known
  `id → address` pairs;
- `S` even and `(T-off)` outside the congruence class — pick a different
  target `T'` in `{off + id*S mod 2^w}`;
- `w` wrong — the wrap modulus may be the pointer width, not the field
  width;
- the check may bound the TRANSFORMED value after all — re-run the
  different-layer test; if it now rejects identically, the card's
  falsifier fired on this target.
