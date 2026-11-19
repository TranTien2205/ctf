# Workflow deep — the OAuth audit sequence, with the full mechanics

The workflow module names the steps. This module carries the full mechanics —
the sequence, the decision points, the escalation path, and the evidence
discipline at every step.

## The sequence

```
1. Walk the flow once — record every artifact verbatim
2. Inventory the cookies — SameSite is the swap signal
3. Inventory the parameters — every one is a testable surface
4. Run the falsifier sweep — cheapest first
5. Confirm the live shape — the verbatim response that proves it
6. Record the confirmation — the verbatim evidence
7. Escalate to the exploit — the chain that reaches the sink
8. Record the negative ledger — every falsifier that held
9. Reclassify when every falsifier holds
```

## Step 1 — the walk

```bash
JAR=/tmp/oauth-jar.txt
curl -i -b "$JAR" -c "$JAR" -L "$BASE/login" 2>&1 | tee transcript.txt
```

The walk records:

- The `302` chain — from the app to the IdP to the callback.
- The `authorize` URL — every parameter, verbatim.
- The `callback` URL — `code`, `state`, `error`, `error_description`.
- Every `Set-Cookie` — the app session and the IdP token.
- The `token` exchange — `grant_type`, `client_id`, `code_verifier` if present.
- The `id_token` — decode it; read `sub`, `email`, `nonce`, `aud`, `iss`, `exp`.
- The session issued — the final `Set-Cookie` on the app.

## Step 2 — the cookie inventory

```bash
grep -i "Set-Cookie" transcript.txt
```

For each cookie:

| Attribute | The check | The gap |
|---|---|---|
| `SameSite` | `Lax`/`Strict`/`None`/missing | missing or `None` → cross-site writes land |
| `HttpOnly` | present/missing | missing → readable by JS |
| `Secure` | present/missing | missing → over plain HTTP |
| `Domain` | app domain/parent domain | parent → shared across subdomains |
| `Path` | `/` or restricted | `/` → readable everywhere |

Two cookies — one from the app (`session`), one from the IdP (`token`/`sso`/`auth`)
— in the same jar is the swap signal.

## Step 3 — the parameter inventory

```bash
grep -oP 'authorize\?[^"]+' transcript.txt | tr '&' '\n'
```

Every parameter is a testable surface:

| Parameter | The surface | The check |
|---|---|---|
| `state` | CSRF binding | bound to session? single-use? predictable? |
| `redirect_uri` | code delivery target | exact match? prefix? wildcard? |
| `response_type` | flow shape | `code` only? `token`? `id_token`? hybrid? |
| `scope` | permissions | broader than requested? `offline_access`? |
| `nonce` | replay binding | present? validated? |
| `code_challenge` | PKCE binding | required? `S256` or `plain`? |
| `client_id` | client identity | enumerate — sequential? predictable? |
| `prompt` | consent behavior | `none` → silent re-auth? |
| `response_mode` | delivery mode | `query`? `fragment`? `form_post`? `web_message`? |

## Step 4 — the falsifier sweep

Run the cheapest falsifiers first — a `curl` that takes seconds beats an
exploit chain that takes minutes:

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

## Step 5 — the confirmation

When a falsifier does not hold, the shape is live. Confirm it with the
verbatim response that carries the artifact:

```bash
python3 tools/hooks.py post-probe "$CHALLENGE" --class web-oauth-sso \
  --hypothesis-id "$HID" --verdict confirms \
  --evidence-kind class \
  --evidence "$(grep -E 'HTTP/|Set-Cookie:|Location:' evidence.txt | head -3)" \
  --response "$(cat evidence.txt)"
```

## Step 6 — the escalation

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

## Step 7 — the negative ledger

```bash
python3 tools/hooks.py post-probe "$CHALLENGE" --class web-oauth-sso \
  --hypothesis-id "$HID" --verdict negative \
  --request "<probe>" --result "<verbatim result>"
```

## Step 8 — the kill map

```bash
python3 tools/hooks.py post-probe "$CHALLENGE" --class web-oauth-sso \
  --hypothesis-id "$HID" --verdict falsifier \
  --request "<probe>" --result "<verbatim falsifier>"
```

## Step 9 — the reclassification

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
