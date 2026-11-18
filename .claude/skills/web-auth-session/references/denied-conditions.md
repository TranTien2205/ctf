# Denied conditions — the falsifiers that close the class

A falsifier is a response that *proves* this mechanism cannot reach the
flag — record it, don't retry it. Each entry: the observation → what it
closes → where to go next.

---

## 1. JWT falsifiers

| Observed | Closes | Next |
|---|---|---|
| `algorithms:["HS256"]` pinned in code AND secret ≥128-bit random AND `kid`/`jku` absent | all JWT-forgery routes | pivot: mass-assign, idor, logic |
| `verify_signature` enforced + alg allowlist + `aud`/`iss`/`exp`/`nbf` all validated | alg confusion + replay | check `jti` uniqueness only |
| token signed `EdDSA`/`ES256` with HSM/KMS key, no `jku`/`x5u` | weak-secret + confusion | pivot |
| `algorithms` list is `["EdDSA"]` or `["RS256"]` only — HMAC not accepted | alg confusion | try kid/jku if header honored |
| `kid`/`jku`/`x5u` fields rejected or allowlisted to HTTPS + fixed host | header injection | pivot |
| `jti` checked against a server-side revocation set | replay of old tokens | steal live session instead |

## 2. Session falsifiers

| Observed | Closes | Next |
|---|---|---|
| session id rotates on login AND old id invalidated | fixation | hijack/idor |
| session bound to user.id server-side, token is just a lookup key | token-content tampering | steal the id instead |
| `Set-Cookie` has `Secure; HttpOnly; SameSite=Strict; __Host-` | cookie-flag attacks | OAuth or reset flow |
| logout + password-change both revoke all sessions | replay-after-change | token itself |
| session id is `secrets.token_urlsafe(32)` — 256-bit | prediction/brute | fixation or leak |
| sessions stored server-side with expiry + revocation | anything token-local | OAuth/reset/logic |

## 3. Reset-flow falsifiers

| Observed | Closes | Next |
|---|---|---|
| token `secrets.token_urlsafe(32)`+expiry+single-use+account-bound | prediction/replay/confusion | host-header only |
| `Host`/`X-Forwarded-Host` ignored — reset link hardcoded `BASE` | header injection | token itself |
| `email` strictly parsed (single RFC5322 addr) | param pollution | token itself |
| reset kills all sessions + rotates them | post-takeover persistence | n/a |
| token bound to `email` in the verify query | token-swapping | prediction only |

## 4. MFA falsifiers

| Observed | Closes | Next |
|---|---|---|
| TOTP seed never leaves server + rate limit + bound to session+user | prediction/skip/replay | oauth/logic |
| `code` required AND type-checked AND range-checked AND single-use | missing/falsy/dupe code | race only |
| backup codes random 128-bit + separate rate limit | backup-code brute | pivot |
| remember-device cookie is `HMAC(user_id + device_fp)` with strong key | cookie forgery | steal cookie only |

## 5. OAuth falsifiers

| Observed | Closes | Next |
|---|---|---|
| `redirect_uri` exact-match against registered list (no prefix, no suffix) | redirect takeover | open-redirect chain on target |
| `state` required + bound to session + single-use | login CSRF | token-side bugs |
| `id_token` signature + `aud` + `iss` + `nonce` + `exp` all verified | token forgery | provider confusion |
| `code` bound to `client_id`+`redirect_uri`+PKCE-verifier | code replay | client_secret leak |
| `prompt=none` still enforces consent for new scopes | silent scope escalation | n/a |

## 6. Carrier falsifiers

| Observed | Closes |
|---|---|
| token only in `Authorization` header, never cookie/localStorage/URL | CSRF-leak, subdomain-leak, Referer-leak |
| cookie `Partitioned` + `__Host-` + `SameSite=Strict` + `Secure` + `HttpOnly` + short `Max-Age` | every cookie-attribute attack |

## 7. Recording a falsifier

```bash
python3 tools/hooks.py post-probe <name> \
  --hypothesis-id H<x> --class web-auth-session \
  --verdict refutes --evidence-kind class \
  --evidence 'verify_signature enforced; alg allowlist is exactly ["EdDSA"]' \
  --response '<verbatim response or code excerpt>'
```

The `refutes` verdict is the deliverable — `decide.py` uses it to switch
mechanism. An unrecorded falsifier is work you'll redo.
