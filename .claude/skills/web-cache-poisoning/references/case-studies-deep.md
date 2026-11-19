# Case studies deep — the named cache-poisoning shapes, exhaustively

The full mechanics for each shape — the setup, the probe, the falsifier.

---

## Case 1 — the authenticated-page-served-anonymously (the verified card)

```text
setup:   a Rails app behind an nginx proxy_cache — an authenticated
         /settings.html — the cache keys on the URL, not the auth
mechanism: an authenticated GET stores the privileged page; an
         anonymous GET for the same key gets the privileged copy
probe:   authenticated GET then anonymous GET — the anonymous request
         returns 200 + X-Cache-Status HIT + the authenticated body
falsifier: the anonymous request 302s to /login
blast:   every anonymous requester gets the privileged page until
         the TTL expires
```

## Case 2 — the unkeyed-reflected-header poisoning

```text
setup:   an app that reflects a header — an nginx proxy_cache that
         keys on the URL, not the header
mechanism: a request with the header stores a response that carries
         the header's effect — a clean request for the same key gets
         the stored copy — YOUR header's effect is in the shared copy
probe:   a unique marker in the header, then a clean request — the
         marker reflects → poisoned
falsifier: the header IS keyed — the marker doesn't reach a clean request
```

## Case 3 — the host-rewrite URL poisoning

```text
setup:   an app that builds absolute URLs from X-Forwarded-Host —
         a cache that ignores the header
mechanism: the app's absolute URLs use YOUR host — the stored copy's
         links/scripts point to YOUR domain — every requester's fetch
         hits you
probe:   X-Forwarded-Host: attacker.com, then a clean request — the
         stored copy's links carry attacker.com
falsifier: the header IS keyed — the links don't carry your host
```

## Case 4 — the charset-XSS injection (the verified card's injection)

```text
setup:   an unkeyed reflected charset — an app that decodes the charset
mechanism: an injected charset XSS stored in the cached page — the
         privileged bot's XSS writes files inside the container
probe:   Accept-Charset: <payload>, then a clean request — the stored
         copy carries the charset-decoded XSS
falsifier: the charset isn't reflected — no injection surface
```

## Case 5 — the personalized-page per-user leak

```text
setup:   a personalized page (a profile) cached under a shared URL —
         the cache keys on the URL, not the session
mechanism: the stored copy serves YOUR session's content to every
         requester — a session-data leak
probe:   an authenticated GET stores YOUR content; a clean request —
         YOUR session's content reflected
falsifier: a Vary: Cookie — a per-session copy — not a shared one
```

## Case 6 — the path-normalization deception

```text
setup:   a path the cache and the app normalize differently — a static-
         looking URL served the dynamic response
mechanism: the cache stores the response under a static key — the
         app's dynamic response is served under the victim's URL
probe:   /static/../admin?cb=<unique>, then a clean request — the
         stored copy's response is the app's
falsifier: the app and the cache normalize the same way — no confusion
```

## Case 7 — the unkeyed-param poisoning

```text
setup:   a stripped param — an app that reflects it — a cache that
         ignores it
mechanism: the stored copy carries the param's effect under the
         shared URL — every requester's copy serves it
probe:   a unique marker in the param, then a clean request — the
         marker reflects → poisoned
falsifier: the param IS keyed — the marker doesn't reach a clean request
```

## Case 8 — the scheme-downgrade deception

```text
setup:   an unkeyed X-Forwarded-Scheme — an app that builds URLs from it
mechanism: the app's absolute URLs use YOUR scheme — the stored copy's
         links point to http — a downgrade surface
probe:   X-Forwarded-Scheme: http, then a clean request — the stored
         copy's links use http
falsifier: the scheme IS keyed — the links don't downgrade
```

## Case 9 — the UA-dependent deception

```text
setup:   an unkeyed User-Agent — an app that personalizes on it
mechanism: the stored copy serves YOUR UA's response to every
         requester — a mobile-vs-desktop confusion
probe:   a unique UA, then a clean request — the stored copy's response
         is the per-UA one
falsifier: the UA IS keyed — a per-UA entry
```

## Case 10 — the cookie-dependent deception

```text
setup:   an unkeyed cookie — an app that personalizes on it
mechanism: the stored copy carries the per-cookie response to every
         requester — a per-cookie confusion
probe:   a unique cookie, then a clean request — the stored copy's
         response is the per-cookie one
falsifier: the cookie IS keyed (Vary: Cookie) — a per-session entry
```
