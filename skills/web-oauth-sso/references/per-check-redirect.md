# Per-check redirect — the `redirect_uri`-validation check, with the full mechanics

The per-check-redirect module names the `redirect_uri`-validation check.
This module carries the full mechanics — the probe, the confirmation, the
falsifier, and the escalation.

## The check

`redirect_uri` names where the code is delivered. When it is an exact match
against a registered allowlist, the code is delivered only to the registered
URI. When it is not validated, the code is delivered to an attacker URI.

## The probe

```bash
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://evil.com/callback&response_type=code&state=XYZ"
```

The `redirect_uri` is `https://evil.com/callback` — a URI not in the
registered allowlist. The `authorize` response is the check.

## The confirmation

```
HTTP/1.1 302 Found
Location: https://evil.com/callback?code=ABC&state=XYZ
```

A `302` + `Location: https://evil.com/callback?code=ABC` — the code is
delivered to the attacker. The `redirect_uri` is not validated — the
code-interception shape is live.

## The falsifier

```
HTTP/1.1 400 Bad Request
{"error": "invalid redirect_uri"}
```

A `400` naming the invalid URI — the `redirect_uri` is validated exactly.
The code-interception shape is dead.

## The escalation

Code-interception — the code is delivered to the attacker's endpoint;
replay it against the app's callback.

## The evidence rules

- A `302` + `Location: https://evil.com/callback?code=ABC` is the code
  delivery.
- A `400` naming the invalid URI is the falsifier.
- A `302` to a login page is a negative, not a falsifier.
- A verbatim response excerpt is the evidence — the raw bytes, not a summary.

## The boundary conditions

| Condition | The evidence | The check |
|---|---|---|
| `redirect_uri` exact match | `400 invalid redirect_uri` | dead |
| `redirect_uri` prefix match | `302` + `Location: https://app.evil.com?code=ABC` | live on the prefix surface |
| `redirect_uri` subdomain match | `302` + `Location: https://sub.app?code=ABC` | live on the subdomain surface |
| `redirect_uri` wildcard | `302` + `Location: https://anything?code=ABC` | live |
| `redirect_uri` validated on authorize, not on exchange | `token` request with `redirect_uri=https://evil.com` | live on the exchange surface |
