# Per-check binding — the `code`-binding check, with the full mechanics

The per-check-binding module names the `code`-binding check. This module
carries the full mechanics — the probe, the confirmation, the falsifier,
and the escalation.

## The check

The `code` is bound to `client_id`, `redirect_uri`, and `state`. When any
of these is not re-validated on exchange, a stolen code is exchangeable.

## The probe

```bash
# replay the stolen code — the code is bound to client_id, redirect_uri, and state
curl -i -b "$JAR" "$BASE/callback?code=STOLEN_CODE&state=XYZ"
```

The `code` is `STOLEN_CODE` — the code is bound to `client_id`,
`redirect_uri`, and `state`. The `callback` response is the check.

## The confirmation

```
HTTP/1.1 302 Found
Location: /dashboard
Set-Cookie: session=abc123; HttpOnly; Path=/
```

A `302` + `Set-Cookie: session=...` — the `code` is replayed; the `code` is
bound to `client_id`, `redirect_uri`, and `state`. The `code`-binding shape
is live.

## The falsifier

```
HTTP/1.1 400 Bad Request
{"error": "invalid_grant"}
```

A `400` naming the rejection — the `code` is bound to `client_id`,
`redirect_uri`, and `state`. The `code`-binding shape is dead.

## The escalation

Stolen-code exchange — a code minted with a challenge is exchangeable with
a wrong verifier.

## The evidence rules

- A `302` + `Set-Cookie: session=...` is the session confirmation.
- A `400` naming the rejection is the falsifier.
- A verbatim response excerpt is the evidence — the raw bytes, not a summary.

## The boundary conditions

| Condition | The evidence | The check |
|---|---|---|
| `code` bound to `client_id` | `400 invalid_client` | dead |
| `code` bound to `redirect_uri` | `400 invalid redirect_uri` | dead |
| `code` bound to `state` | `400 state mismatch` | dead |
| `code` not bound | `302` + `Set-Cookie: session=...` | live |
| `code` single-use | `400 invalid_grant` | dead |
| `code` short expiry | `400 invalid_grant` | dead |
