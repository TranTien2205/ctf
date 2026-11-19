# Trust-in-earlier-step — step N+1 uses step N's output unchecked

Step N produces a value; step N+1 uses it without re-checking. The pipeline
trusts its own earlier output — and the output is attacker-shaped when the
attacker can reach the pipeline's middle.

## The mechanism

```
step 1: POST /quote     → server computes price, returns {quoteId, price: 50}
step 2: POST /order     → {quoteId: q1, price: 1}   ← the client sends the price
                            back — the server uses the client's price
```

The server produced `price: 50` in step 1; step 2 trusts the client to echo
it back faithfully. The attacker sends `price: 1` — the server orders at 1.

## The mechanism shapes

| Shape | The trusted value | Where it flows |
|---|---|---|
| echo-back | a value the server computed is sent back by the client | price, total, discount, limit |
| signed-opaque | a server value is signed and echoed — but the signature is weak | JWT, signed cookie, MAC |
| stored-state | a server value is stored in session/DB and trusted later | cart total, step flags |
| derived-id | a value derived from another is used as the key | `user_id` derived from `email` |
| header-trust | a proxy sets a header, the app trusts it | `X-Forwarded-User`, `X-Real-IP` |
| referer-trust | the app trusts `Referer`/`Origin` for a decision | CSRF checks, anti-hotlink |
| cookie-state | a cookie carries mutable state | `cart=...`, `role=user` |

## The detection

### The echo-back signal

```bash
# does the response contain a value the next request sends back?
grep -oE '"(price|total|discount|amount|limit|quota|role|tier)": *[0-9a-zA-Z."-]+' flow.txt
```

If the server's step-1 response carries `price: 50` and step-2's request
body contains `price`, the echo-back surface is live.

### The stored-state signal

```bash
# does a step's response carry a state token the next step consumes?
grep -oE '"(state|token|step|flag|session)": *"[^"]+"' flow.txt
```

### The header-trust signal

```bash
# does the app behave differently when a trust header is added?
curl -i -H "X-Forwarded-User: admin" "$BASE/api/me"
curl -i -H "X-Real-IP: 127.0.0.1" "$BASE/admin"
```

## The probe

```bash
# step 1 — get the server's value
QUOTE=$(curl -s -b "$JAR" -X POST "$BASE/quote" -d 'item=2&qty=1' | jq -r .quoteId)

# step 2 — echo it back, modified
curl -i -b "$JAR" -X POST "$BASE/order" -d "quoteId=$QUOTE&price=1"

# read the state back
curl -i -b "$JAR" "$BASE/order/$QUOTE"
```

## The confirmation

The downstream step acts on the modified value — the order's `price` is the
attacker's, not the server's:

```
HTTP/1.1 200 OK
{"orderId": 99, "price": 1, "charged": 1, "status": "confirmed"}
```

The `charged: 1` — the server's computed `50` was replaced by the
attacker's `1`, and the charge went through.

## The falsifier

The downstream step re-derives the value — the response carries the
server's computed value, not the attacker's:

```
HTTP/1.1 200 OK
{"orderId": 99, "price": 50, "charged": 50}
```

The sent `price=1` was ignored — the server looked up the quote's real
price. Or the mismatch is named:

```
HTTP/1.1 400 Bad Request
{"error": "price mismatch"}
```

## The pipeline map

Every place one endpoint's output feeds another's input:

```
/quote → /order → /payment → /confirm
/register → /verify → /activate
/init → /challenge → /solve → /flag
/upload → /scan → /publish
```

For each edge in the pipeline, name the value that crosses it and whether
the consumer re-checks it.

## The evidence rules

- The modified value must reach the sink verbatim — `charged: 1` in the
  order's stored state, not just a `200` response.
- Compare the server's computed value vs the value the endpoint used — the
  gap is the evidence.
- A `400` naming the mismatch is the falsifier — the step re-checks.

## The traps

- **The value may be opaque but signed.** A JWT or MAC'd token echoed back
  is the signed-opaque shape — the flaw is a weak signature, not
  trust-in-earlier-step. Classify accordingly.
- **The pipeline may store state server-side.** If `/order` reads the
  price from the stored quote, the echo-back is dead — but the stored
  value may be modifiable via a different endpoint.
- **The header-trust shape crosses into `web-parser-differential`** when a
  proxy strips and re-adds the header — check whether the header survives
  or is overwritten.
- **`Referer`-based decisions are fragile** — the browser controls the
  header, so `Referer` checks are always attacker-controlled from `curl`
  but not from a browser. The CSRF implication differs.
