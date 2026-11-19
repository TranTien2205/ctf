# Checklist — the open-redirect verification pass

## The presence checks

- [ ] a redirect-param name is in the vocabulary (`param-inventory`)
- [ ] the param lands in a `Location:`/meta-refresh/JS-nav carrier
- [ ] the first canary (`?next=https%3A%2F%2Fattacker.invalid`) is sent
- [ ] the verbatim `Location:` header is read — `--max-redirs 0` / `-i`

## The fingerprint checks

- [ ] `Location: <canary>` — a candidate; record verbatim
- [ ] `Location: /`/`Location: <safe>` — the fingerprint names the filter
- [ ] `Location: <partial-canary>` — a path-only / host-force fingerprint
- [ ] no `Location` — a weak-negative (the param name is wrong)

## The bypass checks — by filter shape

- [ ] `//evil.com` tried against a `startswith('/')` check
- [ ] `/\evil.com`, `\\evil.com`, `%5c` tried against a `//`-block
- [ ] `https://target.com@evil.com`/`evil.com\@target.com` against a
      substring/hostname check
- [ ] `https://target.com.evil.com`/`eviltarget.com` against a suffix/
      contains check
- [ ] `https%3a%2f%2fevil.com`, `%252f` double-encode against an encoded-
      check
- [ ] `javascript:`/`data:` against a scheme-gap
- [ ] a unicode/fullwidth arm against an ASCII-check
- [ ] a whitespace/tab/CRLF arm against a trim-gap

## The surface checks

- [ ] the post-login `next`/`return`/`continue`
- [ ] the post-logout `next`/`post_logout_redirect_uri`
- [ ] the OAuth/SSO `redirect_uri`/`callback`/`RelayState`
- [ ] the tracker `url`/`link`/`target`/`out`
- [ ] the fetcher `url`/`img`/`feed`/`uri` (the SSRF-twin check)
- [ ] the multi-step `back`/`cancel`/`return`
- [ ] the error-path `next`/`url`
- [ ] the stored-redirect set-then-fire pair
- [ ] the Referer-derived `/back`
- [ ] the client-side meta/JS/`location.hash` surface

## The falsifier checks

- [ ] EVERY canary + bypass arm → `Location: <safe>` — the class falsifier
- [ ] the param produces NO Location/meta/JS — a weak-negative (wrong param)
- [ ] the client-side twin is escaped/sanitized — the twin is closed
- [ ] the chain precondition fails — the redirect confirms but doesn't launder

## The evidence checks

- [ ] the verbatim `Location:` value is recorded — the bytes, not a summary
- [ ] the status (302/301/303/307/308) is recorded
- [ ] the payload sent is recorded — the exact `next=` value
- [ ] the client-side-twin evidence is the verbatim attribute/assignment
- [ ] the chain-impact is the downstream observation, not "the chain works"
- [ ] `post-probe` runs with `--evidence` a substring of `--response`

## The chain checks

- [ ] the `redirect_uri` launder — is the open-redirect on an allowlisted domain?
- [ ] the SSRF-fetch-follow — does the fetcher follow `Location`?
- [ ] the `javascript:`/`data:` sink — is the scheme reachable and unblocked?
- [ ] the bot-visit — does a bot visit the URL and run JS?
- [ ] the CRLF split — does `%0d%0a` reach the header bytes?

## The budget checks

- [ ] ≤5 probes on the mechanism; a uniform falsifier stops it
- [ ] the bypass arms are chosen by the fingerprint, not swept blindly
- [ ] a confirm/negative/falsifier is recorded for every probe
