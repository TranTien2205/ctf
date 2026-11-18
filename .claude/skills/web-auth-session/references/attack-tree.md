# Attack tree — the auth-session decision map

The ordered decision tree for an auth-session target. Walk it top-down;
each node is a falsifiable probe, each edge is "if yes go here."

---

## 0. Entry — what do you have?

```
[handout with source] ──► whitebox-hunt.md greps ──► the verify call decides everything
[black-box URL]       ──► detection.md first-contact ──► identify the token format
```

## 1. Token format?

```
a.b.c three-part b64 ──► JWT ──► §2
single b64 blob ───────► session-analysis.md decode ──► §3
opaque short id ───────► session id ──► §4
cookie pair ───────────► remember-me/signed-blob ──► §3
OAuth dance ───────────► oauth-flow-issues.md ──► §6
no token, login form ──► registration-abuse + password-reset ──► §5
```

## 2. JWT branch

```
alg=none? ──► forge ──► REPLAY ──► flag?
  no ──►
kid/jku/x5u in header? ──► header injection ──► REPLAY
  no ──►
alg in {RS,ES,Ed}*? ──► pubkey reachable? ──► RS→HS confusion ──► REPLAY
  no ──►
secret guessable? ──► session_dissect --try-keys ──► re-sign ──► REPLAY
  no ──►
claims leak? (aud/iss/sub mismatched) ──► claim-side forge ──► REPLAY
  no ──►
replay a STOLEN token? (log/referer/xss) ──► hijack not forge ──► REPLAY
  all dead ──► park ──► decide.py escalate
```

`REPLAY` = send the forged token to a protected endpoint — see
`evidence-rules.md`: only a *protected endpoint accepting* counts.

## 3. Signed/encrypted blob branch

```
format? ──► session_dissect identifies ──►
  flask/itsdangerous ──► SECRET_KEY reachable? ──► forge ──► REPLAY
  django signed ──► SECRET_KEY reachable? ──► forge ──► REPLAY
  rails _session ──► secret_key_base reachable? ──► forge ──► REPLAY
  laravel_session ──► APP_KEY reachable? ──► forge ──► REPLAY
  express connect.sid ──► secret reachable? ──► forge ──► REPLAY
  opaque ──► §4 (session id)
  unknown ──► decode deeper (session-analysis §4) ──► §4
```

`SECRET_KEY`/`APP_KEY`/`secret_key_base`/`secret` sources: `.env`,
`config.py`, `settings.py`, `app.js`, `config/secrets.yml`,
`credentials.yml.enc` (+`master.key`), `git log`, bundle (`bundle_miner`),
`/proc/self/environ` via file-read.

## 4. Session-id branch

```
id format? ──► session-analysis entropy table ──►
  sequential ──► id_sweep ──► replay ──► flag?
  md5(sha1(user+time)) ──► recompute ──► replay ──► flag?
  uuid v1 ──► time+MAC ──► predict ──► replay
  opaque-random ──► fixation path ──► §4a
  transparent (b64 json) ──► §3
```

### 4a. Fixation path

```
login page sets sid pre-auth? ──► plant sid ──► victim logs in ──► replay sid
?sid= URL param accepted? ──► craft link ──► same
subdomain cookie plant possible? ──► plant Domain=.tld ──► same
none ──► §5 (steal)
```

### 4b. Hijack path

```
HttpOnly missing + XSS exists? ──► steal document.cookie ──► replay
Secure missing + http link? ──► sniff ──► replay
?sid= in Referer to external? ──► read log ──► replay
localStorage token? ──► XSS ──► read ──► replay
none ──► §5
```

## 5. Credential/flow branch

```
registration open? ──► mass-assign role field ──► admin account
  no role field ──► duplicate-email / verify-bypass / race ──► §5a
password reset? ──► token unbound? predictable? Host-injection? ──► ATO
mfa? ──► step-skip / code-falsy / device-trust / backup-codes ──► bypass
login itself? ──► user-enum oracle ──► web-user-enum
```

### 5a. Registration sub-branch

```
role/is_admin field in body? ──► mass-assign
email array pollution? ──► SMTP-header / array-injection
canonical-email race? ──► race_probe --write-ack
verify-skippable? ──► direct to /home post-register
unverified-account usable? ──► squat
```

## 6. OAuth/SSO branch

```
state missing/not-checked? ──► login CSRF
redirect_uri wildcard/loose? ──► token theft
response_type=token? ──► implicit leak
id_token unsigned/aud-mismatch? ──► forge
code replay / code not bound to client? ──► confused-deputy
logout at IdP not at RP? ──► session persists
```

## 7. Post-auth boundary branch

```
vertical: admin endpoint reachable as user? ──► access-control check
horizontal: /users/1 as user2? ──► idor check (web-idor)
field: role/is_admin in update body? ──► mass-assign
impersonation: /su|/switch_user|?become= ? ──► impersonation.md
multi-step: pre-mfa session reaches post-mfa surface? ──► mfa-bypass
```

## 8. The flag-reach branch

```
admin session/token? ──► where's the flag?
  /admin/* → read
  /api/admin → read
  user's note/profile field → read
  internal endpoint → SSRF/file-read chain
  second-order (bot logs in as admin) → steal
```

## 9. Dead-end map

| Dead end | Re-route |
|---|---|
| alg=none rejected | → confusion / kid / jku / secret |
| confusion rejected | → kid / jku / secret / claims |
| kid traversal fails | → jku / secret / claims |
| secret uncrackable | → claims / steal / reset-flow |
| claims verified | → steal / reset-flow / registration-abuse |
| session unpredictable | → fixation / hijack / reset-flow |
| fixation fails | → hijack / reset-flow / registration-abuse |
| hijack fails | → reset-flow / registration-abuse / oauth |
| reset flow clean | → registration-abuse / mfa / oauth |
| registration clean | → mfa / oauth / post-auth boundary |
| mfa solid | → oauth / post-auth boundary |
| oauth solid | → post-auth boundary |
| post-auth boundary solid | → park + escalate to writeup_search |
```

## 10. The "stop and escalate" condition

After the tree is exhausted — every branch measured dead with a recorded
negative — `tools/decide.py` names the escalation rung. The tree is the
*search space*; the ledger is the *memory*; the controller is the
*stop*. Don't re-walk a branch the ledger already closed.
