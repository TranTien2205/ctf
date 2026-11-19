# Summary — the class in one page

## What it is

An account-touching endpoint that responds differently to a real account
vs a fake one — **user enumeration** — plus the dual question of whether
the guessing loop is bounded — **auth throttling**.

## The four channels (cheapest first)

1. **body** — the raw-byte diff: text, code, CSS class, hidden field
2. **status+redirect** — the code and the `Location` parameter
3. **timing** — the bcrypt/argon2 hash runs only for real users
4. **side-artifact** — a `Set-Cookie`, an email sent, a lock set, a JSON field

## The three-request probe

```bash
curl -i -X POST -d 'user=KNOWN&pass=x'      "$BASE/<form>" > good
curl -i -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/<form>" > bad1
curl -i -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/<form>" > bad2
```

`bad1==bad2` (noise baseline), `good!=bad` on ≥1 channel = the oracle.

## The form coverage

Probe every account-touching form — check-username > register > reset >
login > mfa — the weakest leaks first. A uniform login does not close a
leaky register.

## The throttle

A bounded burst (8-15) measures: absent (no 429/lock/delay), present
(record the threshold), or bypassed (`X-Forwarded-For`/session/endpoint
reset — the bypass is the finding).

## The enum is a link

A confirmed account name routes to `web-auth-session` (spray/reset/MFA),
`web-idor` (the user object), `web-logic-flaw` (reset-flow bugs),
`web-oauth-sso` (email-collision pre-hijack).

## The rules

- a differential is a **repeated, channel-identified** delta, not a
  one-shot
- mask per-request noise before diffing
- **never spray** a real wordlist on a shared/victim target — the oracle
  is proven with 3 requests, the list is bounded and scope-gated
- a locked account is an exists-oracle, not a dead end
- **catalogue** — record real observations in `../field-notes.md`
