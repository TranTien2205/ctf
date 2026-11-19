# Registration and reset enumeration — the forms that leak first

## Registration — the taken-name oracle

A signup form must tell the user a name is taken — that check is the
oracle, usually unauthenticated and unhardened.

```bash
curl -s -X POST -d 'user=KNOWN&email=KNOWN@x.c&pass=x&pass2=x' "$BASE/register" > rg
curl -s -X POST -d 'user=zzz-NOSUCH&email=zzz@x.c&pass=x&pass2=x' "$BASE/register" > rb
diff rg rb
```

The leaks:
- `"username already taken"` / `"email already registered"` — direct
- a `409 Conflict` / `422` vs `201` / `302` — status
- an inline `aria-invalid` / a `?taken=1` redirect
- a client-side `fetch('/check-username')` the register page makes —
  that endpoint is the direct oracle (`form-surface.md` #1)
- a timing gap — a duplicate-key check vs an insert attempt

The registration oracle is often stronger than login's: the form is
BUILT to reveal availability.

## Password reset / forgot — the exists oracle

```bash
curl -i -X POST -d 'email=KNOWN@x.c' "$BASE/forgot-password" > fg
curl -i -X POST -d 'email=zzz@x.c'   "$BASE/forgot-password" > fb
diff fg fb
```

- `"If that account exists…"` — a hardened uniform message; then check
  timing (the send runs only for a real row) and the side channel (does
  YOUR email get it)
- `"No account with that email"` / `"account found"` — direct text
- a `302 /check-email` only on the real arm
- `{"sent":true}` vs `{"sent":false}` — JSON

## forgot-username / unlock / reactivate

`POST /forgot-username` — "we emailed your username" vs "no such email".
`/unlock` — "account unlocked" vs "no locked account found". Both are
exists-oracles on an often-unhardened form.

## The send side-effect as the real signal

A truly uniform response still sends the email/OTP only to a real
account. On an owned target: submit YOUR address and a random address,
confirm only yours receives (or the response carries `emails_sent`/`to`
/`queued` differently). The side effect is the oracle when every
response channel is equal.

## The per-form record

`register: text: "username taken" vs none` / `reset: timing: +180ms` —
each form's oracle is recorded separately; the weakest form is the
enumeration path.
