# Falsifiers — the measurements that kill a business-logic shape

A falsifier is a probe whose result *closes* a hypothesis. Run it early,
record it when it fires, and let it move you to the next layer. A falsified
shape is progress — it is a layer you never have to walk again.

## Class falsifier (from SKILL.md)

> **The handler reads an explicit allowlist of fields and ignores
> everything else.**

If `register` accepts `role=admin` without error and the read-back shows
`role: user`, the mass-assignment shape is dead on this endpoint. Record it
and move — do not try `isAdmin`, `is_admin`, `admin`, `userRole` as ten
more probes of the same layer. The allowlist is the mechanism; the field
name was never the question.

## Per-mechanism falsifiers

| Shape | The falsifying result | Meaning |
|---|---|---|
| mass assignment | `role: user` in read-back after `role=admin` sent | allowlist binding |
| mass assignment | `400 "unknown field: role"` | strict schema — also dead |
| workflow skip | `400 "payment required"` or `302` to step 2 | server tracks state |
| workflow skip | step 3 returns identical to step 1 result | no sequential state at all — also dead |
| state replay | `409 already redeemed` on second POST | idempotency key exists |
| numeric boundary | `400 quantity must be positive` for `-1` | input validated |
| numeric boundary | quantity clamped to `0` or `1` silently | server-side clamp — dead at this field |
| scaling-after-check | out-of-limit ID rejected identically to a malformed ID | check happens post-transform, or no transform |
| unit confusion | `price=100` charged as `1.00` consistently | single canonical unit |
| role assignment | `role: user` after `role=admin` | allowlist (same as mass assignment) |
| idempotency | `409` on exact replay | deduplication exists |
| time assumption | `400 invalid expiry` for a past date | server-side time check |
| sequence assumption | `409` or `400` on old ID replay | sequence tracked |
| ownership assumption | `403` on another user's objectId | ownership enforced — this is IDOR's falsifier |
| singleton assumption | `409 admin already exists` | uniqueness enforced |
| trust-in-earlier-step | recomputed price differs from sent price → `400 price mismatch` | server recomputes |

## The Pachinko falsifier — the one this skill was built on

From the verified card's `first_confirming_probe`:

- Submit a minimal correct circuit.
- Submit the same circuit with one node ID just past the documented limit.
- **Expected**: valid circuit succeeds; out-of-limit value gets a
  *different-layer* rejection (it failed somewhere the documented limit
  doesn't describe).
- **Falsifier**: both rejected identically → no validator gap. The
  transform either doesn't exist or is checked too. Stop; the shape is dead.

The generalized form, reusable on any checked-then-transformed value:

```
baseline:   send id=N (documented valid)      → accepted
probe:      send id=N+k (just past limit)     → compare the rejection shape
same-layer rejection (identical error as a malformed id)
            → falsifier: the transform is checked too, or absent
different-layer rejection (a new error, a crash, a 500, silence)
            → the transform ran first — the gap is live
```

## Falsifier ≠ negative result

A falsifier *kills the hypothesis* ("this shape cannot work here"). A
negative result *bounds it* ("this variant didn't work; the shape may
still"). `role=admin` dropped → falsifier for that field. `role=admin`
rejected `400` → falsifier. `role=admin` accepted but `role: user` →
falsifier. There is no "the third spelling worked" once an allowlist is
proven — the allowlist answers all spellings at once.

## What to record

```bash
python3 tools/hooks.py post-probe <ch> \
  --request "POST /register role=admin" \
  --verdict falsified --class web-logic-flaw \
  --hypothesis-id <id> --evidence-kind class \
  --evidence '"role":"user"' --response "$(cat r.json)"
```

A falsified shape is recorded evidence of the same grade as a confirm —
it is what lets `decide.py` route you off a dead layer instead of
re-walking it next session.
