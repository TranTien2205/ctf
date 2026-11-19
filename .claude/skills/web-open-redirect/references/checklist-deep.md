# Checklist (deep) — the complete open-redirect verification pass

## The presence checks — the param + the carrier

- [ ] a redirect-param name is in the swept vocabulary
- [ ] the param reaches a `Location:`/`Refresh:`/meta/JS carrier
- [ ] the param is attacker-controlled (GET/POST/cookie/Referer/session/fragment)
- [ ] the first canary sent — `?next=https%3A%2F%2Fattacker.invalid`
- [ ] the verbatim `Location:`/carrier-value read

## The oracle checks — the verbatim evidence

- [ ] `Location: https://attacker.invalid` — the absolute canary
- [ ] `Location: //evil.com` — the scheme-relative canary
- [ ] `Location: https://target.com.evil.com` — the subdomain-gap canary
- [ ] `Location: https://evil.com/target.com` — the substring-gap canary
- [ ] `Location: https:evil.com` — the scheme-no-// canary
- [ ] the meta `content="0;url=<canary>"` — the client-side twin
- [ ] the `location.href="<canary>"` — the JS-twin
- [ ] the `Refresh: 0;url=<canary>` — the header-twin
- [ ] the stored `Location:` on the fire-step — the two-step
- [ ] the Referer-derived `Location:` — the header-carried

## The fingerprint checks — the filter-shape read

- [ ] `Location: /` — the forced-relative fingerprint
- [ ] `Location: https://target.com/` — the host-allowlist fingerprint
- [ ] `Location: <partial>` — the path/host-force fingerprint
- [ ] `Location: <relative>` — the same-origin-resolution negative
- [ ] `Location: <javascript:>` — the scheme-pass fingerprint
- [ ] no `Location:` — the weak-negative (wrong param)

## The bypass-arm checks — the filter-shape arms

- [ ] `//evil.com` — the scheme-relative
- [ ] `/\evil.com`, `\\evil.com`, `/%5cevil.com` — the backslash
- [ ] `https://target.com@evil.com` — the userinfo
- [ ] `evil.com\@target.com` — the `\@`
- [ ] `https://evil.com%40target.com` — the encoded `@`
- [ ] `https://target.com.evil.com` — the subdomain
- [ ] `eviltarget.com`, `target-com.evil.com` — the no-boundary/hyphen
- [ ] `https://evil.com/target.com`, `?target.com`, `#target.com` — the substring
- [ ] `https:evil.com`, `https:/\evil.com`, `https:\\evil.com` — the scheme
- [ ] `https%3a%2f%2fevil.com`, `%2f%2fevil.com` — the encoded
- [ ] `https%253a%252f%252fevil.com` — the double-encoded
- [ ] `javascript:`, `data:`, `vbscript:`, `file:` — the scheme-family
- [ ] the unicode/fullwidth — `%ef%bc%8f`, `%ef%bc%8e`, `%ef%bc%a0`
- [ ] the whitespace/control — `%20`, `%09`, `%0a`, `%0d%0a`

## The surface checks — the endpoint + carrier coverage

- [ ] `/login`/`/logout`/`/oauth`/`/sso`/`/out`/`/goto`/`/link` swept
- [ ] `/back`/`/error`/`/checkout`/`/share`/`/qr` swept
- [ ] the `Location:`/meta/JS/Referer/stored carriers checked
- [ ] the bundle's `location.*` sinks mined
- [ ] the stored set-then-fire pair checked

## The falsifier checks

- [ ] EVERY canary + arm -> `Location: <safe>` — the class falsifier
- [ ] the arms-tried list is recorded
- [ ] the verbatim safe `Location`s are the falsifier's evidence
- [ ] the unswept surfaces are noted (the falsifier closes the swept surface)

## The chain checks

- [ ] the OAuth launder — the open-redirect on an allowlisted domain
- [ ] the SSRF-fetch — a fetcher that follows `Location`
- [ ] the XSS-sink — the `javascript:`/`data:` scheme
- [ ] the bot-visit — a bot that visits target.com URLs
- [ ] the CRLF-split — `%0d%0a` in the `Location:`
- [ ] the phishing-launder — the standalone class-answer

## The evidence checks

- [ ] the verbatim `Location:`/carrier-value recorded — the bytes
- [ ] the status (302/301/303/307/308/200) recorded
- [ ] the payload sent recorded — the exact param value
- [ ] `post-probe --evidence` is a substring of `--response`
- [ ] `--evidence-kind class` for the oracle, `impact` for the chain
- [ ] the negatives/falsifiers recorded with the arms-tried
