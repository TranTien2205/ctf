# Attack shapes — the named cache-poisoning attacks, end to end

The named attacks — each with its setup, mechanism, probe, and falsifier.

---

## Attack 1 — the unkeyed-header poisoning

```text
setup:   an app that reflects a header — a cache that ignores it
mechanism: the stored copy carries YOUR header's effect — every
         requester's copy serves it
probe:   a unique marker in the header, then a clean request — the
         marker reflects → poisoned
falsifier: the header IS keyed — the marker doesn't reach a clean request
```

## Attack 2 — the authenticated-page-served-anonymously

```text
setup:   an authenticated page cached under a shared URL — the cache
         keys on the URL, not the auth
mechanism: the stored copy serves the privileged page to anyone
probe:   authenticated GET then anonymous GET — the anonymous request
         returns 200 + HIT + the authenticated body
falsifier: the anonymous request 302s to /login
```

## Attack 3 — the host-rewrite URL poisoning

```text
setup:   an app that builds absolute URLs from X-Forwarded-Host —
         a cache that ignores it
mechanism: the stored copy's links/scripts point to YOUR domain —
         every requester's fetch hits you
probe:   X-Forwarded-Host: attacker.com, then a clean request — the
         stored copy's links carry attacker.com
falsifier: the header IS keyed — the links don't carry your host
```

## Attack 4 — the charset-XSS injection

```text
setup:   an unkeyed reflected charset — an app that decodes it
mechanism: an injected charset XSS stored in the cached page — the
         privileged bot's XSS writes files
probe:   Accept-Charset: <payload>, then a clean request — the stored
         copy carries the charset-decoded XSS
falsifier: the charset isn't reflected — no injection surface
```

## Attack 5 — the personalized-page per-user leak

```text
setup:   a personalized page cached under a shared URL — the cache
         keys on the URL, not the session
mechanism: the stored copy serves YOUR session's content to every
         requester — a session-data leak
probe:   an authenticated GET stores YOUR content; a clean request —
         YOUR session's content reflected
falsifier: a Vary: Cookie — a per-session copy — not a shared one
```

## Attack 6 — the path-normalization deception

```text
setup:   a path the cache and the app normalize differently
mechanism: the stored copy's URL is the victim's URL, the response is
         YOUR request's — a route confusion
probe:   /static/../admin?cb=<unique>, then a clean request — the
         stored copy's response is the app's
falsifier: the app and the cache normalize the same way — no confusion
```

## Attack 7 — the unkeyed-param poisoning

```text
setup:   a stripped param — an app that reflects it — a cache that
         ignores it
mechanism: the stored copy carries the param's effect under the
         shared URL — every requester's copy serves it
probe:   a unique marker in the param, then a clean request — the
         marker reflects → poisoned
falsifier: the param IS keyed — the marker doesn't reach a clean request
```

## Attack 8 — the scheme-downgrade deception

```text
setup:   an unkeyed X-Forwarded-Scheme — an app that builds URLs from it
mechanism: the stored copy's links point to http — a downgrade surface
probe:   X-Forwarded-Scheme: http, then a clean request — the stored
         copy's links use http
falsifier: the scheme IS keyed — the links don't downgrade
```

## Attack 9 — the stored-XSS-bot injection

```text
setup:   an unkeyed reflected payload — a bot that renders the page
mechanism: the stored copy carries the XSS — the bot's render runs it
         — a privileged-context read
probe:   a reflected payload, then the bot's visit — the bot's action
         on your listener
falsifier: the payload isn't reflected — no injection surface
```

## Attack 10 — the per-cookie deception

```text
setup:   an unkeyed cookie — an app that personalizes on it
mechanism: the stored copy carries the per-cookie response to every
         requester — a per-cookie confusion
probe:   a unique cookie, then a clean request — the stored copy's
         response is the per-cookie one
falsifier: the cookie IS keyed (Vary: Cookie) — a per-session entry
```

## Attack 11 — the scheme-header deception

```text
setup:   an unkeyed X-Forwarded-Proto — an app that builds URLs from it
mechanism: the stored copy's links use the proto — a scheme confusion
probe:   X-Forwarded-Proto: <proto>, then a clean request — the stored
         copy's links use it
falsifier: the proto IS keyed — a per-proto entry
```

## Attack 12 — the X-Original-URL deception

```text
setup:   an unkeyed X-Original-URL — an app that honors it
mechanism: the stored copy serves the rewritten response under the
         public URL — a path-rewrite deception
probe:   X-Original-URL: /admin, then a clean request — the stored
         copy serves /admin under /page
falsifier: the header isn't honored — no rewrite
```
