# Per-check flow — the `flow`-shape check, with the full mechanics

The per-check-flow module names the `flow`-shape check. This module carries
the full mechanics — the probe, the confirmation, the falsifier, and the
escalation.

## The check

The `flow` is the OAuth flow shape — `code`, `token`, `id_token`, `code token`,
`code id_token`, `token id_token`, `code token id_token`. When `response_type`
is not allowlisted, the implicit or hybrid flow is accepted.

## The probe

```bash
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code%20token&state=XYZ&nonce=N"
```

The `response_type` is `code token` — the hybrid flow. The `authorize`
response is the check.

## The confirmation

```
HTTP/1.1 302 Found
Location: https://app/callback#code=ABC&access_token=ABC&state=XYZ
```

A `302` + `Location: https://app/callback#code=ABC&access_token=ABC` — the
hybrid flow is accepted; the code and the token are in the fragment. The
`response_type` is not allowlisted — the hybrid flow is live.

## The falsifier

```
HTTP/1.1 400 Bad Request
{"error": "response_type not allowed"}
```

A `400` naming the rejection — the `response_type` is allowlisted to `code`.
The hybrid flow is dead.

## The escalation

Fragment-harvest — the callback page loads a subresource; the `Referer`
carries the fragment; the code and the token are leaked.

## The evidence rules

- A `302` + `Location: ...#code=ABC&access_token=ABC` is the token delivery.
- A `400` naming the rejection is the falsifier.
- A verbatim response excerpt is the evidence — the raw bytes, not a summary.

## The boundary conditions

| Condition | The evidence | The check |
|---|---|---|
| `response_type` allowlisted to `code` | `400 response_type not allowed` | dead |
| `response_type` not allowlisted | `302` + `Location: ...#code=ABC&access_token=ABC` | live |
| `response_mode` validated | `400 response_mode not allowed` | dead |
| `response_mode` not validated | `200` + `form_post`/`web_message` page | live |
