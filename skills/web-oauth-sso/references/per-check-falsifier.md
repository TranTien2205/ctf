# Per-check falsifier — the OAuth falsifiers by mechanism, with the full mechanics

The per-check-falsifier module names the falsifier for each mechanism. This
module carries the full mechanics — the probe, the expected falsifier, the
evidence, and the reclassification.

## The falsifier map

| Mechanism | The probe | The falsifier | The reclassification |
|---|---|---|---|
| state CSRF | `callback?code=ABC&state=DIFFERENT` | `400 state mismatch` | `web-csrf` |
| redirect interception | `authorize?...&redirect_uri=https://evil.com` | `400 invalid redirect_uri` | `web-open-redirect` |
| cookie swap | `POST /api/login` `Content-Type: text/plain` | `Set-Cookie` not issued | `web-auth-session` |
| account linking | `register` the target account | `409 Conflict` | `web-race-condition` |
| implicit leak | `authorize?...&response_type=token` | `400 response_type not allowed` | `web-auth-session` |
| PKCE bypass | `authorize?...&code_challenge_method=plain` | `400 code_challenge_method must be S256` | `web-auth-session` |
| cross-client | `token` request with `client_id=B` | `400 invalid_client` | `web-auth-session` |
| scope escalation | `authorize?...&scope=openid+admin` | `400 scope not allowed` | `web-auth-session` |
| registration race | `register` the same account twice | `409 Conflict` | `web-race-condition` |
| device flow | `POST /token` `grant_type=urn:ietf:params:oauth:grant-type:device_code` | `400` | `web-auth-session` |
| refresh replay | `POST /token` `grant_type=refresh_token` | `400` | `web-auth-session` |
| logout forge | `POST /logout` `logout_token=FORGED` | `400` | `web-auth-session` |

## Falsifier 1 — `state` bound to session

**The probe**:

```bash
curl -i -b "$JAR" "$BASE/callback?code=ABC&state=DIFFERENT"
```

**The falsifier**:

```
HTTP/1.1 400 Bad Request
{"error": "state mismatch"}
```

**The reclassification**: `web-csrf` — the CSRF is the delivery; the OAuth
flow is the mechanism.

## Falsifier 2 — `redirect_uri` exact match

**The probe**:

```bash
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://evil.com/callback&response_type=code&state=XYZ"
```

**The falsifier**:

```
HTTP/1.1 400 Bad Request
{"error": "invalid redirect_uri"}
```

**The reclassification**: `web-open-redirect` — the redirect is the sink; the
OAuth flow is the mechanism.

## Falsifier 3 — `SameSite=Lax|Strict` on the SSO token

**The probe**:

```bash
grep -i "Set-Cookie.*token\|Set-Cookie.*sso\|Set-Cookie.*auth" transcript.txt
```

**The falsifier**:

```
Set-Cookie: token=ABC; HttpOnly; SameSite=Lax; Secure; Path=/
```

**The reclassification**: `web-auth-session` — the session is the mechanism;
the OAuth flow is the target.

## Falsifier 4 — `response_type` allowlisted to `code`

**The probe**:

```bash
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=token&state=XYZ&nonce=N"
```

**The falsifier**:

```
HTTP/1.1 400 Bad Request
{"error": "response_type not allowed"}
```

**The reclassification**: `web-auth-session` — the session is the mechanism;
the OAuth flow is the target.

## Falsifier 5 — PKCE required + `S256` + verifier re-validated

**The probe**:

```bash
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code&state=XYZ"
```

**The falsifier**:

```
HTTP/1.1 400 Bad Request
{"error": "code_challenge required"}
```

**The reclassification**: `web-auth-session` — the session is the mechanism;
the OAuth flow is the target.

## Falsifier 6 — code bound to `client_id` + `aud` verified

**The probe**:

```bash
curl -X POST $IDP/token -d "grant_type=authorization_code&code=ABC&client_id=B&client_secret=SECRET_B&redirect_uri=https://app/callback"
```

**The falsifier**:

```
HTTP/1.1 400 Bad Request
{"error": "invalid_client"}
```

**The reclassification**: `web-auth-session` — the session is the mechanism;
the OAuth flow is the target.

## Falsifier 7 — `scope` allowlisted

**The probe**:

```bash
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code&state=XYZ&scope=openid+admin"
```

**The falsifier**:

```
HTTP/1.1 400 Bad Request
{"error": "scope not allowed"}
```

**The reclassification**: `web-auth-session` — the session is the mechanism;
the OAuth flow is the target.

## Falsifier 8 — linking on `sub` + `email_verified` enforced

**The probe**:

```bash
# register the target account with the same email
curl -X POST $BASE/api/register -d '{"email":"student@domain","password":"own","username":"student"}'
# complete the OAuth flow — the session lands on the sub-mapped account
curl -b $JAR -L $BASE/login
```

**The falsifier**:

```
HTTP/1.1 302 Found
Location: /dashboard
Set-Cookie: session=sub_mapped_session; HttpOnly; Path=/
```

**The reclassification**: `web-race-condition` — the race is the mechanism;
the OAuth flow is the target.
