# Per-check client — the `aud`-verification check, with the full mechanics

The per-check-client module names the `aud`-verification check. This module
carries the full mechanics — the probe, the confirmation, the falsifier,
and the escalation.

## The check

The `aud` claim in the `id_token` names which client the token is for. When
the `aud` is verified, a `id_token` minted for client A is rejected by client
B. When the `aud` is not verified, the cross-client shape is live.

## The probe

```bash
# decode the id_token — read the aud claim
echo "$ID_TOKEN" | cut -d'.' -f2 | base64 -d 2>/dev/null | jq .aud
```

The `aud` claim in the `id_token` is the check.

## The confirmation

```
HTTP/1.1 200 OK
{"access_token": "AT", "token_type": "Bearer", "expires_in": 3600}
```

A `200` + `{"access_token": "AT"}` — the `id_token` with `aud=B` is accepted.
The `aud` is not verified — the cross-client shape is live.

## The falsifier

```
HTTP/1.1 400 Bad Request
{"error": "aud mismatch"}
```

A `400` naming the rejection — the `aud` is verified. The cross-client shape
is dead.

## The escalation

Code replay — a code minted for client A is replayable by client B; the
`id_token` with `aud=B` is accepted.

## The evidence rules

- A `200` + `{"access_token": "AT"}` is the token confirmation.
- A `400` naming the rejection is the falsifier.
- A verbatim response excerpt is the evidence — the raw bytes, not a summary.

## The boundary conditions

| Condition | The evidence | The check |
|---|---|---|
| `aud` verified | `400` on `aud=B` | dead |
| `aud` not verified | `id_token` with `aud=B` accepted | live |
| `client_id` bound to code | `400 invalid_client` | dead |
| `client_id` not bound | `200` + `{"access_token": "AT"}` | live |
