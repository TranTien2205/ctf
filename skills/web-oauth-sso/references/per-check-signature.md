# Per-check signature — the `signature`-verification check, with the full mechanics

The per-check-signature module names the `signature`-verification check.
This module carries the full mechanics — the probe, the confirmation, the
falsifier, and the escalation.

## The check

The `signature` on the `id_token` is verified — the `alg` is not `none`, the
signature is valid, the `aud`/`iss`/`exp`/`nonce` are validated. When the
signature is not verified, the `id_token` is forgeable.

## The probe

```bash
# decode the id_token — read the alg claim
echo "$ID_TOKEN" | cut -d'.' -f1 | base64 -d 2>/dev/null | jq .alg
```

The `alg` claim in the `id_token` is the check.

## The confirmation

```
HTTP/1.1 200 OK
{"access_token": "AT", "token_type": "Bearer", "expires_in": 3600}
```

A `200` + `{"access_token": "AT"}` — the `id_token` with `alg=none` is
accepted. The `signature` is not verified — the `id_token` is forgeable.

## The falsifier

```
HTTP/1.1 400 Bad Request
{"error": "invalid signature"}
```

A `400` naming the rejection — the `signature` is verified. The `id_token`
forge shape is dead.

## The escalation

`id_token` forge — the `id_token` is forgeable; the `sub` claim is
attacker-controlled; the session is issued on the attacker's account.

## The evidence rules

- A `200` + `{"access_token": "AT"}` is the token confirmation.
- A `400` naming the rejection is the falsifier.
- A verbatim response excerpt is the evidence — the raw bytes, not a summary.

## The boundary conditions

| Condition | The evidence | The check |
|---|---|---|
| `signature` verified | `400` on `alg=none` | dead |
| `signature` not verified | `id_token` with `alg=none` accepted | live |
| `alg=none` accepted | `id_token` with `alg=none` accepted | live |
| `aud` verified | `400` on `aud=B` | dead |
| `iss` verified | `400` on `iss=evil.com` | dead |
| `nonce` validated | `400` on `nonce` mismatch | dead |
