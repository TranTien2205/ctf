# Detection — when to open this class

## The entry signals

- a **login**, **registration**, **password-reset**, or **contact/**"
  **forgot-username** form
- a `?next=`/`?redirect=` on the login — the app distinguishes auth states
- an API endpoint that takes a username/email/id and a credential
- a `Sign up` / `Create account` / `Reset password` / `Forgot password` link
- an error that mentions an account ("no such user", "wrong password",
  "account locked", "email not found")
- a `/users/check`, `/api/user-exists`, `/api/username-available`,
  `/check-email`, `/validate-username` endpoint — a direct exists-oracle

## The three-way probe — the entry measurement

```bash
# known-good, known-bad, repeated-bad — same form, same other fields
curl -i -X POST -d 'user=KNOWN&pass=x' "$BASE/login"  > good
curl -i -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/login" > bad1
curl -i -X POST -d 'user=zzz-NOSUCH&pass=x' "$BASE/login" > bad2
```

Measure every channel: body bytes, status, `Location`, `Set-Cookie`,
elapsed. A difference between `good` and `bad` that also appears between
`good` and `bad2` (i.e., `bad1`==`bad2`, both != `good`) is the oracle.

## enum_probe — the oracle tool

```bash
python3 tools/web/enum_probe.py --url "$BASE/login" \
  --body 'user={U}&pass=x' --pass-field 'pass=x' \
  --known-user 'admin' --method POST
```

It sends the known-user against four random usernames and reports which
channel separates them — status, body signature+length, or elapsed —
with verbatim excerpts. A uniform result is a real negative, not a
no-signal.

## What detection is NOT

A single different-looking response is not detection — it could be a
crash, a CSRF failure, a honeypot field. Detection requires the
difference to *repeat* on the same bad username twice and to *track* the
username across a second bad name.

## The recognize-vs-confirm boundary

Recognition = "the form could distinguish". Confirmation = "measured a
repeatable difference on a channel". Do not report enumeration from a
single anomalous response; report it from a repeated, channel-identified
delta.
