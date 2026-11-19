# Channels — the four oracle channels, ordered cheapest-first

## Channel 1: body text

The response bytes differ. The diff must be on the **raw body**, not the
rendered page — renderers normalize whitespace, hide `<input type=hidden>`,
`data-*` attributes, comments, and inline JS booleans.

```bash
curl -s -X POST -d 'user=KNOWN&pass=x' "$BASE/login" > g.body
curl -s -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/login" > b.body
diff <(tr -d ' ' < g.body) <(tr -d ' ' < b.body)   # whitespace-insensitive
cmp -l g.body b.body | head                          # byte-level diff
wc -c g.body b.body                                  # length delta
```

A 1-byte length delta, a different `<input name=err value=1>` vs `2`, a
`<div class="error-USER">` vs `error-PASS` — all count.

## Channel 2: status and redirect

```bash
curl -s -o /dev/null -w '%{http_code} -> %{redirect_url}\n' -X POST -d 'user=KNOWN&pass=x' "$BASE/login"
curl -s -o /dev/null -w '%{http_code} -> %{redirect_url}\n' -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/login"
```

A `200` vs `302`, a `302 /dashboard` vs `302 /login?e=2`, a `401` vs
`403`, a `Location: /login?error=user` vs `?error=pass` — the status
line and `Location` are the oracle.

## Channel 3: timing

Password hashing runs only for real users — the expensive `verify` call
is the asymmetry. Measure alternately, compare medians:

```bash
for i in $(seq 8); do
  for u in KNOWN zzz-NOSUCH; do
    t=$(curl -s -o /dev/null -w '%{time_total}' -X POST -d "user=$u&pass=x" "$BASE/login")
    echo "$u $t"
  done
done
```

Median(good) − median(bad) is the delta. bcrypt/argon2 give 50-500ms;
a fast hash gives a sub-10ms delta lost to jitter. See `timing-oracle.md`.

## Channel 4: side artifacts

- **`Set-Cookie`** — a session/error cookie set on one arm only
- **an email/send** — a "reset link sent" that fires only for real
  accounts (the response is uniform; the side effect is not)
- **a lockout** — repeated bad attempts lock only real accounts
- **a log/audit entry** — one arm writes a "failed login for KNOWN"
- **a JSON field** — `{"user_exists":true}`, `{"error_code":1001}` vs
  `1002`, `{"attempts_remaining":4}`

The side artifact is the subtlest channel — when text+timing are
equalized, the artifact still leaks.

## The per-channel falsifier

A channel is closed when: the same bad username twice gives byte-identical
output on that channel, AND a second different bad name gives the same
output. One anomalous read is noise; a repeated identical read is a
closed channel.
