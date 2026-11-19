# CORS chains — the read feeding the next primitive

A CORS read rarely ends the chain — it leaks the capability or data
that unlocks the write, the auth, or the flag.

---

## 1. The token-read → CSRF-write chain — the canonical chain

```text
a CORS-open /api/csrf-token returns the token → your page reads it →
uses it in a CSRF-write → the write succeeds. the read breaks the
write's token defense.
```

```html
<script>
fetch('https://t/api/csrf',{credentials:'include'})
 .then(r=>r.json())
 .then(t=>fetch('https://t/api/change',{method:'POST',
    credentials:'include',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({csrf:t.token,email:'x@x'})}))
</script>
```

## 2. The read → flag chain — the direct leak

```text
/api/me or /api/flag returns the flag in the response — the CORS
read IS the flag path. no write needed.
```

## 3. The read → token → authenticated-API chain

```text
/api/token returns an API key → the page uses it in a subsequent
authenticated call → reads a privileged endpoint.
```

## 4. The read → XSS-less-session-hijack

```text
the read leaks the session cookie's value or a session token → you
replay it directly — a session-hijack, not just a data leak.
```

## 5. The CORS-read → IDOR chain

```text
/api/me returns your user id + an admin endpoint guess → read the
admin endpoint with the leaked id — a CORS-read feeding an IDOR.
```

## 6. The subdomain-XSS → CORS-read chain

```text
a subdomain XSS (or takeover) on sub.target.com → the page reads
target.com/api via the subdomain-trusted CORS → the read works
because your origin is a trusted sub.
```

## 7. The CORS-read → stored-write → flag chain

```html
<script>
fetch('https://t/api/me',{credentials:'include'})
 .then(r=>r.json())
 .then(d=>fetch('https://t/api/comment',{method:'POST',
    credentials:'include',
    body:JSON.stringify({text:d.flag}),
    headers:{'Content-Type':'application/json'}}))
</script>
```

Read the flag → write it to a public comment → read it same-origin.

## 8. The read → cache-poison chain

```text
a reflected ACAO without Vary: Origin → a poisoned cache serves the
attacker-origin response to every visitor — a CORS-read that
becomes a stored-leak.
```

## 9. The read → SSRF-pivot

```text
the CORS read leaks an internal URL/token → a subsequent SSRF
server-side fetches it — the read guides the pivot.
```

## 10. The read → logic-flaw chain

```text
the read leaks a workflow's state — a balance, an order id — → a
subsequent request exploits the leaked state — a logic chain.
```

## 11. The chain-vs-alone decision — when the read suffices

```text
the flag is IN the read → the CORS read is the whole exploit.
the read leaks a capability → a write/auth/flag step follows.
the read is public → not a chain — a different vector.
```

## 12. The chain-ledger — naming the full chain

```bash
python3 tools/state.py <c> --hypothesis \
  "cors-read /api/token -> csrf-write /api/change -> flag"
# the chain is the hypothesis — each step a measured gate
```
