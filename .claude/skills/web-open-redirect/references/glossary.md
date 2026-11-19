# Glossary — the open-redirect vocabulary

## The carriers

| Term | Meaning |
|---|---|
| **Location header** | the `Location:` response header on a 3xx — the server-side redirect carrier |
| **meta refresh** | `<meta http-equiv="refresh" content="0;url=X">` — a client-side redirect tag |
| **JS navigation** | `location.href=X`/`location.replace(X)`/`location.assign(X)`/`location=X` — a client-side redirect |
| **location.hash** | `location.hash=X` — a fragment-nav (same-page) unless the JS re-reads it |
| **Refresh header** | `Refresh: 0;url=X` — a header-carried non-Location redirect |
| **history.pushState** | a same-origin path-change (not cross-origin) |

## The filter shapes

| Term | Meaning |
|---|---|
| **prefix filter** | `startswith('/')`/`startswith('https://')` — the `//`/`\`/`scheme` arms defeat it |
| **substring filter** | `'target.com' in url` — the substring-in-path/query arms defeat it |
| **suffix filter** | `endswith('target.com')` — the `eviltarget.com` no-boundary arm |
| **allowlist filter** | `host in [a,b,c]` — the userinfo/`\@`/encoded-host arms |
| **parse filter** | a `urlparse`/`URI.parse` host-read — the parser-differential arms |
| **scheme filter** | `scheme in [http,https]` — the `javascript:`/`data:`/`//` arms |
| **decode filter** | a check on the encoded/decoded form — the decode-order arms |

## The bypass shapes

| Term | Meaning |
|---|---|
| **scheme-relative** | `//evil.com` — inherits the page's scheme; cross-origin |
| **protocol-relative** | same as scheme-relative |
| **backslash** | `/\evil.com`, `\\evil.com` — the `\`→`/` browser normalization |
| **userinfo** | `https://user@host` — the `@` separates userinfo from host; `target.com@evil.com` reads host=`evil.com` |
| **\@** | `evil.com\@target.com` — the backslash-@ parser differential |
| **substring bypass** | `evil.com/target.com` — the substring in the path |
| **subdomain bypass** | `target.com.evil.com` — a subdomain of the allowed host |
| **double-encode** | `%252f` -> `%2f` -> `/` — the double-decode |
| **fullwidth** | `%ef%bc%8f` = `／` — a multi-byte char the ASCII check misses |
| **punycode/IDN** | `xn--...` — an internationalized host the ASCII check misses |

## The evidence terms

| Term | Meaning |
|---|---|
| **canary** | the attacker-controlled destination — `https://attacker.invalid/landing` |
| **verbatim Location** | the raw `Location:` header bytes — the evidence |
| **fingerprint** | the one `Location:` on the first canary — names the filter shape |
| **uniform falsifier** | `Location: <safe>` on every arm — the class-closing observation |
| **carrier** | the redirect mechanism — Location/meta/JS/Refresh |

## The chain terms

| Term | Meaning |
|---|---|
| **laundered trust** | the redirect's value — a downstream trust the canary inherits |
| **redirect_uri** | the OAuth callback param — the OAuth-launder surface |
| **post_logout_redirect_uri** | the OIDC logout redirect |
| **RelayState** | the SAML post-auth destination |
| **fetcher-follow** | an SSRF fetcher that follows `Location` — the SSRF-chain |
| **DOM-sink** | the client-side `location.*`/`location.href` the param reaches |

## The verdict terms

| Term | Meaning |
|---|---|
| **candidate** | a `Location:`/meta/JS carrying the canary — the class-confirm |
| **impact** | the chain's downstream effect — the code/token/fetch/visit on the canary |
| **strong-negative** | a verbatim safe `Location` on a real redirect param |
| **weak-negative** | a null/no-Location on a guessed param — the name was wrong |
| **the class falsifier** | the allowlist/relative-force holds on every arm |
