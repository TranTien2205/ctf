# Common questions (deep) — the operator's extended FAQ

## "The `Location:` is `//evil.com` — is that the gap?"

Yes — `//evil.com` is scheme-relative — the browser inherits the page's
scheme (`https:` on `https://target.com`) and resolves to
`https://evil.com` — cross-origin. That's a CANDIDATE — the verbatim
`Location: //evil.com` is the evidence.

## "The `Location:` is `evil.com` — same thing?"

NO — `Location: evil.com` (no scheme, no `//`) resolves RELATIVE to the
request's URL → `https://target.com/evil.com` — same-origin, a relative
path. The gap needs `//`/`scheme`/`\\` — a bare host is a relative-path.

## "The allowlist checks the HOST — is it safe?"

The check's PARSER matters — `urlparse(...).hostname` vs a substring vs a
netloc vs a regex. The bypass is where the filter's parse disagrees with
the browser's WHATWG parse — the `\@`, the `%5c`, the encoded-host, the
userinfo `@`, the subdomain. `per-check.md`/`parser-differentials.md`.

## "The `javascript:` reached the sink — is it XSS?"

The sink-value is the evidence — `location.href="javascript:..."` proves
the scheme reaches the sink. Whether it FIRES is browser-split — Chrome
blocks `location.href='javascript:...'` in some contexts; `data:`/`blob:`
may pass. Record the sink-value; the firing is a separate check.

## "The redirect confirms — what's the flag?"

The class-confirm is hop-0 — the `Location: <canary>`. The flag-path is
the laundered-trust — `chain-routes.md`: the OAuth-code launder, the
SSRF-fetch, the XSS, the bot-visit, or the standalone phishing launder.

## "Every arm returns `Location: /` — closed?"

For the SWEPT surface — yes, the class falsifier on that surface. The
reopen is an unswept endpoint/carrier — `/logout`, `/error`, `/back`-
Referer, the stored two-step, the meta/JS twin.

## "The Referer-derived redirect — is that the class?"

Yes — the header-carried variant. `Referer: evil.com -> Location: evil.com`
is the verbatim evidence; record `carrier: referer-derived`.

## "The stored-redirect — the set-param 302s but the fire doesn't?"

The stored value is re-validated at READ-time — a two-step where the set
is unchecked but the fire checks — a chain-dead stored-redirect. Record
both steps.

## "The `Location:` carries the canary but the client doesn't navigate?"

The verbatim `Location: <canary>` IS the server-side evidence — the class
confirm. Whether a specific CLIENT navigates is the client-side-split —
a `javascript:` blocked, a `data:` allowed. Record the server-side
`Location:` as the class-confirm; the client's nav is a separate question.

## "The OAuth `redirect_uri` is `https://allowed.com/*` — how does the open-redirect help?"

Find an open-redirect ON `allowed.com` — `redirect_uri =
https://allowed.com/redirect?next=https://evil.com` — the OAuth server
302s to the allowlisted URL which 302s to evil.com — the code lands on
the canary.

## "The `Location:` is `Location: ` + a relative path the param set — open?"

`Location: /evil.com` — a relative path on the origin — NOT the gap. The
param set the PATH; the host is the origin. `//evil.com`/`https://evil.com`
are the cross-origin forms.

## "The meta-refresh carries the canary — the server emitted it?"

The server rendered the `<meta>` tag — the NAVIGATION is client-side.
The verbatim `content="0;url=<canary>"` is the evidence — the client-side
twin — record `carrier: meta-refresh`.

## "A `Location:` with a port — `Location: https://evil.com:8443`?"

The port is surface-detail — `evil.com:8443` is host=`evil.com`, port=8443
— cross-origin. The `Location: https://evil.com:8443` is the canary —
CANDIDATE.

## "The redirect carries the canary but the challenge wants a flag?"

The class-confirm is the verbatim `Location: <canary>` — if the challenge
is the phishing/launder shape, that IS the answer. Otherwise the flag is
the laundered-trust — `chain-routes.md` for the OAuth/SSRF/XSS/bot route.
