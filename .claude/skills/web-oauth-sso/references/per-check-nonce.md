# Per-check nonce — the `nonce`-validation check, with the full mechanics

The per-check-nonce module names the `nonce`-validation check. This module
carries the full mechanics — the probe, the confirmation, the falsifier,
and the escalation.

## The check

The `nonce` is the replay binding — the random value that binds the
`id_token` to the request. When the `nonce` is bound to the `id_token` it
was minted for, a replayed `id_token` carries its own `nonce`. When the
`nonce` is bound to the request, a replayed `id_token` is rejected.

## The probe

```bash
# replay the id_token — the nonce is bound to the id_token, not the request
curl -i -b "$JAR" "$BASE/callback?id_token=REPLAYED_ID_TOKEN&state=XYZ"
```

The `id_token` is replayed — the `nonce` is bound to the `id_token`, not the
request. The `callback` response is the check.

## The confirmation

```
HTTP/1.1 302 Found
Location: /dashboard
Set-Cookie: session=abc123; HttpOnly; Path=/
```

A `302` + `Set-Cookie: session=...` — the `id_token` is replayed; the
`nonce` is bound to the `id_token`, not the request. The `nonce`-validation
shape is live.

## The falsifier

```
HTTP/1.1 400 Bad Request
{"error": "nonce mismatch"}
```

A `400` naming the mismatch — the `nonce` is bound to the request. The
`nonce`-validation shape is dead.

## The escalation

`id_token` replay — the `id_token` is replayed; the `nonce` is bound to the
`id_token`, not the request; the session is issued on the attacker's account.

## The evidence rules

- A `302` + `Set-Cookie: session=...` is the session confirmation.
- A `400` naming the mismatch is the falsifier.
- A verbatim response excerpt is the evidence — the raw bytes, not a summary.

## The boundary conditions

| Condition | The evidence | The check |
|---|---|---|
| `nonce` bound to `id_token` | `302` + `Set-Cookie: session=...` | live |
| `nonce` bound to request | `400 nonce mismatch` | dead |
| `nonce` validated | `400` on `nonce` mismatch | dead |
| `nonce` not validated | `302` + `Set-Cookie: session=...` | live |
