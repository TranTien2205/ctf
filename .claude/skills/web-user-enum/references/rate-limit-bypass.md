# Rate-limit bypass — when the counter resets

## The bypass inventory

### Source-IP rotation — the per-IP counter

If the limit is keyed on client IP, these headers may reset it:

```bash
for h in 'X-Forwarded-For: 1.1.1.1' 'X-Forwarded-For: 2.2.2.2' \
         'X-Real-IP: 3.3.3.3' 'X-Client-IP: 4.4.4.4' \
         'X-Originating-IP: 5.5.5.5' 'CF-Connecting-IP: 6.6.6.6' \
         'True-Client-IP: 7.7.7.7' 'Forwarded: for=8.8.8.8'; do
  curl -s -o /dev/null -w "%{http_code} [$h]\n" -X POST \
    -H "$h" -d 'user=x&pass=y' "$BASE/login"
done
```

A `429` that becomes a `401`/`200` under a spoofed `X-Forwarded-For`
means the app reads the header for the counter — the bypass is the
finding. Rotate the value per-request and the per-IP limit is gone.

### Username rotation — the per-account counter

The counter is keyed on `username`; rotating usernames avoids the lock.
This is the password-spraying pattern — one password against many
accounts, never two attempts on the same account. If `/login` locks
`admin` after 5 but `admin2` has its own counter, the per-account limit
is bypassed by enumeration itself.

### Session/cookie reset — the per-session counter

```bash
# a fresh session each request resets a session-keyed counter
curl -s -c /dev/null -X POST -d 'user=x&pass=y' "$BASE/login"   # no cookie jar
```

A counter stored in a cookie or keyed on the session id resets when the
session is dropped — send each attempt with no cookie / a fresh session.

### Endpoint rotation — a per-endpoint limit

`/login` limited, but `/api/login`, `/api/v1/login`, `/auth`, `/token`,
`/reset`, or a `/login/` (trailing slash), `/LOGIN` (case), `/login `
(trailing space) alias is not. Probe every auth-path alias.

### Method/parameter rotation

- `POST` limited, `GET` not (or vice versa)
- a JSON body vs a form body hitting different limiters
- a `Content-Type` change routing around the limiter

### Credential-stuffing-friendly gaps

- the limiter counts only FAILED attempts — interleave a success to reset
- a captcha cookie/token reusable across attempts
- a `remember-me`/`device` field that skips the limiter

## The bypass = the finding

When a reset works, record `limit reset by <header/param>` — the bypass
is itself the reportable weakness (the limiter trusts attacker input).
Confirm the reset is real: the response returns to the pre-limit
behavior (200/401 not 429), and a subsequent normal request still works.
