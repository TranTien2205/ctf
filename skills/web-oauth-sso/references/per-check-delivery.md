# Per-check delivery — the `delivery`-validation check, with the full mechanics

The per-check-delivery module names the `delivery`-validation check. This
module carries the full mechanics — the probe, the confirmation, the
falsifier, and the escalation.

## The check

The `delivery` is the mechanism that delivers the code — `query`, `fragment`,
`form_post`, `web_message`. When `response_mode` is not validated, the code
is delivered to a different surface.

## The probe

```bash
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code&state=XYZ&response_mode=form_post"
```

The `response_mode` is `form_post` — the code is delivered to a POST
endpoint. The `authorize` response is the check.

## The confirmation

```
HTTP/1.1 200 OK
```

A `200` + a form that POSTs `code=ABC&state=XYZ` to `https://app/callback` —
the code is delivered via `form_post`, not `query`. The `response_mode` is
not validated — the code is delivered to a different surface.

## The falsifier

```
HTTP/1.1 400 Bad Request
{"error": "response_mode not allowed"}
```

A `400` naming the rejection — the `response_mode` is validated. The
`response_mode` shape is dead.

## The escalation

`form_post` delivery — the code is delivered to a POST endpoint; the attacker
reads the `POST` body and replays the code.

## The evidence rules

- A `200` + a form that POSTs the code is the delivery.
- A `400` naming the rejection is the falsifier.
- A verbatim response excerpt is the evidence — the raw bytes, not a summary.

## The boundary conditions

| Condition | The evidence | The check |
|---|---|---|
| `response_mode` validated | `400 response_mode not allowed` | dead |
| `response_mode` not validated | `200` + `form_post` page | live |
| `response_type` allowlisted to `code` | `400 response_type not allowed` | dead for implicit |
| `response_type` not allowlisted | `302` + `Location: ...#access_token=ABC` | live |
