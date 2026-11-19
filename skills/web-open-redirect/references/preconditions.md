# Preconditions — what must be true for the class to apply

## The presence preconditions

```text
1. a redirect-param exists — a request value that lands in a Location,
   a meta-refresh, a JS-nav, or a Refresh header
2. the value is attacker-controlled — a GET query, a POST body, a cookie,
   a Referer, a fragment the JS reads
3. the server emits the destination UNCHECKED — no allowlist, no
   relative-path force, no parse-boundary that catches every arm
```

## The mechanism preconditions

```text
4. the carrier is a redirect — a 3xx Location OR a client-side meta/JS
   nav; a reflected link (the victim must click) is a phishing surface
   not a server-side open-redirect
5. the value survives to the carrier — not stripped/sanitized/escaped
   before the Location/meta/JS
6. the browser resolves it cross-origin — a `Location: evil.com` (no
   scheme/`//`) resolves RELATIVE to the origin — same-origin, not open
```

## The chain preconditions — when the redirect alone isn't enough

```text
7. for the OAuth chain:   the open-redirect must be ON an allowlisted
   redirect_uri domain (or reachable through one)
8. for the SSRF chain:    the fetcher must follow 3xx Location
9. for the XSS chain:     the scheme must reach a client-side sink
   unblocked (a javascript:/data:)
10. for the bot chain:    the bot must visit the URL and run the JS
    that navigates
11. for the phishing chain: the URL must start on the trusted domain —
    https://target.com/login?next=https://evil.com
```

## The falsifier preconditions — when the class is closed

```text
12. the destination is allowlisted — every arm -> a safe Location
13. the destination is forced-relative — every arm -> Location: /<path>
14. the param isn't a redirect — no Location/meta/JS carrier
15. the param is sanitized — the client-side twin is escaped
16. the chain precondition fails — the redirect confirms but doesn't launder
```

## The surface preconditions — the per-surface presence

| The surface | The precondition |
|---|---|
| the post-login `next` | a login flow + a `next` param |
| the OAuth `redirect_uri` | an OAuth/SSO flow + a redirect_uri param |
| the tracker `url`/`out` | a link-tracker feature |
| the fetcher `url`/`img` | a server-side fetch feature |
| the Referer-derived `/back` | a flow that reads the Referer |
| the stored-redirect | a param that persists to a later flow |
| the meta-refresh | a server-rendered meta tag |
| the JS-nav | a bundle `location.*` sink fed by a param |
| the `location.hash` | a fragment-param read by the JS |

## The tool preconditions

```text
- python3 + tools/web/redirect_probe.py (a --selftest proves it)
- curl for the verbatim-Location read
- urllib.parse for the encoding
- the bundle_miner.py for the client-side JS-sink
```

## The precondition-check order

```text
1. is there a redirect-param?          -> the vocabulary sweep
2. does it reach a redirect carrier?   -> the Location/meta/JS read
3. is it attacker-controlled?          -> the canary
4. is it unchecked?                    -> the Location carries the canary?
5. does it launder?                    -> the chain-route precondition
```
