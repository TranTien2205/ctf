# Side-channel observability — measuring the un-observable

## The send-side as the strongest oracle

A reset/OTP/invite whose EMAIL/SMS fires only for a real row is the
hardest-to-equalize channel — the send is a real side-effect, not a
response byte. Measure it:

- register a real account you control → `POST /forgot-password` with
  YOUR email → the email arrives
- `POST /forgot-password` with a fake → no email → the send-side oracle
- `{"emails_queued":1}`/`{"sent":true}` — a response field carrying the
  send count
- a `302 /check-email` only on the real arm — the redirect reveals it

## The `Set-Cookie` envelope

```bash
diff <(grep -i 'set-cookie' g) <(grep -i 'set-cookie' b)
```

A `Set-Cookie: auth_attempt=`, `error=`, `last_user=`, a flash-cookie —
a cookie set on one arm only is the envelope oracle. A session-cookie
issued on the real arm (a pre-auth session) vs none on the fake is a
differential.

## The `X-` header hunt

```bash
curl -sv -d "user=$U&pass=x" "$FORM" 2>&1 | grep -iE '^< (x-|set-cookie|retry|www-auth)'
```

- `X-Auth-Reason: no_user` / `X-Auth-Reason: bad_pass`
- `X-RateLimit-Remaining` / `X-RateLimit-Reset` — the counter
- `Retry-After` — a throttle/delay hint
- `X-User-Exists` / `X-Error-Code` / a custom debug header
- `WWW-Authenticate` realm/message — a basic-auth oracle

## The JSON-field hunt

```bash
curl -s ... | python3 -m json.tool | grep -iE 'attempt|remain|exist|user|reason|error|code|lock|email|sent|valid'
```

`attempts_remaining` — a counter only a real row carries; `emails_sent`,
`user_exists`, `is_locked`, `reason`, a typed `code` — the field the UI
never renders is the oracle.

## The audit/log side-effect

A failed login that logs `"failed login for <name>"` — if the log/
audit is readable (a debug endpoint, an exposed log, an admin panel),
the recorded name is a confirmation channel. Rare but decisive.

## The cache-timing side-channel

A cached login page vs an uncached auth attempt — a `Cache-Control`/
`X-Cache: HIT`/`MISS` differential, or a cached `200` for a real user's
profile vs a `404` — the cache layer leaks existence.

## The third-party side-effect

A webhook/callback that fires only for a real row — a `POST` to a
callback URL on registration/reset; a queue/metric that increments on a
real user. Indirect but real.

## The observability rule

The response BODY is the least reliable channel — it is the one the
defense equalizes. The ENVELOPE (cookie/header), the SIDE-EFFECT (send/
log/cache), and the TIMING are where the unequalized asymmetry survives.
`channel-side.md` is the protocol; this file is the observable map.
