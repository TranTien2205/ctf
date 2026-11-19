# Per-check token — the `client_id`-binding check, with the full mechanics

The per-check-token module names the `client_id`-binding check. This module
carries the full mechanics — the probe, the confirmation, the falsifier,
and the escalation.

## The check

The `client_id` is bound to the code — a code minted for one client works
on another. When the `client_id` is bound, a code minted for client A is
exchangeable by client B. When the `client_id` is not bound, the cross-client
shape is live.

## The probe

```bash
curl -X POST $IDP/token -d "grant_type=authorization_code&code=ABC&client_id=B&client_secret=SECRET_B&redirect_uri=https://app/callback"
```

The `client_id` is `B` — a code minted for client A exchanged as client B.
The `token` response is the check.

## The confirmation

```
HTTP/1.1 200 OK
{"access_token": "AT", "token_type": "Bearer", "expires_in": 3600}
```

A `200` + `{"access_token": "AT"}` — the token is issued for client B. The
`client_id` is not bound — the cross-client shape is live.

## The falsifier

```
HTTP/1.1 400 Bad Request
{"error": "invalid_client"}
```

A `400` naming the rejection — the `client_id` is bound to the code. The
cross-client shape is dead.

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
| `client_id` bound to code | `400 invalid_client` | dead |
| `client_id` not bound | `200` + `{"access_token": "AT"}` | live |
| `aud` verified | `400` on `aud=B` | dead |
| `aud` not verified | `id_token` with `aud=B` accepted | live |
