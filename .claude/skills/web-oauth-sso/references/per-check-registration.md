# Per-check registration — the registration-idempotency check, with the full mechanics

The per-check-registration module names the registration-idempotency check.
This module carries the full mechanics — the probe, the confirmation, the
falsifier, and the escalation.

## The check

The registration endpoint allows pre-registration of a fixed account. When
the registration is idempotent — a duplicate registration returns the same
account — the pre-registration race cannot win a different password. When
the registration is not idempotent — a duplicate registration returns a new
account — the pre-registration race lands on the attacker's account.

## The probe

```bash
# register the same account twice
curl -X POST $BASE/api/register -d '{"email":"student@domain","password":"own","username":"student"}'
curl -X POST $BASE/api/register -d '{"email":"student@domain","password":"different","username":"student"}'
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
{"status": "registered", "account_id": "new_id"}
```

A `200` + `{"status": "registered"}` — the account is registered; the
registration is not idempotent. The pre-registration race is live.

## The falsifier

```
HTTP/1.1 409 Conflict
{"error": "account already exists"}
```

A `409` naming the conflict — the account is already registered; the
registration is idempotent. The pre-registration race is dead.

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
| registration idempotent | `409 Conflict` | dead |
| registration not idempotent | `200` + `{"status": "registered"}` | live |
| linking on `email` | `200` + `{"status": "registered"}` | live |
| linking on `sub` | `409 Conflict` | dead |
| `email_verified` enforced | `400 email not verified` | dead |
