# Open redirect filter bypasses

An open redirect is almost worthless alone — its value is what it *launders*:
an OAuth code, a phishing URL that starts on a trusted domain, an SSRF that
follows the Location it was handed, a `javascript:` that survives to a
client-side redirect. Test for the payoff, not just the 302.

## Finding the parameter

Any parameter that ends up in a `Location` header, a `meta refresh`, or a
`window.location` assignment: `next`, `url`, `redir`, `return`, `returnTo`,
`goto`, `dest`, `target`, `continue`, `out`, `view`, `callback`, `to`.
The most-missed spot is the *error/logout/login* path — a 302 after a failed
login that still honours `next`.

## The filter-bypass alphabet

A filter that "requires the host" fails on a different parse than the one it
checks. Send every arm of the pair:

| Filter idea | Bypass shape |
|---|---|
| must start with `/` | `//evil.com` (scheme-relative) |
| must contain `target.com` | `evil.com/target.com`, `evil.com?target.com`, `evil.com#target.com` |
| substring whitelist | `target.com.evil.com`, `target.com-evil.com` |
| suffix match | `eviltarget.com` (no dot boundary) |
| userinfo ignored | `https://target.com@evil.com/` |
| `@` stripped before host check | `https://evil.com\@target.com/` |
| dot or slash required | `https://evil%2ecom`, `https:/%5cevil.com` |
| host allowlist by parse | `https://target.com.evil.com` — `urllib`/browser disagree |
| backslash normalization | `https:\/\/evil.com`, `https://target.com\evil.com` |
| CRLF in Location | `%0d%0a` splitting the header |
| base64/decoded first | `?next=aHR0cHM6Ly9ldmls` |

Client-side redirects (`window.location`, meta refresh, `location.hash` flows)
skip the server check entirely — read the bundle for `location.*=` and feed it
the parameter it reads.

## The payoff chain

| Redirect leads to | The class it becomes |
|---|---|
| OAuth `redirect_uri` or SSO callback | `../web-oauth-sso/` — token leaks to your collector |
| `javascript:` or `data:` | `../web-xss/` — script context, not navigation |
| internal address the server then fetches | `../web-ssrf/` — the redirect is the SSRF's second hop |
| a page that reads the fragment | `../web-xs-leaks/` — fragment survives the redirect |

## Confirm wording

The finding is the *reachable external destination*, not the parameter: name
the exact payload that produced a `Location` (or client-side navigation) to a
host you control, and what that launders.

## Falsifier

Every bypass shape stays on the target's origin — the parameter is parsed,
allowlisted by exact match, and `javascript:`/`data:` are rejected on all
paths including the client-side ones.

## Traps

- A 302 to `/login?error=` is not the finding; the *Location value* must be
  your host.
- Some apps only honour the parameter on a second visit or a specific method —
  retry the winning shape via GET and POST.
- `Referer`-based redirects (back buttons) accept the header as input — an
  often-missed parameter surface.
