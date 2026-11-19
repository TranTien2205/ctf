# Per-check scope — the `scope`-allowlist check, with the full mechanics

The per-check-scope module names the `scope`-allowlist check. This module
carries the full mechanics — the probe, the confirmation, the falsifier,
and the escalation.

## The check

`scope` names the permissions the token carries. When it is allowlisted per
client, the token carries only what was requested. When it is not allowlisted,
a broader scope is accepted — the token carries broader permissions.

## The probe

```bash
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code&state=XYZ&scope=openid+admin"
```

The `scope` is `openid+admin` — a broader scope. The `authorize` response is
the check.

## The confirmation

```
HTTP/1.1 302 Found
Location: https://app/callback?code=ABC&state=XYZ
```

A `302` + `Location: https://app/callback?code=ABC` — the broader scope is
accepted; the `id_token` carries `scope=openid+admin`. The scope-escalation
shape is live.

## The falsifier

```
HTTP/1.1 400 Bad Request
{"error": "scope not allowed"}
```

A `400` naming the rejection — the `scope` is allowlisted. The
scope-escalation shape is dead.

## The escalation

Broader token — the token carries a broader scope; check what the broader
scope unlocks on the app's endpoints.

## The evidence rules

- A `302` + `Location: ...?code=ABC` is the code delivery.
- A `400` naming the rejection is the falsifier.
- A verbatim response excerpt is the evidence — the raw bytes, not a summary.

## The boundary conditions

| Condition | The evidence | The check |
|---|---|---|
| `scope` allowlisted | `400 scope not allowed` | dead |
| `scope` not allowlisted | `302` + `Location: ...?code=ABC` | live |
| `scope=offline_access` accepted | `200` + `refresh_token` | live on the refresh surface |
| `scope` broader but unused | `id_token` carries `scope=openid+admin` but the app's endpoints do not check `scope` | live but unused |
