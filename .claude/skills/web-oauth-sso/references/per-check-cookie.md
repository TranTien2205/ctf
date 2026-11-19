# Per-check cookie — the `SameSite`-validation check, with the full mechanics

The per-check-cookie module names the `SameSite`-validation check. This
module carries the full mechanics — the probe, the confirmation, the
falsifier, and the escalation.

## The check

`SameSite` controls whether the cookie is sent on cross-site requests. When
it is `Lax` or `Strict`, the cross-site write does not land. When it is
missing or `None`, the cross-site write lands — the cookie-swap shape is
live.

## The probe

```bash
grep -i "Set-Cookie.*token\|Set-Cookie.*sso\|Set-Cookie.*auth" transcript.txt
```

The `Set-Cookie` header on the IdP's login response is the check.

## The confirmation

```
HTTP/1.1 200 OK
Set-Cookie: token=NEW_TOKEN; HttpOnly; Path=/
{"status": "ok"}
```

A `200` + `Set-Cookie: token=NEW` — the `SameSite` is missing or `None`; the
cross-site write lands. The cookie-swap shape is live.

## The falsifier

```
Set-Cookie: token=ABC; HttpOnly; SameSite=Lax; Secure; Path=/
```

`SameSite=Lax` or `Strict` — the cross-site write does not land. The
cookie-swap shape is dead.

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
| `SameSite=Lax` | `SameSite=Lax` on the IdP token | dead for POST; live for GET |
| `SameSite=Strict` | `SameSite=Strict` on the IdP token | dead |
| `SameSite` missing | `SameSite` missing on the IdP token | live |
| `SameSite=None` | `SameSite=None` on the IdP token | live |
| `Secure` required | `Secure` missing on the IdP token | live over HTTP |
