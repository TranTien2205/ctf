# Origin check deep — every way the allowlist breaks

The origin-check is the read's gate. Every check shape, its bypass,
and the exact probe that names it.

---

## 1. The reflect — the trivial vuln

```text
the server echoes the request's Origin: `ACAO: <whatever you sent>`.
ANY origin passes — a reflected ACAO+ACAC is the canonical vuln.
```

```bash
curl -s -i -b "$CJ" "$BASE/api/x" -H 'Origin: https://evil.com' | \
  grep -i 'access-control-allow-origin'
#   ACAO: https://evil.com — reflected → ANY page reads
```

## 2. The `null` allow — the opaque-origin bypass

```text
'null' is in the allowlist — a sandboxed iframe, a data: URL, or a
file: page's Origin is 'null' → passes.
```

```bash
curl -s -i -b "$CJ" "$BASE/api/x" -H 'Origin: null' | \
  grep -i 'access-control-allow-origin'
#   ACAO: null → an opaque-origin page reads
```

## 3. The prefix check — `startswith('https://target.com')`

```text
passes any origin STARTING with the allowed string —
'https://target.com.evil.com' passes.
```

```bash
curl -s -i -b "$CJ" "$BASE/api/x" -H 'Origin: https://target.com.evil.com' | \
  grep -i 'access-control-allow-origin'
```

## 4. The suffix check — `endswith('target.com')`

```text
passes any origin ENDING with the allowed string —
'https://eviltarget.com' passes.
```

```bash
curl -s -i -b "$CJ" "$BASE/api/x" -H 'Origin: https://eviltarget.com' | \
  grep -i 'access-control-allow-origin'
```

## 5. The substring check — `'target.com' in origin`

```text
passes any origin CONTAINING the string — 'https://evil-target.com',
'https://target.com.evil.com', 'https://evil.com/target.com' all pass.
```

```bash
for o in 'https://evil-target.com' 'https://target.com.evil.com' \
         'https://evil.com/target.com'; do
  curl -s -i -b "$CJ" "$BASE/api/x" -H "Origin: $o" | \
    grep -i 'access-control-allow-origin'; done
```

## 6. The regex check — an unanchored/loose pattern

```text
a regex `target\.com` (no anchors) passes 'https://target.com.evil.com';
an unescaped dot `target.com` matches 'targetXcom'; a pattern like
`.*target.com.*` is a substring check.
```

```bash
# the regex greps
grep -rnoE "re\.(match|search|fullmatch)\(['\"].*origin|match.*origin|test.*origin" <src>
# the bypass battery — each pattern a different probe
```

## 7. The subdomain trust — `*.target.com`

```text
an allowlist entry '*.target.com' trusts EVERY subdomain — a
subdomain XSS, a takeover, or a CTF-supplied sub passes.
```

```bash
curl -s -i -b "$CJ" "$BASE/api/x" -H 'Origin: https://sub.target.com' | \
  grep -i 'access-control-allow-origin'
```

## 8. The URL-parse confusion — `@`, `?`, `#`

```text
'https://target.com@evil.com' — the HOST is evil.com (the 'target.com'
is userinfo) — a naive 'target.com in origin' check passes it.
'https://evil.com?target.com' — the host is evil.com; the query
carries 'target.com'.
'https://evil.com#target.com' — the fragment carries it.
```

```bash
for o in 'https://target.com@evil.com' 'https://evil.com?target.com' \
         'https://evil.com#target.com'; do
  curl -s -i -b "$CJ" "$BASE/api/x" -H "Origin: $o" | \
    grep -i 'access-control-allow-origin'; done
```

## 9. The special-char bypass — ` `, ` `, `_`, `-`

```text
a regex `target\.com` that doesn't anchor the dot — 'target`com',
'target_com', 'target-com' may match or be parsed as the domain.
```

```bash
for o in 'https://target`com' 'https://target_com' 'https://target-com'; do
  curl -s -i -b "$CJ" "$BASE/api/x" -H "Origin: $o" | \
    grep -i 'access-control-allow-origin'; done
```

## 10. The scheme/port confusion

```text
'http://target.com' vs 'https://target.com' — a scheme-agnostic check.
'https://target.com:443' vs 'https://target.com' — a port-explicit.
'https://target.com.' — a trailing dot.
```

```bash
for o in 'http://target.com' 'https://target.com:443' 'https://target.com.'; do
  curl -s -i -b "$CJ" "$BASE/api/x" -H "Origin: $o" | \
    grep -i 'access-control-allow-origin'; done
```

## 11. The allowlist-bypass matrix — the battery's full table

```text
check-shape        probe                                passes-if
reflect            https://evil.com                     always
null-allow         null                                 'null' listed
prefix             https://target.com.evil.com          startswith
suffix             https://eviltarget.com               endswith
substring          https://evil-target.com              'target.com' in origin
regex-loose        https://target.com.evil.com          unanchored regex
subdomain          https://sub.target.com               *.target.com trusted
userinfo           https://target.com@evil.com          naive 'in' check
query              https://evil.com?target.com          naive 'in' check
encoded-dot        https://target.com%2eevil.com        decode-order bug
backtick           https://target`com                   loose regex
underscore         https://target_com                   loose regex
trailing-dot       https://target.com.                  no normalization
scheme             http://target.com                    scheme-agnostic
```

## 12. The strict-allowlist case — the closed check

```text
an exact-match allowlist — only the listed origins pass — no bypass.
the read is closed; pivot to a different class or an alternate-read
channel.
```

## 13. The white-box check read — the exact logic

```bash
# the check's code — reflect? allowlist? regex? in? startswith?
grep -rnoiE 'origin.*(in|==|===|match|test|startswith|endswith|includes|indexOf|regex|allow)' <src> | head -20
# the allowlist itself
grep -rnoE 'allowed_origins|allow_origins|origins.*=|whitelist.*origin|allowedOrigins' <src> | head -20
```

## 14. The decision — which check-shape, which bypass

```text
a reflect          → any origin — the trivial vuln
a null-allow       → a data:/sandboxed page — the opaque vuln
a prefix/suffix    → a lookalike origin — the bypass
a substring        → a containing origin — the bypass
a regex            → a pattern bypass — test the regex
a subdomain-trust  → a controlled subdomain — the bypass
a URL-parse bug    → an @/?/# confusion — the bypass
a strict allowlist → closed — pivot
```
