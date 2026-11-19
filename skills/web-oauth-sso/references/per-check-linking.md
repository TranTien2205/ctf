# Per-check linking — the account-linking check, with the full mechanics

The per-check-linking module names the account-linking check. This module
carries the full mechanics — the probe, the confirmation, the falsifier,
and the escalation.

## The check

The app links the IdP's identity to a local account. The linking field is
`email`/`username`/`sub`. When the linking is on `email`/`username`, the
pre-registration race lands on the attacker's account. When the linking is
on `sub`, the race is dead.

## The probe

```bash
# register the target account with the same email
curl -X POST $BASE/api/register -d '{"email":"student@domain","password":"own","username":"student"}'
# complete the OAuth flow — the session lands on the sub-mapped account
curl -b $JAR -L $BASE/login
```

The `register` endpoint's response is the check.

## The confirmation

```
HTTP/1.1 200 OK
{"status": "registered"}
```

followed by:

```
HTTP/1.1 200 OK
{"session": "abc123"}
```

A `200` + `{"status": "registered"}` — the account is registered; the OAuth
login lands on the attacker's account. The linking is on `email`/`username` —
the pre-registration race is live.

## The falsifier

```
HTTP/1.1 409 Conflict
{"error": "account already exists"}
```

A `409` naming the conflict — the account is already registered; the linking
is on `sub`, not `email`. The pre-registration race is dead.

## The escalation

Pre-registration race — the attacker hammers `POST /api/register` for the
bot's account before the bot's `registerUser` step runs; the OAuth login
lands on the attacker's account; the flag is submitted into the attacker's
owned account.

## The evidence rules

- A `200` + `{"status": "registered"}` is the registration confirmation.
- A `409` naming the conflict is the falsifier.
- A `302` + `Location: /dashboard` is the session confirmation — the session
  lands on the `sub`-mapped account, not the pre-registered one.
- A verbatim response excerpt is the evidence — the raw bytes, not a summary.

## The boundary conditions

| Condition | The evidence | The check |
|---|---|---|
| linking on `email` | `200` + `{"status": "registered"}` | live |
| linking on `username` | `200` + `{"status": "registered"}` | live |
| linking on `sub` | `409 Conflict` | dead |
| `email_verified` enforced | `400 email not verified` | dead |
| registration idempotent | `409 Conflict` | dead |
