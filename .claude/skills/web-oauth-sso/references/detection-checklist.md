# Detection checklist — the OAuth artifacts that name the mechanism, in order

The checklist is the walk — the artifacts in order, the mechanism each one
names, the probe that confirms or falsifies.

## Step 1 — the `authorize` URL

```bash
grep -oP 'authorize\?[^"]+' transcript.txt | tr '&' '\n'
```

| Parameter | The mechanism | The probe |
|---|---|---|
| `client_id` | the client identity | enumerate — sequential? predictable? |
| `redirect_uri` | the code delivery target | authorize with a wrong URI |
| `response_type` | the flow shape | `token`/`id_token`/`code token` |
| `scope` | the permissions | broader than requested? `offline_access`? |
| `state` | the CSRF binding | bound to session? single-use? predictable? |
| `nonce` | the replay binding | present? validated? |
| `code_challenge` | the PKCE binding | required? `S256` or `plain`? |
| `code_challenge_method` | the PKCE method | `S256` enforced? `plain` accepted? |
| `prompt` | the consent behavior | `none` → silent re-auth? |
| `max_age` | the re-auth window | required? enforced? |
| `login_hint` | the prefilled username | reflected? injectable? |
| `id_token_hint` | a previous `id_token` | replayable? |
| `request`/`request_uri` | a JWT carrying the request | signature verified? URI SSRF-able? |
| `response_mode` | the delivery mode | `query`? `fragment`? `form_post`? `web_message`? |
| `claims` | the requested claims | broader? |
| `aud` | the token audience | present? validated? |
| `resource` | the resource indicator | a different resource? |
| `acr_values` | the auth level | lower acr accepted? |

## Step 2 — the `callback` URL

```bash
grep -oP 'callback\?[^"]+' transcript.txt | tr '&' '\n'
```

| Parameter | The mechanism | The probe |
|---|---|---|
| `code` | the authorization code | replay? single-use? bound to `client_id`? |
| `state` | the CSRF binding | bound to session? single-use? predictable? |
| `error`/`error_description` | the error path | what does the error name? |

## Step 3 — the `Set-Cookie` headers

```bash
grep -i "Set-Cookie" transcript.txt
```

| Cookie | The mechanism | The probe |
|---|---|---|
| app `session` | session issuance | `GET /dashboard` — is the session valid? |
| IdP `token`/`sso`/`auth` | token issuance | `GET /userinfo` — is the token valid? |
| IdP `refresh_token` | refresh artifact | `POST /token` — is the refresh token valid? |
| IdP `device_code` | device flow | `POST /token` — is the device code valid? |
| IdP `state` | CSRF binding | `GET /callback` — is the state bound? |
| IdP `nonce` | replay binding | `GET /callback` — is the nonce bound? |
| IdP `code_verifier` | PKCE verifier | `POST /token` — is the verifier re-validated? |

## Step 4 — the `id_token` decode

```bash
# decode the id_token — read the claims
echo "$ID_TOKEN" | cut -d'.' -f2 | base64 -d 2>/dev/null | jq .
```

| Claim | The mechanism | The probe |
|---|---|---|
| `sub` | the subject identifier | user-controlled? linking field? |
| `email` | the email claim | linking field? `email_verified` enforced? |
| `email_verified` | the verification flag | enforced? |
| `preferred_username` | the username claim | linking field? |
| `groups`/`roles` | the permission claims | broader? |
| `aud` | the token audience | verified? |
| `iss` | the token issuer | verified? |
| `exp` | the token expiry | validated? |
| `nonce` | the replay binding | validated? |
| `signature` | the JWT signature | verified? `alg=none`? |

## Step 5 — the falsifier sweep

```bash
# falsifier 1 — state binding
STATE=$(curl -si -b "$JAR" -c "$JAR" "$BASE/login" | grep -oP 'state=\K[^&\s]+')
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

## Step 6 — the confirmation

```bash
python3 tools/hooks.py post-probe "$CHALLENGE" --class web-oauth-sso \
  --hypothesis-id "$HID" --verdict confirms \
  --evidence-kind class \
  --evidence "$(grep -E 'HTTP/|Set-Cookie:|Location:' evidence.txt | head -3)" \
  --response "$(cat evidence.txt)"
```

## Step 7 — the escalation

| Confirmed shape | The escalation |
|---|---|
| state not bound | login-CSRF or linking-CSRF |
| redirect_uri loose | code-interception |
| account linking on email | pre-registration race |
| cookie swap | text/plain JSON login |
| implicit leak | fragment-harvest |
| PKCE bypass | stolen-code exchange |
| cross-client | code replay |
| scope escalation | broader token |
| registration race | pre-registration |
