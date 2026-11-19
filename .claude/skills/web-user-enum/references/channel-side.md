# Side-artifact channel — the leak that is not in the body

## The artifact inventory

When text and timing are equalized, these still leak:

### Set-Cookie

```bash
curl -s -D - -o /dev/null -X POST -d 'user=KNOWN&pass=x' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -o /dev/null -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/login" | grep -i 'set-cookie'
```

- a `session=…` issued on the good arm (auth-progress cookie) but not
  the bad arm
- an `error=…` / `last_user=…` / `flash=…` cookie carrying the reason
- a cookie that is SET on one arm and DELETED (`Max-Age=0`) on the other

### Email / send side effect

A `forgot-password` form returns "if that account exists, a link was
sent" — a uniform response — but the email only goes out for a real
account. The send is the side effect; measure it on an account you
control (does YOUR address get the mail while a random one provably
does not — confirmed via a second channel or a response artifact like
`{"emails_sent":1}` vs `0`).

### Lockout / counter

Repeated bad attempts lock only real accounts. A real account that
returns `423 Locked` / `"account locked"` after N tries while a random
name keeps returning `"invalid"` is an account-exists oracle — the lock
fires only on a real row.

### Audit / log artifact

A response or side channel that logs `"failed login for KNOWN"` vs a
silent bad-user — visible in an error, a `X-Request-Id` that resolves to
a log line, or a subsequent admin/audit view.

### Header artifact

- `X-RateLimit-Remaining` that decrements differently
- `Retry-After` present on one arm
- a custom `X-Auth-Reason` / `X-Error-Code` header

### Embedded boolean / JSON field

`{"user_exists":true}`, `{"reason":"no_user"}` vs `{"reason":"bad_pass"}`,
`{"attempts_remaining":4}` — the field carries the distinction even when
the top-level message is uniform.

## The artifact hunt protocol

```bash
# capture EVERYTHING, both arms, then diff the whole envelope
curl -sv -X POST -d 'user=KNOWN&pass=x' "$BASE/login" 2>&1 | grep -E '^[<>]|Set-Cookie|HTTP/' > g.env
curl -sv -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/login" 2>&1 | grep -E '^[<>]|Set-Cookie|HTTP/' > b.env
diff g.env b.env
```

The envelope — status line, every header, every cookie — is the artifact
surface. A `-sv` capture shows what a body-diff misses.
