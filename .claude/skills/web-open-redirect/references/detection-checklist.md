# Detection checklist — the systematic surface-verification pass

## Phase A — the param inventory

- [ ] `next` swept on the redirect-prone endpoints
- [ ] `url`/`redir`/`redirect`/`redirect_uri`/`redirect_url` swept
- [ ] `return`/`returnTo`/`returnto`/`return_url`/`ret` swept
- [ ] `goto`/`continue`/`to`/`out`/`view`/`forward` swept
- [ ] `dest`/`destination`/`target`/`link`/`ref`/`referer` swept
- [ ] `callback`/`RelayState`/`relay`/`reply`/`acs` swept
- [ ] `post_logout_redirect_uri`/`logout`/`signout` swept
- [ ] `successUrl`/`cancelUrl`/`failUrl`/`errorUrl` swept
- [ ] `image`/`img`/`src`/`uri`/`feed`/`load`/`file`/`doc` swept
- [ ] `back`/`prev`/`previous`/`site`/`host`/`path` swept
- [ ] the bundle/JS grep for `location.*` sinks done

## Phase B — the carrier inventory

- [ ] `Location:` header checked on each `?param=` (`curl -si | grep -i '^location'`)
- [ ] `Refresh:` header checked (`grep -i '^refresh'`)
- [ ] `<meta http-equiv="refresh">` checked (`grep -i 'refresh'`)
- [ ] `location.href`/`location.replace`/`location.assign` checked
- [ ] `window.location`/`location=`/`location.hash` checked
- [ ] `history.pushState`/`document.referrer` checked
- [ ] the bundle's `location.*` sinks mined (`bundle_miner`/grep)

## Phase C — the fingerprint

- [ ] the first canary sent — `?next=https%3A%2F%2Fattacker.invalid`
- [ ] the ONE `Location:` read — the fingerprint
- [ ] the fingerprint mapped to the filter shape
- [ ] the filter-shape named the arm family

## Phase D — the bypass arms

- [ ] `//evil.com` tried
- [ ] `/\evil.com`, `\\evil.com`, `/%5cevil.com` tried
- [ ] `https://target.com@evil.com`, `evil.com\@target.com` tried
- [ ] `https://target.com.evil.com`, `eviltarget.com` tried
- [ ] `https://evil.com/target.com`, `evil.com?target.com` tried
- [ ] `https:evil.com`, `https:/\evil.com`, `https:\\evil.com` tried
- [ ] `https%3a%2f%2fevil.com`, `%2f%2fevil.com` tried
- [ ] `https%253a%252f%252fevil.com` (double) tried
- [ ] `javascript:`, `data:`, `vbscript:`, `file:` tried
- [ ] the unicode/fullwidth arms tried
- [ ] the whitespace/control arms tried

## Phase E — the verdicts

- [ ] each arm's `Location:` recorded verbatim
- [ ] a `Location: <canary>` -> `post-probe confirms --evidence-kind class`
- [ ] a `Location: <safe>` on all arms -> the class falsifier
- [ ] a no-`Location` -> the param-vocabulary sweep continues
- [ ] a confirmed canary -> `chain-routes.md` for the launder

## Phase F — the chain

- [ ] the OAuth `redirect_uri` launder checked (the open-redirect on an allowlisted domain)
- [ ] the SSRF-fetch-follow checked (does the fetcher follow `Location`?)
- [ ] the `javascript:`/`data:` sink checked (the scheme's reachability)
- [ ] the bot-visit checked (a bot that visits target.com URLs)
- [ ] the CRLF-split checked (`%0d%0a` in the `Location:`)
- [ ] the standalone phishing-launder recorded (the class's own answer)
