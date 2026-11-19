# Form surface — every account-touching form, ranked by leak

## The inventory, cheapest-leak first

### 1. check-username / availability endpoints — the direct oracle

`/check-username`, `/username-available`, `/api/user-exists`,
`/api/validate-username`, `/api/check-email`, a `?available=` query.
These exist to tell a signup form whether a name is taken — they are a
direct exists-oracle with no credential needed:

```bash
curl -s "$BASE/api/check-username?u=KNOWN"
curl -s "$BASE/api/check-username?u=zzz-NOSUCH"
# {"available":false} vs {"available":true}  ->  a direct oracle
```

### 2. registration

`POST /register` with a taken vs a free username:

```bash
curl -s -X POST -d 'user=KNOWN&email=a@b.c&pass=x' "$BASE/register"
curl -s -X POST -d 'user=zzz-NOSUCH&email=a@b.c&pass=x' "$BASE/register"
```

A `"username already taken"` / `"email already registered"` on the known
arm is the oracle — register leaks what login often does not.

### 3. password reset / forgot

`POST /forgot-password` / `/reset`:

- `"Reset link sent"` only for real accounts (or a send side-effect)
- `"No account with that email"` vs a uniform "if exists, sent"
- a timing gap — the send/lookup runs only for a real row

### 4. login

`POST /login` — the headline form, usually the most hardened. Check all
four channels; the register/reset often leaks first.

### 5. forgot-username / reactivate / unlock

`POST /forgot-username`, `/reactivate`, `/unlock` — "a reminder was sent"
vs "no such account"; "account unlocked" vs "no locked account".

### 6. contact / invite

`POST /invite`, `/contact`, a "refer a friend" — "that email is already
a member" vs a generic "invitation sent".

### 7. MFA / OTP

`POST /mfa`, `/2fa`, `/send-otp` — "code sent" only for real accounts,
or a "no such account" vs "enter your code".

### 8. API / GraphQL

- `POST /api/login`, `/api/token`, `/api/auth` — JSON differential
- `mutation { login }`, `query { userByEmail }`, `query { checkUser }`

## The per-form probe rule

For each form: same known-good vs same known-bad vs repeated-bad, other
fields held constant, ALL four channels measured. A form that leaks is
a separate finding from the one that does not — record per-form, not
per-app.
