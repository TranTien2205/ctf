# Negative results — the measurements that bound a business-logic shape

A negative result is a probe that produced no distinguishing signal. It is
not a failure and not a falsifier — it is a bound on where the mechanism
lives. Record every one; the ledger of negatives is what makes the next
probe cheaper.

## The three outcomes of any probe

| Result | Meaning | Action |
|---|---|---|
| confirming signal | forbidden state reached | confirm, record, chain forward |
| falsifying signal | the mechanism is provably absent | record `falsified`, leave the layer |
| **no distinguishing signal** | this variant didn't distinguish | record negative, change ONE variable |

The third row is the negative result. `POST /redeem` twice returning `200`
both times but balance read-back only shows one credit — the replay
*executed* but the write was deduplicated downstream. That is a negative on
the replay shape and a lead toward "the dedup lives in the ledger write,
not the endpoint" — a different layer.

## Negative-result catalogue

| Probe | Silent result | What it bounds |
|---|---|---|
| `role=admin` at register → `role: user` | field dropped | allowlist binding — falsifier |
| `role=admin` at register → `400` | strict schema | allowlist binding — falsifier |
| skip to `/confirm` → `302` to step 2 | state tracked | workflow state machine — falsifier |
| replay `redeem` → `200` both, balance +50 once | dedup at write | replay accepted, ledger dedups — move to ledger layer |
| `quantity=-1` → `400` | validated | numeric boundary dead at THIS field — try `price`, `discount` |
| `quantity=-1` → `200`, total clamps to `0` | clamped | boundary dead — clamp is the mechanism |
| ID past limit → identical rejection as malformed | transform checked or absent | Pachinko falsifier |
| `price=100` charged `1.00` | canonical unit | unit confusion dead |
| second `POST /admin` → `409` | singleton enforced | uniqueness check exists |
| `objectId=999` → `403` | ownership enforced | IDOR falsifier, not logic |
| upstream `price=1` → `400 price mismatch` | server recomputes | trust-in-earlier-step dead at this field |

## The discipline: one negative = one variable change

A negative tells you *this combination* didn't distinguish. It does not
tell you the class is dead. The rule:

1. Change exactly ONE variable — the field, the value, the endpoint, or
   the layer.
2. Record which variable changed and what the negative bound.
3. Five negatives inside one mechanism class = the budget signal to
   change LAYER, not variant. `decide.py` enforces this; don't spend a
   sixth probe re-spelling `role`.

## Recording a negative

```bash
python3 tools/hooks.py post-probe <ch> \
  --request "POST /cart productId=2&quantity=-1" \
  --verdict negative --class web-logic-flaw \
  --hypothesis-id <id> \
  --evidence "quantity rejected at input validation" \
  --response "$(cat resp_cart_400.txt)"
```

A negative with `--response` is auditable. A mental note is not.

## The pattern: negatives funnel toward the layer

Pachinko again: variant after variant of malformed circuit produced the
*same* rejection — no distinguishing signal. The card's lesson: **stop
probing variants when a mechanism produces no distinguishing signal and
change layer.** The negative results weren't wasted — they proved the
rejection lived in the transport checker, which is exactly the evidence
that pointed at the post-check transform.

A run of identical negatives is itself a measurement: it maps which layer
rejects first.
