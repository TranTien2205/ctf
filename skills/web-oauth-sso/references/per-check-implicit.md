# Per-check implicit — the `response_type`-allowlist check, with the full mechanics

The per-check-implicit module names the `response_type`-allowlist check.
This module carries the full mechanics — the probe, the confirmation, the
falsifier, and the escalation.

## The check

`response_type` names the flow shape. When it is allowlisted to `code` only,
the implicit flow is not accepted — the token is never in the fragment, and
the leak surface is closed. When it is not allowlisted, the implicit flow is
accepted — the token is in the fragment.

## The probe

```bash
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=token&state=XYZ&nonce=N"
```

The `response_type` is `token` — an implicit-flow request. The `authorize`
response is the check.

## The confirmation

```
HTTP/1.1 302 Found
Location: https://app/callback#access_token=ABC&token_type=Bearer&expires_in=3600
```

A `302` + `Location: https://app/callback#access_token=ABC` — the token is
in the fragment. The implicit flow is accepted — the leak surface is live.

## The falsifier

```
HTTP/1.1 400 Bad Request
{"error": "response_type not allowed"}
```

A `400` naming the rejection — the `response_type` is allowlisted to `code`.
The implicit flow is dead.

## The escalation

Fragment-harvest — the callback page loads a subresource; the `Referer`
carries the fragment; the token is leaked.

## The evidence rules

- A `302` + `Location: ...#access_token=ABC` is the token delivery.
- A `400` naming the rejection is the falsifier.
- A verbatim response excerpt is the evidence — the raw bytes, not a summary.

## The boundary conditions

| Condition | The evidence | The check |
|---|---|---|
| `response_type` allowlisted to `code` | `400 response_type not allowed` | dead |
| `response_type` not allowlisted | `302` + `Location: ...#access_token=ABC` | live |
| `response_type` hybrid | `302` + `Location: ...#code=ABC&access_token=ABC` | live |
| `response_mode` not validated | `302` + `Location: ...?code=ABC` via `form_post`/`web_message` | live on the delivery surface |
