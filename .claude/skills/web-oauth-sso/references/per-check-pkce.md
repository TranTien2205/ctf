# Per-check PKCE — the `code_challenge`-validation check, with the full mechanics

The per-check-pkce module names the `code_challenge`-validation check. This
module carries the full mechanics — the probe, the confirmation, the
falsifier, and the escalation.

## The check

PKCE binds the code exchange to the same client that started the flow. When
`code_challenge` is required, `code_challenge_method` is `S256` (not `plain`),
and `code_verifier` is re-validated on exchange, a stolen code is not
exchangeable. When any of these is missing, the PKCE shape is live.

## The probe

```bash
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code&state=XYZ"
```

The `code_challenge` is missing — the PKCE requirement is the check.

## The confirmation

```
HTTP/1.1 302 Found
Location: https://app/callback?code=ABC&state=XYZ
```

A `302` + `Location: https://app/callback?code=ABC` — the `code_challenge`
is not required. The PKCE shape is live.

## The falsifier

```
HTTP/1.1 400 Bad Request
{"error": "code_challenge required"}
```

A `400` naming the requirement — the `code_challenge` is required. The PKCE
shape is dead.

## The escalation

Stolen-code exchange — the verifier is captured from the URL or the browser
history; the code is exchangeable.

## The evidence rules

- A `302` + `Location: ...?code=ABC` is the code delivery.
- A `400` naming the requirement is the falsifier.
- A verbatim response excerpt is the evidence — the raw bytes, not a summary.

## The boundary conditions

| Condition | The evidence | The check |
|---|---|---|
| `code_challenge` required | `400 code_challenge required` | dead |
| `code_challenge` not required | `302` + `Location: ...?code=ABC` | live |
| `code_challenge_method` S256 | `400 code_challenge_method must be S256` | dead for `plain` |
| `code_challenge_method` plain | `302` + `Location: ...?code=ABC` | live |
| `code_verifier` re-validated | `400 invalid_grant` | dead |
| `code_verifier` not re-validated | `200` + `{"access_token": "AT"}` | live |
