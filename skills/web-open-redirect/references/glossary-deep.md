# Glossary (deep) — the complete open-redirect vocabulary

## The carrier terms

| Term | Definition |
|---|---|
| **Location header** | the `Location:` response header on a 3xx — the server-side redirect carrier; the verbatim bytes are the class evidence |
| **Refresh header** | `Refresh: 0;url=X` — a non-Location response header that redirects |
| **meta refresh** | `<meta http-equiv="refresh" content="0;url=X">` — a client-side redirect tag |
| **JS navigation** | `location.href=X`/`location.replace(X)`/`location.assign(X)`/`location=X`/`window.location` — a client-side redirect |
| **location.hash** | `location.hash=X` — a fragment-nav (same-page unless the JS re-reads it into `location.href`) |
| **history.pushState** | `history.pushState(..., X)` — a same-origin path-change (not cross-origin) |
| **DOM-source sink** | a `location.*`/`location.href` assignment fed by a request param — the client-side redirect sink |

## The filter terms

| Term | Definition |
|---|---|
| **prefix filter** | `startswith('/')`/`startswith('https://')` — the `//`/`\`/`scheme` arms defeat it |
| **substring filter** | `'target.com' in url` — the substring-in-path/query/fragment arms |
| **suffix filter** | `endswith('target.com')` — the `eviltarget.com` no-boundary arm |
| **allowlist filter** | `host in [a,b,c]` — the userinfo/`\@`/encoded-host/subdomain arms |
| **parse filter** | `urlparse`/`URI.parse`/`url.parse` host-read — the parser-differential arms |
| **scheme filter** | `scheme in [http,https]` — the `javascript:`/`data:`/`//`/`https:` arms |
| **decode filter** | a check on the encoded/decoded form — the decode-order arms |
| **regex filter** | a `re.match`/`preg_match` — the regex-boundary arms |

## The bypass-arm terms

| Term | Definition |
|---|---|
| **scheme-relative** | `//evil.com` — inherits the page's scheme; cross-origin |
| **protocol-relative** | the `//evil.com` form — the same |
| **backslash** | `/\evil.com`, `\\evil.com` — the browser's `\`→`/` normalization |
| **userinfo** | `https://user@host` — the `@` splits userinfo from host; `target.com@evil.com` host=`evil.com` |
| **\@** | `evil.com\@target.com` — the backslash-@ parser differential |
| **substring bypass** | `evil.com/target.com` — the substring in the path/query/fragment |
| **subdomain bypass** | `target.com.evil.com` — a subdomain of the allowed host |
| **no-boundary** | `eviltarget.com` — the suffix-match without a dot-boundary |
| **double-encode** | `%252f` -> `%2f` -> `/` — the two-stage decode |
| **fullwidth** | `%ef%bc%8f`=`／`, `%ef%bc%a0`=`＠` — multi-byte chars the ASCII check misses |
| **punycode/IDN** | `xn--...` — an internationalized host |
| **scheme-no-//** | `https:evil.com` — an absolute-scheme URL without `//` |
| **numeric-IP** | `2130706433`/`0x7f000001`/`0177.0.0.1` — the IP-literal forms |

## The evidence terms

| Term | Definition |
|---|---|
| **the canary** | the attacker-controlled destination — `https://attacker.invalid` |
| **the verbatim Location** | the raw `Location:` header bytes — the class evidence |
| **the fingerprint** | the ONE `Location:` on the first canary — names the filter shape |
| **the uniform falsifier** | `Location: <safe>` on EVERY canary + bypass arm — the class-close |
| **the carrier** | the redirect mechanism — Location/meta/JS/Refresh/Referer/stored |
| **the launder** | the downstream trust the redirect feeds — the chain value |

## The chain terms

| Term | Definition |
|---|---|
| **redirect_uri** | the OAuth callback param — the OAuth-launder surface |
| **post_logout_redirect_uri** | the OIDC logout redirect |
| **RelayState** | the SAML post-auth destination |
| **fetcher-follow** | an SSRF fetcher that follows `Location` — the SSRF-chain |
| **the scheme-sink** | the client-side sink accepting `javascript:`/`data:` |
| **the bot-visit** | a bot that visits the URL and runs the JS |

## The verdict terms

| Term | Definition |
|---|---|
| **candidate** | a `Location:`/meta/JS carrying the canary — the class-confirm |
| **impact** | the chain's downstream effect — the code/token/fetch/visit on the canary |
| **strong-negative** | a verbatim safe `Location:` on a real redirect param |
| **weak-negative** | a null/no-`Location` on a guessed param — the name was wrong |
| **the class falsifier** | the allowlist/relative-force holds on every arm |

## The scope terms

| Term | Definition |
|---|---|
| **catalogue class** | the class has no local solve — the corpus is published knowledge |
| **the field-note** | a solve's measured lesson — `../field-notes.md` accumulates them |
| **the chain card** | `knowledge/chains/` — a verified solve's card |
