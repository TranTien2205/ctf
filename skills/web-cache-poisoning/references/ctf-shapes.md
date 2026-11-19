# CTF shapes — the cache-poisoning designs that appear in challenges

The named challenge patterns, with the mechanics that identify them.

---

## The "authenticated-served-anonymously" shape — the verified card

```text
an authenticated page cached under a URL the anonymous requester
also fetches — the cache keys on the URL, not the auth state — the
stored copy is the privileged page served to anyone. the HTB
Encodecept shape.
```

## The "unkeyed-header-poisoned-page" shape — the injected response

```text
an unkeyed reflected header — YOUR header's effect is stored under
the public URL — every requester's copy carries YOUR injected
content. the classic cache-poisoning shape.
```

## The "path-normalization" shape — the route confusion

```text
a path the cache and the app normalize differently — a static-looking
URL served the dynamic response — the stored copy's URL is the
victim's URL, the response is YOUR request's.
```

## The "personalized-served-publicly" shape — the per-user leak

```text
a personalized page (a profile, a dashboard) cached under a shared
URL — the stored copy serves YOUR personalized content to every
requester — a session-data leak.
```

## The "Host-header" shape — the URL-rewrite leak

```text
an unkeyed Host/X-Forwarded-Host — the app's absolute URLs use YOUR
host — the stored copy's links point to YOUR domain — a redirect/
phishing surface.
```

## The "scheme-header" shape — an http/https downgrade

```text
an unkeyed X-Forwarded-Scheme — the app's absolute URLs use YOUR
scheme — the stored copy's links point to http — a downgrade.
```

## The "UA-dependent" shape — a per-UA response

```text
an unkeyed User-Agent — the app personalizes on the UA — the stored
copy serves YOUR UA's response to every requester.
```

## The "language" shape — a localized response

```text
an unkeyed Accept-Language — the app localizes on it — the stored
copy serves YOUR language to every requester.
```

## The "cookie" shape — a per-cookie response

```text
an unkeyed cookie — the app personalizes on it — the stored copy
carries the per-cookie response to every requester.
```

## The "param-append" shape — a keyed-param confusion

```text
a keyed param the app ignores vs an unkeyed param the app reads —
the deception is in which param carries the effect and which carries
the key.
```

## The "charset-XSS" shape — the verified card's injection

```text
an unkeyed reflected charset — an injected charset XSS stored in
the cached page — the privileged bot's XSS writes files inside the
container — the chain that reaches the flag.
```

## The "keyed-param" shape — a cache-buster defeat

```text
a keyed param the app ignores — the stored entry is keyed per-value
— a fresh entry, not a poisoned one — a cache-buster defeats the
poisoning.
```

## The per-shape vector-selection

```text
an authenticated + a shared cache    → authenticated-served-anonymously
a personalized + a shared cache      → personalized-served-publicly
an unkeyed reflected header          → injected-response
a path normalization boundary        → route-confusion
an unkeyed Host                      → URL-rewrite
an unkeyed X-Forwarded-Scheme        → scheme-downgrade
an unkeyed User-Agent                → per-UA confusion
an unkeyed Accept-Language           → localized confusion
an unkeyed cookie                    → per-cookie confusion
a reflected charset                  → a charset-XSS injection
a keyed param                        → a cache-buster defeat
```

## The shape's blast radius — the shared-store effect

```text
a poisoned entry is served to EVERY requester of the URL until it
expires — a public URL poisons every visitor — a niche URL poisons
a few — the blast radius is the URL's requester base.
```

## The shape's falsifier — when it doesn't apply

```text
the input IS part of the cache key — the stored copy is keyed per-
input → a different class.
no front-end cache → no stored response → a different class.
a Cache-Control: no-store/private → the page isn't cached → a
different class.
```
