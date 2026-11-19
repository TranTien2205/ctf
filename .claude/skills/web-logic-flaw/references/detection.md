# Detection — the business-logic surface map

Every business-logic flaw is a rule the application was told and follows
faithfully. Detection is mapping the told-rule to the intended-rule — the
gap between them is the candidate.

## The detection sequence

```
1. Map the object's state — every field, every value, every transition
2. Map the intended rules — from the copy, the source, the error messages
3. Find the divergence — where the told-rule differs from the intended-rule
4. Name the mechanism — mass assignment? workflow skip? numeric boundary?
5. Run the probe — the cheapest falsifier first
```

## Step 1 — the state map

```bash
# the account's own state — every field, every value
curl -i -b "$JAR" "$BASE/api/me" | jq .
curl -i -b "$JAR" "$BASE/api/account" | jq .
curl -i -b "$JAR" "$BASE/api/balance" | jq .

# the object's state — every field the form sends, every field the model has
curl -i -b "$JAR" "$BASE/api/user/1" | jq 'keys'
```

The state map is the before-snapshot — every field, every value, every
transition the object can take.

## Step 2 — the intended rules

The intended rules come from:

- **The copy** — "one coupon per customer", "quantity must be positive",
  "payment required before shipping".
- **The source** — white-box: the model's validation, the handler's checks.
- **The error messages** — "quantity must be positive" names the rule that
  exists but is not enforced.
- **The form** — the form's field list vs the model's field list — the gap.
- **The workflow** — the intended step order vs the enforced step order.

## Step 3 — the divergence

The divergence is where the told-rule differs from the intended-rule:

| The told-rule | The intended-rule | The mechanism |
|---|---|---|
| bind every field in the body | bind only the form's fields | mass assignment |
| trust the step order | enforce the step order | workflow skip |
| validate the input | record the transition | state replay |
| accept the type's values | accept only the domain's values | numeric boundary |
| check the pre-transform value | check the post-transform value | scaling-after-check |
| bind the privileged field | bind only the user fields | role assignment |
| run the action | record that it ran | idempotency |
| trust the client's unit | use the server's unit | unit confusion |
| default permissively | default restrictively | default fallback |
| trust the earlier step | re-check the earlier step | trust-in-earlier-step |

## Step 4 — the mechanism

Name the mechanism — the rule that is wrong — before probing:

| The signal | The mechanism |
|---|---|
| extra field changes state | mass assignment |
| step N+1 reachable before step N | workflow skip |
| second application produces same effect | state replay |
| forbidden value reaches the sink | numeric boundary |
| post-transform address out of range | scaling-after-check |
| `role=admin` at register | role assignment |
| refund twice | idempotency |
| `100` for `1.00` | unit confusion |
| absent `role` defaults to admin | default fallback |
| modified upstream value flows through | trust-in-earlier-step |

## Step 5 — the falsifier sweep

```bash
# falsifier 1 — mass assignment
curl -i -b "$JAR" -X POST "$BASE/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"probe","password":"x","role":"admin"}'

# falsifier 2 — workflow skip
curl -i -b "$JAR" -X POST "$BASE/confirm" -d 'orderId=1'

# falsifier 3 — state replay
curl -i -b "$JAR" -X POST "$BASE/redeem" -d 'code=SAVE50'
curl -i -b "$JAR" -X POST "$BASE/redeem" -d 'code=SAVE50'

# falsifier 4 — numeric boundary
curl -i -b "$JAR" -X POST "$BASE/cart" -d 'productId=2&quantity=-1'

# falsifier 5 — role assignment
curl -i -b "$JAR" -X POST "$BASE/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"probe","password":"x","role":"admin"}'
```

## The detection signals

| Signal | The mechanism | The probe |
|---|---|---|
| extra field changes state | mass assignment | add the field |
| step N+1 reachable before step N | workflow skip | call the later step |
| second application produces same effect | state replay | replay the transition |
| forbidden value reaches the sink | numeric boundary | send the forbidden value |
| post-transform address out of range | scaling-after-check | pick the index |
| `role=admin` at register | role assignment | register with the field |
| refund twice | idempotency | replay the action |
| `100` for `1.00` | unit confusion | send the other unit |
| absent `role` defaults to admin | default fallback | omit the field |
| modified upstream value flows through | trust-in-earlier-step | modify the upstream value |
