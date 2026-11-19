# Onboarding (deep) — the guided first-pass

## The mental model

The server does MORE work for a real account than a fake one — it looks
up the row, it hashes the password, it sends the email, it counts the
attempt, it sets the lock. Each bit of extra work is a measurable
difference. The whole class is "find the difference the developer
forgot to hide".

## The 3-minute first probe

```bash
# 1. the direct oracle — one request may confirm it all
curl -s "$BASE/api/username-available?u=admin"

# 2. register — built to reveal availability
curl -s -X POST -d 'user=admin&email=a@b.c&pass=x' "$BASE/register"

# 3. the login pair — the 3-request differential
curl -i -X POST -d 'user=admin&pass=x'      "$BASE/login" > good
curl -i -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/login" > bad
diff good bad
```

## What you are looking at

- a different error message → text oracle
- a different status/`Location` → status/redirect oracle
- a slower `admin` arm → timing oracle (bcrypt gap)
- a `Set-Cookie` on one arm → side oracle
- `{"available":false}`/`{"taken":true}` → direct oracle
- a `423`/`429` → the throttle (and a lock-out oracle)

## The confusions to avoid

- a `500`/anomaly that does not repeat → a crash, not a channel
- a CSRF/`403` on both arms → a form error, not a differential
- identical body → the OTHER channels still open
- a uniform `/login` → the OTHER forms still open

## The two questions, always

1. **does it reveal which accounts exist?** (the oracle)
2. **can the guessing loop run unbounded?** (the throttle / its bypass)

## The next step

A confirmed oracle + a bounded seeded-name list → the verified accounts
→ route each to `web-auth-session`/`web-idor`/`web-logic-flaw`/
`web-oauth-sso`. The enum is the measurement; the exploit is the
neighbor's.
