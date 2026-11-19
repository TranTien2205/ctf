# ACAO deep — the origin-check, every shape

The `Access-Control-Allow-Origin` header is the read's gate. Every
value it can take, and what each means for the exploit.

---

## 1. `Access-Control-Allow-Origin: *` — the public read

```text
'any origin may read this' — but NEVER with credentials. the
browser rejects `*`+ACAC:true. a `*` endpoint is a public API.
the vuln is NOT a `*` — it's a named origin allowed WITH creds.
```

```bash
curl -s -i -b "$CJ" "$BASE/api/public" | grep -i 'access-control-allow-origin'
#   ACAO: * — public; the fetch works but reads no session data
```

## 2. Reflected — the canonical vuln

```text
the server echoes the request's Origin. 'you asked from X → I allow X'.
any attacker page reads the credentialed response.
```

```bash
curl -s -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com' | \
  grep -i 'access-control-allow-origin'
#   ACAO: https://evil.com — reflected → THE VULN (if ACAC:true)
```

## 3. `Access-Control-Allow-Origin: null` — the opaque-origin vuln

```text
'null' is the origin a sandboxed iframe, a data: URL, or a file:
page sends. a `null`-allowed CORS lets an opaque-origin page read
the credentialed data — harder to spot than a reflect.
```

```bash
curl -s -i -b "$CJ" "$BASE/api/x" -H 'Origin: null' | \
  grep -i 'access-control-allow-origin'
#   ACAO: null — the opaque origin is allowed
```

## 4. Fixed allowlist — the closed case

```text
ACAO names a specific allowed origin — only that origin reads. your
foreign origin is rejected. the vuln needs a bypass or a different
vector.
```

```bash
curl -s -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com' | \
  grep -i 'access-control-allow-origin'
#   ACAO: https://app.target.com — fixed; yours isn't allowed
```

## 5. Subdomain-trust — `*.target.com`

```text
the allowlist is a suffix/regex matching `*.target.com` — ANY
subdomain passes: a subdomain XSS, a takeover, a CTF-supplied sub.
```

```bash
curl -s -i -b "$CJ" "$BASE/api/x" -H 'Origin: https://sub.target.com' | \
  grep -i 'access-control-allow-origin'
#   ACAO: https://sub.target.com — the suffix is trusted
```

## 6. Prefix/suffix checks — the bypassable allowlist

```text
the check is `startswith('https://target.com')` — passes
`target.com.evil.com`. or `endswith('target.com')` — passes
`eviltarget.com`. a substring check passes `evil-target.com`.
```

```bash
for o in 'https://target.com.evil.com' 'https://eviltarget.com' \
         'https://evil-target.com'; do
  curl -s -i -b "$CJ" "$BASE/api/x" -H "Origin: $o" | \
    grep -i 'access-control-allow-origin'; done
```

## 7. Regex-based checks — the loose pattern

```text
a regex `target\.com` (unanchored) passes `evil.com/target.com` or
`target.com.evil.com`. an unescaped dot `target.com` matches
`targetXcom`. grep the source for the regex.
```

```bash
grep -rn 're\.match\|re\.search\|match\|test\|origin' <src> | \
  grep -iE 'target|origin|allow' | head -10
```

## 8. `Vary: Origin` — the dynamic ACAO

```text
a `Vary: Origin` response signals the ACAO is computed per-origin —
the reflect/bypass check applies. a missing Vary on a dynamic ACAO
is a cache-poisoning surface.
```

## 9. The absent ACAO — not the class

```text
no ACAO = no CORS read — the browser blocks the response read. the
request may still fire (CSRF-style) but the data is unreadable.
not the web-cors class.
```

## 10. The decision table — ACAO → exploitability

```text
reflected + ACAC    → the vuln — any origin reads credentialed
null + ACAC         → opaque-origin vuln
* (alone)           → public read — not the vuln
* + ACAC            → INVALID — browser rejects
fixed (in list)     → read — vuln if you can host there
fixed (not in list) → closed — bypass or pivot
subdomain + ACAC    → subdomain-read — vuln if a sub is reachable
prefix/suffix + ACAC → lookalike bypass — vuln
regex + ACAC        → pattern bypass — test the regex
absent              → not CORS
```

## 11. The ACAO-credential interplay — the matrix

```text
ACAO       ACAC      browser behavior
*          absent    public read — no creds
*          true      REJECTED — invalid combo
reflected  absent    non-credentialed read — the cookie doesn't ride
reflected  true      CREDENTIALED read — THE VULN
null       true      credentialed opaque-origin read
fixed      true      credentialed read — only that origin
```

## 12. The white-box ACAO read

```bash
# the ACAO-set code — reflect? allowlist? regex?
grep -rnoE 'Access-Control-Allow-Origin|allow_origin|setHeader.*Origin|Access-Control' <src> | head -20
# the exact check — reflect vs allowlist vs regex
grep -rnoE 'origin.*(in|==|match|test|startswith|endswith|regex)' <src>
```
