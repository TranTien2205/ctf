# Negative results deep — reading the silence

A probe producing no distinguishing signal is the most information-dense
result in logic testing — it maps which layer answered. This module is
how to read it.

## The rejection-shape taxonomy

Compare every rejection on four axes: status, error text, timing, and
what the state did afterward.

| Rejection shape | Layer that fired | What it proves |
|---|---|---|
| `400` + `invalid input` | transport/schema | parser rejected before app logic |
| `400` + `unknown field: role` | binder allowlist | strict schema — mass assignment dead |
| `400` + `quantity must be positive` | field validator | this FIELD checked — others unmeasured |
| `302` → earlier step | state machine | ordering enforced server-side |
| `409` + `already redeemed` | idempotency store | dedup exists |
| `403` + `not your object` | ownership check | IDOR falsifier — different class |
| `500` / crash / reset | unguarded transform or sink | the check was NOT where the value broke |
| `200` + state unchanged | downstream dedup/clamp | endpoint accepted, layer below deduped |
| silence / hang | resource or assertion | deeper layer — investigate timing |

## The contrast probe

When a probe is rejected and you can't name the layer, run the contrast:
a MALFORMED value (string for int) vs an OUT-OF-LIMIT value (int past
the bound).

- Both reject identically → same layer handles both — the check is the
  first thing hit. For the Pachinko shape, that's the falsifier.
- Different rejections → the out-of-limit value got PAST the layer that
  rejects malformed input and failed deeper. That deeper failure is
  evidence the transform ran unchecked — the class signal.

Pachinko: `id` just past the documented limit produced a different-
layer rejection — the transport accepted it, the deeper checker (or the
transform's result) rejected it, and that difference located the gap.

## The accepted-but-deduped silence

`POST /redeem` twice → `200` both times, balance moves once. The endpoint
accepted the replay; the ledger deduplicated the write. Read the
silence as a map:

- the replay reached business logic (no `409`),
- the write was deduped downstream (balance moved once),
- → the dedup lives in the ledger layer, not the endpoint.

The next probe changes layer: can the ledger's dedup key be varied
(`request_id` in body)? Can the ledger be written through a different
endpoint (refund vs redeem)?

## The clamped silence

`quantity=-1` → `200`, cart shows `quantity: 0`. The value was clamped,
not rejected — the clamp IS the mechanism boundary. Record it: boundary
dead at this field via clamping. Then the question is whether the clamp
is consistent — does `quantity=-1` on `price` also clamp, or does
`discount` accept what `quantity` can't?

## Runs of silence

N probes, N identical responses — the card's lesson verbatim:

> Stop probing variants when a mechanism produces no distinguishing
> signal and change layer.

Identical negatives are themselves a measurement: every probe hit the
same layer. After five, `decide.py` forces the layer change. The silence
told you where the rejection lives; the next probe must come from a
layer ABOVE it (a different field, a different endpoint, a different
state carrier — cookie vs body vs header).

## Recording the negative properly

```bash
python3 tools/hooks.py post-probe <ch> \
  --request "POST /cart quantity=-1" \
  --verdict negative --class web-logic-flaw \
  --hypothesis-id <id> \
  --evidence "400: quantity must be positive (field validator)" \
  --response "$(cat resp_cart_400.txt)"
```

The `--evidence` names the LAYER the rejection came from — that's what
makes the negative useful to the next session.

## The negative ledger pattern

Keep the negatives tabular in your notes:

| Probe | Result | Layer | Variable for next probe |
|---|---|---|---|
| qty=-1 | 400 validator | field | try `price` |
| price=-1 | 400 validator | field | try `discount` |
| discount=-50 | 200, total clamped | clamp | try `NaN` |
| discount=NaN | 200, total=NaN, checkout 400 | checkout validator | try `1e309` |

Each row narrows where the unguarded arithmetic lives.
