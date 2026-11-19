# Per-check response-mode — the `response_mode`-validation check, with the full mechanics

The per-check-response-mode module names the `response_mode`-validation check.
This module carries the full mechanics — the probe, the confirmation, the
falsifier, and the escalation.

## The check

`response_mode` names the delivery mode — `query`, `fragment`, `form_post`,
`web_message`. When `response_type` is allowlisted to `code`, the implicit
flow is not accepted — but `response_mode` may still be validated, delivering
the code to a different surface.

## The probe

```bash
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code&state=XYZ&response_mode=web_message"
```

The `response_mode` is `web_message` — the code is delivered to a `postMessage`
target. The `authorize` response is the check.

## The confirmation

```
HTTP/1.1 200 OK
```

A `200` + a page that `postMessage`s `code=ABC&state=XYZ` to the target
origin — the code is delivered via `web_message`, not `query`. The
`response_mode` is not validated — the code is delivered to a different
surface.

## The falsifier

```
HTTP/1.1 400 Bad Request
{"error": "response_mode not allowed"}
```

A `400` naming the rejection — the `response_mode` is validated. The
`response_mode` shape is dead.

## The escalation

`web_message` delivery — the code is delivered to a `postMessage` target;
the attacker reads the `postMessage` and replays the code.

## The evidence rules

- A `200` + a page that `postMessage`s the code is the delivery.
- A `400` naming the rejection is the falsifier.
- A verbatim response excerpt is the evidence — the raw bytes, not a summary.

## The boundary conditions

| Condition | The evidence | The check |
|---|---|---|
| `response_mode` validated | `400 response_mode not allowed` | dead |
| `response_mode` not validated | `200` + `postMessage` page | live |
| `response_type` allowlisted to `code` | `400 response_type not allowed` | dead for implicit |
| `response_type` not allowlisted | `302` + `Location: ...#access_token=ABC` | live |
