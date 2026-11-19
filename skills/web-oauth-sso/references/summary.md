# Summary — the web-oauth-sso skill at a glance

The web-oauth-sso skill is the OAuth/SSO depth skill — the delegation
mechanism that trusts the IdP's identity. It covers the authorization-code
flow, the implicit flow, the PKCE flow, the OIDC `id_token`, the cookie
model, the linking model, and the multi-step chains that reach the sink.

## The verified anchor

`htb-ssos-oauth-registration-race-cookie-swap-json-csrf` — the SSOS chain:
registration race → `data:text/html` `text/plain` JSON login → `loginSSO`
cookie swap → flag submit.

## The mechanism alphabet

| Mechanism | The artifact | The falsifier |
|---|---|---|
| state CSRF | `state` in authorize + callback | `state` bound to session |
| redirect interception | `redirect_uri` in authorize | `redirect_uri` exact match |
| cookie swap | `SameSite` on IdP token + `loginSSO` ignores credentials | `SameSite=Lax|Strict` |
| account linking | `email`/`username`/`sub` in `id_token` | linking on `sub` |
| implicit leak | `response_type` + `access_token` in fragment | `response_type` code-only |
| PKCE bypass | `code_challenge` + `code_verifier` | `S256` + verifier re-validated |
| cross-client | `client_id` + `aud` in `id_token` | `client_id` bound + `aud` verified |
| scope escalation | `scope` in authorize + token | `scope` allowlisted |
| registration race | `email`/`username` in registration | registration idempotent |
| device flow | `device_code` + `user_code` | device flow disabled |
| refresh replay | `refresh_token` in token request | refresh token bound |
| logout forge | `logout_token`/`sid` in backchannel | `logout_token` signature verified |

## The falsifier sweep

```bash
# falsifier 1 — state binding
curl -i -b "$JAR" "$BASE/callback?code=ABC&state=DIFFERENT"

# falsifier 2 — redirect_uri validation
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://evil.com/callback&response_type=code&state=XYZ"

# falsifier 3 — SameSite on the SSO token
grep -i "Set-Cookie.*token\|Set-Cookie.*sso\|Set-Cookie.*auth" transcript.txt

# falsifier 4 — response_type allowlist
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=token&state=XYZ&nonce=N"

# falsifier 5 — PKCE required
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code&state=XYZ"
```

## The decision tree

```
Is there a second cookie (IdP token) in the jar?
  YES → check SameSite → missing/None → cookie-swap shape live
  NO  → single-cookie model → move to state/redirect_uri

Is state bound to session?
  NO  → state CSRF live → login-CSRF or linking-CSRF
  YES → falsifier → move to redirect_uri

Is redirect_uri strictly validated?
  NO  → code-interception live
  YES → falsifier → move to account linking

Is linking on email/username?
  YES → pre-registration race live
  NO  → falsifier → move to implicit/PKCE/cross-client

Is response_type allowlisted to code?
  NO  → implicit-leak live → fragment-harvest
  YES → falsifier → move to PKCE

Is PKCE required + S256 + verifier re-validated?
  NO  → PKCE-bypass live → stolen-code exchange
  YES → falsifier → move to cross-client

Is code bound to client_id + aud verified?
  NO  → cross-client live → code replay
  YES → falsifier → reclassify
```

## The evidence rules

- A `302` + `Set-Cookie: session=...` is the session confirmation.
- A `302` + `Location: ...?code=...` is the code delivery.
- A `200` + `{"access_token": ...}` is the token confirmation.
- A `200` + `Set-Cookie: token=...` is the cookie confirmation.
- A `400` naming the mismatch is the falsifier.
- A `302` to a login page is a negative, not a falsifier.
- A verbatim response excerpt is the evidence — the raw bytes, not a summary.

## The budget

- Per mechanism class: five probes or fifteen active minutes.
- Whole challenge: twenty-five probes or forty-five active minutes.
- Relabeling does not reset the whole-challenge budget.
- Parking time is not charged.

## The escalation order

`chain_match`, `reclassify`, `writeup_search`, `novel_plan`, `fanout_sweep`,
`solver_handoff`. `stop_report` only fires once all escalation rungs are
exhausted.
