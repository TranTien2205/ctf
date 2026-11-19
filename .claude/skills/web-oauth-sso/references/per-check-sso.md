# Per-check SSO — the `loginSSO`-check, with the full mechanics

The per-check-sso module names the `loginSSO`-check. This module carries
the full mechanics — the probe, the confirmation, the falsifier, and the
escalation.

## The check

`loginSSO` is the app's login step — it reads the jar's token and issues a
session. When `loginSSO` ignores credentials and reads the jar's token, a
cross-site write overwrites the token. When `loginSSO` reads credentials,
the cross-site write is dead.

## The probe

```bash
curl -X POST $IDP/api/login -H "Content-Type: text/plain" -d '{"email":"student@domain","password":"own"}'
```

The `POST /api/login` `Content-Type: text/plain` is the probe — the raw JSON
lands; the `Set-Cookie` overwrites the shared jar's token.

## The confirmation

```
HTTP/1.1 200 OK
Set-Cookie: token=NEW_TOKEN; HttpOnly; Path=/
{"status": "ok"}
```

A `200` + `Set-Cookie: token=NEW` — the `loginSSO` reads the jar's token;
the cross-site write lands. The cookie-swap shape is live.

## The falsifier

```
Set-Cookie: token=ABC; HttpOnly; SameSite=Lax; Secure; Path=/
```

`SameSite=Lax|Strict` on the IdP token — the cross-site write does not land.
The cookie-swap shape is dead.

## The escalation

`data:text/html` URL carries a form that POSTs to the IdP's `/api/login` —
the `Set-Cookie` overwrites the shared jar's token; the `loginSSO` step
uses the swapped token.

## The evidence rules

- A `200` + `Set-Cookie: token=NEW` is the cookie confirmation.
- `SameSite=Lax|Strict` is the falsifier.
- A verbatim response excerpt is the evidence — the raw bytes, not a summary.

## The boundary conditions

| Condition | The evidence | The check |
|---|---|---|
| `loginSSO` reads jar token | `200` + `Set-Cookie: token=NEW` | live |
| `loginSSO` reads credentials | `200` + `Set-Cookie: session=...` | dead |
| `SameSite` missing | `Set-Cookie: token=NEW` | live |
| `SameSite` `Lax` | `SameSite=Lax` on the IdP token | dead for POST; live for GET |
| `SameSite` `Strict` | `SameSite=Strict` on the IdP token | dead |
