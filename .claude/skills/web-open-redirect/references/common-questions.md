# Common questions — the recurring operator confusions

## "The param is `next` — it's a redirect param; is that enough?"

No — a redirect PARAM is surface. The confirm needs a `Location:` header
carrying your canary verbatim. `?next=` existing + a 302 existing ≠ the
redirect carries the canary.

## "The Location is `evil.com` — is that open?"

`Location: evil.com` resolves RELATIVE to the origin →
`target.com/evil.com` — same-origin, not open. The cross-origin forms
are `//evil.com` (scheme-relative) or `https://evil.com` (absolute).

## "The server returned `Location: /` — the filter blocked it; done?"

For THAT arm — yes, a strong-negative. The class isn't closed until
EVERY bypass arm returns a safe `Location` — the falsifier. One arm
blocked ≠ the class closed; sweep the filter-shape-specific arms.

## "The `javascript:` reached the sink but didn't fire — confirmed?"

The sink-value is the verbatim evidence — `location.href="javascript:..."`
proves the SCHEME reaches the sink. Whether it FIRES is browser-split
(Chrome blocks `location.href='javascript:...'` in some contexts). Record
the sink-value as the candidate; the firing is a separate client-side check.

## "The OAuth `redirect_uri` is allowlisted — is the chain dead?"

The allowlist on `redirect_uri` is strict BUT the allowlisted domain may
itself have an open-redirect — `redirect_uri = https://allowlisted.com/
redirect?next=https://evil.com` — the OAuth server redirects to the
allowlisted URL which then redirects to evil.com. The chain is dead only
if the allowlisted domains have NO open-redirect.

## "The SSRF fetcher doesn't follow redirects — the chain is dead?"

For THAT fetcher — yes. But a fetcher that DOES follow is the bypass for
an IP-literal filter on its URL. Check the fetcher's `follow_redirects`
behavior — some follow by default.

## "The meta-refresh carries the canary — is that a server-side redirect?"

No — the meta-refresh is the CLIENT-side twin. The server rendered the
`<meta>` tag but the NAVIGATION is client-side. Same class, different
carrier — record `carrier: meta-refresh` and the verbatim `content=` value.

## "A `Location:` on a non-3xx — is that a redirect?"

A `Location:` on a 200/201 isn't a NAV redirect — some APIs set `Location:`
as a "created-at" hint. The oracle needs a 3xx OR a client-side carrier.
Record the status; a non-3xx `Location` isn't the open-redirect oracle.

## "The `location.hash` carries the param — is that a redirect?"

`location.hash` changes the FRAGMENT — same-page, no origin change. It's
a redirect only if the page's JS parses the hash and assigns it to
`location.href` — the DOM-sink surface.

## "I found `?next=` on EVERY endpoint — which is the bug?"

Every endpoint with a `next` is a candidate surface — test each with the
canary. The BUG is the one whose `Location:` carries the canary. The
post-login/logout/oauth/tracker surfaces are the high-value ones.

## "The redirect confirms — what's the flag?"

A standalone `Location: <canary>` IS the class-answer if the challenge
is the phishing/domain-launder shape. Otherwise route to the chain —
`chain-routes.md` — OAuth/SSRF/XSS/bot.

## "The Referer-derived redirect confirms — is that the class?"

Yes — a Referer-derived open-redirect is this class's header-carried
variant. `Referer: evil.com -> Location: evil.com` is the verbatim
evidence; record `carrier: referer-derived`.

## "The double-encode arm works — is that a different bug?"

Same class, different arm — the double-decode is a decode-order gap in
the filter. Record the arm + the decode-stage.

## "The server returns `Location: ` the param VERBATIM but it resolves same-origin — open?"

`Location: evil.com` (no scheme/`//`) resolves relative — same-origin,
not open. Only the `//`/`scheme`/`\\` forms cross the origin.
