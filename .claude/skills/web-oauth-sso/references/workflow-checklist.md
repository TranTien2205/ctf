# Workflow checklist — the OAuth audit in order, with the commands

The checklist is the walk — the commands in order, the expected outputs, the
decision points.

## Step 0 — the transcript

```bash
JAR=/tmp/oauth-jar.txt
curl -i -b "$JAR" -c "$JAR" -L "$BASE/login" 2>&1 | tee transcript.txt
```

Expected: a `302` chain — `GET /login` → `GET /authorize` → `GET /callback` →
`GET /dashboard`. The transcript carries every artifact verbatim.

## Step 1 — the cookie inventory

```bash
grep -i "Set-Cookie" transcript.txt
```

Expected: two cookies — the app's `session` and the IdP's `token`/`sso`/`auth`.
Record the `SameSite`, `HttpOnly`, `Secure`, `Domain`, `Path` attributes.

## Step 2 — the parameter inventory

```bash
grep -oP 'authorize\?[^"]+' transcript.txt | tr '&' '\n'
```

Expected: `client_id`, `redirect_uri`, `response_type`, `scope`, `state`,
`nonce`, `code_challenge`, `code_challenge_method`, `prompt`, `max_age`,
`login_hint`, `id_token_hint`, `request`, `request_uri`, `response_mode`,
`claims`, `resource`, `acr_values`.

## Step 3 — the falsifier sweep

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

## Step 4 — the confirmation

```bash
python3 tools/hooks.py post-probe "$CHALLENGE" --class web-oauth-sso \
  --hypothesis-id "$HID" --verdict confirms \
  --evidence-kind class \
  --evidence "$(grep -E 'HTTP/|Set-Cookie:|Location:' evidence.txt | head -3)" \
  --response "$(cat evidence.txt)"
```

## Step 5 — the escalation

```bash
# the confirmed shape → the escalation command
# see exploitation-playbook.md for the chain
```

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

## Step 8 — the reclassification

When every falsifier holds — `state` bound to session, `redirect_uri` exact
match, `SameSite=Lax|Strict`, `response_type` code-only, PKCE required, code
bound to `client_id`, `aud` verified, `scope` allowlisted, linking on `sub` +
`email_verified` — the OAuth surface is closed. Reclassify: `web-auth-session`
for a session-mechanism attack, `web-logic-flaw` for a business-logic attack,
or a different class for a different mechanism.

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
