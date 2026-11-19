# Quick reference — the OAuth audit in one page

## The walk

```bash
JAR=/tmp/oauth-jar.txt
curl -i -b "$JAR" -c "$JAR" -L "$BASE/login" 2>&1 | tee transcript.txt
```

## The cookie inventory

```bash
grep -i "Set-Cookie" transcript.txt
```

| Attribute | The gap |
|---|---|
| `SameSite` | missing or `None` → cross-site writes land |
| `HttpOnly` | missing → readable by JS |
| `Secure` | missing → over plain HTTP |
| `Domain` | parent → shared across subdomains |
| `Path` | `/` → readable everywhere |

## The parameter inventory

```bash
grep -oP 'authorize\?[^"]+' transcript.txt | tr '&' '\n'
```

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

## The mechanism map

| Mechanism | The artifact | The falsifier |
|---|---|---|
| state CSRF | `state` in authorize + callback | `state` bound to session |
| redirect interception | `redirect_uri` in authorize | `redirect_uri` exact match |
| cookie swap | `SameSite` on IdP token | `SameSite=Lax|Strict` |
| account linking | `email`/`username`/`sub` in `id_token` | linking on `sub` |
| implicit leak | `response_type` + `access_token` in fragment | `response_type` code-only |
| PKCE bypass | `code_challenge` + `code_verifier` | `S256` + verifier re-validated |
| cross-client | `client_id` + `aud` in `id_token` | `client_id` bound + `aud` verified |
| scope escalation | `scope` in authorize + token | `scope` allowlisted |
| registration race | `email`/`username` in registration | registration idempotent |

## The evidence rules

- A `302` + `Set-Cookie: session=...` is the session confirmation.
- A `302` + `Location: ...?code=...` is the code delivery.
- A `200` + `{"access_token": ...}` is the token confirmation.
- A `200` + `Set-Cookie: token=...` is the cookie confirmation.
- A `400` naming the mismatch is the falsifier.
- A `302` to a login page is a negative, not a falsifier.

## The decision tree

```
Is there a second cookie (IdP token) in the jar?
  YES → check SameSite → missing/None → cookie-swap shape live
  NO  → single-cookie model → move to state/redirect_uri

Is state bound to session?
  NO  → state CSRF live
  YES → falsifier → move to redirect_uri

Is redirect_uri strictly validated?
  NO  → code-interception live
  YES → falsifier → move to account linking

Is linking on email/username?
  YES → pre-registration race live
  NO  → falsifier → move to implicit/PKCE/cross-client

Is response_type allowlisted to code?
  NO  → implicit-leak live
  YES → falsifier → move to PKCE

Is PKCE required + S256 + verifier re-validated?
  NO  → PKCE-bypass live
  YES → falsifier → move to cross-client

Is code bound to client_id + aud verified?
  NO  → cross-client live
  YES → falsifier → reclassify
```
