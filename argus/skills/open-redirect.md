# Open redirect

**When:** a parameter names the next destination: `next`, `redirect`, `url`,
`return`, `returnTo`, `continue`, `dest`, `goto`, `target`, `r`, `u`, `redir`.
Common on login (post-auth bounce), logout, OAuth `redirect_uri`, error pages.

`probe_redirect` sets the param to an external URL and reads `Location`.

## Payload ladder for filtered targets

1. `https://example.org/` (baseline external)
2. `//example.org/` (scheme-relative - passes many `^/` allowlists)
3. `/\\example.org`, `\/\/example.org`, `//evil%5c@example.org`
4. `https://victim.com@example.org/` (userinfo - parser shows left host)
5. `https://example.org@victim.com` reversed - reads as victim but lands evil
6. Encoded: `%2f%2fexample.org`, `https%3a%2f%2fexample.org`
7. `javascript:alert(1)` - when the redirect happens via JS/DOM, this is XSS
8. Path-confused: `https://victim.com.evil.com`, `victim.com.evil.com`

## Where the redirect happens

- 30x `Location` header - probe_redirect catches it
- `<meta http-equiv="refresh" content="0;url=...">` in body
- JS: `location.href = param` - check inline JS from js_recon
- OAuth `redirect_uri`: scope matters - code/token theft when the check is
  prefix/suffix-based; test `redirect_uri=https://app.com@evil.com` and
  `.../callback/../evil` path tricks

## Impact upgrade

- Phishing vector alone: low-medium - be honest in the report
- OAuth token/code exfiltration chain: high
- `javascript:` execution: XSS severity (see xss)
- Chained into SSO/account-takeover flows: rate the chain

## Falsifier

External/encoded destinations all land on a fixed allowlist page or the
param is path-normalized so the host cannot change.

## Severity guide

Plain open redirect: low. Into OAuth/SSO flow: medium-high. As a link in a
demonstrated account-takeover chain: rate the chain's impact.
