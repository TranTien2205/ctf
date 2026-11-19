# Negative map — the negative-signal navigation

## The "I saw a safe Location" map

| The safe `Location:` | The file | The read |
|---|---|---|
| `Location: /` on the canary | `falsifiers.md` | a forced-relative arm-block — try the `//`/`\`/`%5c` family |
| `Location: https://target.com/` | `falsifiers.md` | a host-allowlist — try the `@`/substring/subdomain family |
| `Location: /dashboard` on the canary | `falsifiers.md` | a fixed-safe — a strong-negative for that arm |
| `Location: <partial>` | `decision-table.md` | a path/host-force fingerprint |
| `Location: evil.com` (relative) | `edge-cases.md` | resolves same-origin — NOT the gap |
| `Location: <the-param> escaped` | `client-side.md` | a sanitized client-side twin |
| no `Location:` at all | `troubleshoot.md` | a weak-negative — the param name is wrong |
| a `400`/`422` | `troubleshoot.md` | the format is rejected — a different param |

## The "which arm next" map

| The last arm failed | The next arm family | The file |
|---|---|---|
| `https://evil.com` blocked | `//`, `/\`, `\\`, `%5c`, `https:` | `per-vector.md` |
| `//evil.com` blocked | `/\evil.com`, `\\evil.com`, `/%5c`, `https:evil.com` | `filter-bypass-deep.md` |
| `/\evil.com` blocked | `/%5cevil.com`, `/%255cevil.com`, `\\evil.com` | `encoding-attacks.md` |
| `@`-arm blocked | `\@`, `%40`, `?@`, `#@` | `per-vector.md` |
| subdomain blocked | the no-boundary `eviltarget.com`, the hyphen `target-com.evil.com` | `per-target.md` |
| substring blocked | the `@`/`subdomain`/`encoded` | `per-check.md` |
| encoded blocked | the double-encode, the unicode | `encoding-attacks.md` |
| scheme blocked | the `//`/`\\`/`https:`/`file:`/`intent:` | `per-vector.md` |
| ALL blocked | the class falsifier | `falsifiers-deep.md` |

## The "the chain is dead" map

| The dead chain | The reopen | The file |
|---|---|---|
| the OAuth launder | a different allowlisted domain's open-redirect | `chain-routes.md` |
| the SSRF-follow | a different fetcher / a direct-URL | `chain-routes.md` |
| the XSS-sink | a different sink / a `data:`/`blob:` scheme | `client-side.md` |
| the bot-visit | a different bot-feature / a meta-carrier | `chain-routes.md` |
| the CRLF | a different header-carrier | `edge-cases.md` |
| the stored-redirect | a different set-then-fire pair | `stored-and-referer.md` |
| the Referer-derived | a different surface | `stored-and-referer.md` |

## The "the param doesn't redirect" map

| The observation | The reopen |
|---|---|
| `200 render` | a different param name — the vocabulary sweep |
| `400`/`422` | a different param / the relative-form carrier-check |
| a `Location: <fixed>` | a different param — this one isn't read |
| a meta/JS but escaped | a different sink — the DOM-source |
| a `Location:` on a non-3xx | a different carrier — the status-check |

## The negative-to-class map

| The observed non-open-redirect | The real class |
|---|---|
| the URL is fetched not redirected | `web-ssrf` |
| the `javascript:` reaches a sink | `web-xss` |
| the `redirect_uri` is the OAuth surface | `web-oauth-sso` |
| a `%0d%0a` splits the header | `web-request-smuggling`/header-injection |
| a reflected `?next=` link | `web-xss`/phishing |
| the `\@`/`%5c` parse-gap on any input | `web-parser-differential` |
