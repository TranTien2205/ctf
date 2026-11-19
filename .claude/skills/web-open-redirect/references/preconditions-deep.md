# Preconditions (deep) — the complete presence-check list

## The fundamental preconditions — the class's existence

```text
1. a redirect-param exists — a request value that reaches a redirect carrier
2. the value is attacker-controlled — GET/POST/cookie/Referer/session/fragment
3. the server emits the destination UNCHECKED — the allowlist/relative-force
   is missing or has a parse-boundary gap
4. the client follows it cross-origin — the WHATWG parse resolves the value
   to an attacker host
```

## The per-component preconditions

```text
the param:
  - the param NAME is in the vocabulary OR the app invents one
  - the param reaches a carrier — not just reflected
  - the param is the DESTINATION not a fragment/flag the server reads
the filter:
  - the filter is absent OR has a parse-boundary gap
  - the filter's parse differs from the browser's WHATWG parse
  - the filter is on the STRING/ENCODED/PARSED form at the wrong stage
the resolution:
  - the param survives to the carrier — not stripped/sanitized/escaped
  - the resolution doesn't force a host/path/scheme
the carrier:
  - the carrier IS a redirect — a 3xx Location or a client-side nav
  - a non-3xx Location isn't a nav redirect — a REST 'created-at' hint
the navigation:
  - the browser's parse resolves the value cross-origin
  - a bare 'evil.com' (no scheme/ //) resolves relative — same-origin
```

## The per-surface preconditions

```text
the post-login surface:      a login flow + a `next`/`return` param
the post-logout surface:     a logout flow + `next`/`post_logout_redirect_uri`
the OAuth surface:           an OAuth/SSO flow + `redirect_uri`/`callback`/`RelayState`
the tracker surface:         a link-tracker feature + `url`/`target`/`out`
the fetcher surface:         a server-side fetch + `url`/`uri`/`img`
the multi-step surface:      a wizard/form + `back`/`return`/`cancel`
the error-path surface:      an error-redirect + `next`/`url`
the Referer surface:         a `/back` that reads the Referer header
the stored surface:          a param that persists to a later flow
the meta-refresh surface:    a server-rendered `<meta>` + the param
the JS-nav surface:          a bundle `location.*` sink + the param
the location.hash surface:   a fragment-param the JS reads
```

## The chain preconditions — when the launder fires

```text
the OAuth chain:    the open-redirect is ON an allowlisted redirect_uri domain
                    OR reachable through one
the SSRF chain:     a fetcher that FOLLOWS 3xx Location
the XSS chain:      the sink accepts a javascript:/data: scheme AND the
                    browser fires it
the bot chain:      a bot that visits the URL AND runs the JS that navigates
the phishing chain: the URL starts on the trusted domain
the CRLF chain:     a %0d%0a reaching the Location: header bytes
```

## The falsifier preconditions — when the class is closed

```text
- every arm -> Location: <safe>            <- the allowlist/relative-force
- the param isn't a redirect                <- a weak-negative — wrong name
- the client-side twin is escaped           <- the meta/JS sanitized
- the scheme is rejected                    <- the scheme-surface closed
- the stored value re-validated             <- the stored-surface closed
- the Referer validated/not-read            <- the Referer-surface closed
- the chain precondition fails              <- the confirm-but-no-launder
```

## The tool preconditions

```text
- python3 + tools/web/redirect_probe.py     (the --selftest proves it)
- curl for the verbatim Location read
- urllib.parse for the encoding
- tools/web/bundle_miner.py for the client-side JS-sink
```

## The precondition-check order

```text
1. does a redirect-param exist?             -> the vocabulary sweep
2. does it reach a redirect carrier?         -> the Location/meta/JS read
3. is the destination unchecked?            -> the canary's Location
4. does the browser resolve it cross-origin?-> the scheme/ // check
5. does it launder?                          -> the chain-precondition
```

## The precondition-record

`precondition: <the-component>: <the-presence>: <the-verdict>`
