# Per-check exchange — the `token`-exchange check, with the full mechanics

The per-check-exchange module names the `token`-exchange check. This module
carries the full mechanics — the probe, the confirmation, the falsifier,
and the escalation.

## The check

The `token` exchange binds the code to `client_id`, `redirect_uri`, and
`code_verifier`. When any of these is not re-validated on exchange, a stolen
code is exchangeable.

## The probe

```bash
curl -X POST $IDP/token -d "grant_type=authorization_code&code=ABC&client_id=APP&client_secret=SECRET&redirect_uri=https://app/callback&code_verifier=WRONG"
```

The `code_verifier` is `WRONG` — the `code_verifier` is not re-validated.
The `token` response is the check.

## The confirmation

```
HTTP/1.1 200 OK
{"access_token": "AT", "token_type": "Bearer", "expires_in": 3600}
```

A `200` + `{"access_token": "AT"}` — the `code_verifier` is not re-validated.
The PKCE-bypass shape is live.

## The falsifier

```
HTTP/1.1 400 Bad Request
{"error": "invalid_grant"}
```

A `400` naming the rejection — the `code_verifier` is re-validated. The
PKCE-bypass shape is dead.

## The escalation

Stolen-code exchange — a code minted with a challenge is exchangeable with
a wrong verifier.

## The evidence rules

- A `200` + `{"access_token": "AT"}` is the token confirmation.
- A `400` naming the rejection is the falsifier.
- A verbatim response excerpt is the evidence — the raw bytes, not a summary.

## The boundary conditions

| Condition | The evidence | The check |
|---|---|---|
| `code_verifier` re-validated | `400 invalid_grant` | dead |
| `code_verifier` not re-validated | `200` + `{"access_token": "AT"}` | live |
| `code_challenge` required | `400 code_challenge required` | dead |
| `code_challenge` not required | `302` + `Location: ...?code=ABC` | live |
| `client_id` bound to code | `400 invalid_client` | dead |
| `client_id` not bound | `200` + `{"access_token": "AT"}` | live |
| `redirect_uri` validated on authorize, not on exchange | `token` request with `redirect_uri=https://evil.com` | live on the exchange surface |
