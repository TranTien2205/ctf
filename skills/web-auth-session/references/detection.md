# Detection — map the auth surface before touching it

The first job is inventory: which mechanism carries identity (cookie, bearer,
JWT, opaque token, signed value), where it is minted, where it is verified,
and who else can read it. Everything after that is a per-mechanism checklist.

---

## 1. Inventory in one pass

```bash
# what the server sends you
curl -si -X POST "$BASE/login" -d 'user=a&pass=b' | grep -iE 'set-cookie|authorization|www-authenticate|x-(auth|token|session)|location'

# what the client sends back — check the SPA
grep -rhoE '(localStorage|sessionStorage|document\.cookie)[^;]{0,80}' public/ static/ 2>/dev/null | sort -u

# endpoint names in the bundle — auth surface is usually named
grep -rhoE '"/[a-zA-Z0-9_/-]*(login|logout|register|signup|signin|auth|token|session|oauth|sso|callback|refresh|reset|forgot|verify|confirm|activate|invite|mfa|totp|2fa|otp|password|passwd|credential|magic)[a-zA-Z0-9_/?=&-]*"' . --include='*.js' 2>/dev/null | sort -u
```

Record:

| Field | Value |
|---|---|
| auth mechanism | form / JWT-bearer / cookie-session / OAuth / magic-link / basic |
| token carrier | Cookie `name=` / `Authorization: Bearer` / header / URL param |
| token format | JWT (3 dots) / JWE (5) / itsdangerous (`:` split) / base64-JSON / opaque hex |
| cookie flags | `Secure; HttpOnly; SameSite=?; Domain=?; Path=?; Max-Age/Expires` |
| login | endpoint, method, body shape, lockout, captcha, error strings |
| register | endpoint, fields accepted, role/plan field, email verify |
| reset | endpoint, link shape, token entropy, expiry |
| session mgmt | `/logout`, `/sessions`, "remember me", device list |
| mfa | TOTP/SMS/email/backup codes, enrollment, verify endpoint |
| oauth | providers, `/authorize` params (state, redirect_uri, scope, nonce) |

## 2. Classify the token format

`python3 tools/web/session_dissect.py --token "$TOKEN"` names it. The
shorthand:

| Shape | Format |
|---|---|
| `aaa.bbb.ccc` (3 b64url parts) | **JWT/JWS** — decode header+payload without key |
| 5 b64url parts | **JWE** — encrypted; attack surface is `alg`/`enc` confusions |
| `data:timestamp:sig` or `data.sig` | **itsdangerous** (Flask/Django-style signed) |
| `eyJ...` single blob that b64-decodes to JSON | base64-JSON (unsigned!) or Fernet (`gAAA`) |
| 32–64 hex | opaque session id — the lookup happens server-side |
| `session=abc.def` cookie signed `sha1`/`sha256` | express-signed / rack / play |

The carrier matters as much as the format: a JWT in `localStorage` is
XSS-readable; the same JWT in an `HttpOnly` cookie is not.

## 3. The two-account differential — cheap and decisive

Register **two accounts** (A and B). The trick that catches the whole class
family:

1. Log in as A, capture `tokenA`. Log in as B, capture `tokenB`.
2. Send A's request with `tokenB` → accepted? session binding bug.
3. Diff `tokenA` vs `tokenB`: same prefix? sequential id? timestamp visible?
4. Tamper one byte of `tokenB` signature → still accepted? no verification.
5. Logout A, replay `tokenA` → still accepted? no invalidation.

Each row is one request and one verdict — no fuzzing needed.

## 4. Signal → class routing

| Observed | Route |
|---|---|
| `alg: none` accepted / RS→HS works | jwt-attacks.md |
| signature not checked at all | jwt-attacks.md §verification-skipped |
| `kid`/`jku`/`x5u` honored | jwt-header-injection.md |
| secret in wordlist | weak-secrets.md → `session_dissect --try-keys` |
| sequential/timestamp session id | session-analysis.md → id_sweep |
| Set-Cookie on GET with no `state` | oauth-flow-issues.md |
| reset link predictable | password-reset.md |
| login error differs per user | `skills/web-user-enum/` |
| role field in register body | `skills/web-mass-assignment/` |
| cookie `Secure` missing on HTTPS | cookie-flags.md — report-level |
| session bound to nothing | session-hijacking.md |

## 5. What to grep in white-box

```bash
grep -rnE 'jwt\.(sign|verify|decode)|decode\(|verify\(|createSignedToken|jsonwebtoken|pyjwt|jjwt|jsonwebtoken' --include='*.py' --include='*.js' --include='*.ts' --include='*.java' --include='*.rb' --include='*.go' --include='*.php'
grep -rnE 'algorithms?\s*[:=]|verify_signature|verify_exp|verify_aud|audience|issuer' --include='*.py' --include='*.js' --include='*.ts'
grep -rnE 'secret|SECRET|signing_key|private_key|public_key|JWT_' --include='*.py' --include='*.js' --include='*.env*' --include='*.yml' --include='*.yaml' --include='*.json' --include='*.env'
grep -rnE 'cookie|session|set_cookie|set-cookie|Set-Cookie|secure|httponly|samesite' --include='*.py' --include='*.js' --include='*.ts' | grep -iv 'test\|spec'
grep -rnE 'kid|jku|x5u|jwk|jwks' --include='*.py' --include='*.js' --include='*.ts'
```

The decisive question: **what does the verify call look like?**

```python
jwt.decode(t, key, algorithms=["HS256"])          # fine
jwt.decode(t, key)                                # alg not pinned — confusion
jwt.decode(t, key, algorithms=["HS256","RS256"])  # RS→HS confusion possible
jwt.decode(t, options={"verify_signature":False}) # dead — forge anything
jwt.decode(t, verify=False)                       # dead — pyjwt<2 legacy
```

```javascript
jwt.verify(t, SECRET)                     // alg from header — confusion
jwt.verify(t, SECRET, {algorithms:['HS256']})  // pinned — fine
jwt.decode(t)                             // NO verification — dead
```

## 6. White-box flag locations

```bash
grep -rnE 'flag|FLAG|ctf\{' --include='*.py' --include='*.js' --include='*.ts' --include='*.env*' --include='*.yml' | grep -v 'test'
grep -rnE 'role|admin|is_admin|isAdmin|superuser|staff' --include='*.py' --include='*.js' --include='*.ts' | grep -iE 'claim|payload|token|jwt|session'
```

The flag usually sits behind `role=="admin"` in a claim, or behind an
endpoint that requires a claim you don't have — so the payload you forge
is `{"role":"admin"}`, `{"sub":"admin"}`, `{"uid":1}`, `{"user_id":0}`,
`{"isAdmin":true}`, `{"scope":"admin"}`, `{"groups":["admin"]}`.

## 7. First-probe contract

```bash
python3 tools/web/session_dissect.py --token "$TOKEN"
```

— it names the format, decodes what needs no key, and prints the next
command (`jwt_forge` variant or `http_probe` replay). Record the dissect
output in the ledger; it decides which sub-file to open.
