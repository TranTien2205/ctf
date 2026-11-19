# Real-world cases — where cache poisoning appears in actual challenges

The named shapes with the mechanics that identify them.

---

## The classic shapes — the unkeyed-input poisoning

### An unkeyed reflected header — the injected response

```text
an X-Forwarded-Host/Referer/User-Agent the app reflects but the
cache ignores — YOUR header's effect is stored under the public URL
— every requester's copy carries YOUR injected content. the classic
shape.
```

### An unkeyed query param — a tracking-param poisoning

```text
a utm/fbclid/gclid the app reflects but the cache ignores — YOUR
param's effect is stored under the shared URL — every requester's
copy carries YOUR input.
```

### An unkeyed cookie — a per-cookie poisoning

```text
a cookie the app reads but the cache doesn't Vary on — YOUR cookie's
effect is stored under the shared URL — a per-cookie response served
to every requester.
```

### A path-normalization boundary — the route confusion

```text
a path the cache and the app normalize differently — a static-looking
URL served the dynamic response — the stored copy's URL is the
victim's URL, the response is YOUR request's.
```

## The deception shapes — the stored-response confusion

### The authenticated-page-served-anonymously — the verified card

```text
an authenticated page cached under a URL the anonymous requester
also fetches — the cache keys on the URL, not the auth state — the
stored copy is the privileged page served to anyone. the HTB
Encodecept shape — the card's first probe: an authenticated GET
then an anonymous GET — the anonymous request returns the privileged
page.
```

### The personalized-page-served-publicly — the per-user leak

```text
a personalized page (a profile, a dashboard) cached under a shared
URL — the stored copy serves YOUR personalized content to every
requester — a session-data leak.
```

### The Host-header deception — the URL-rewrite leak

```text
an unkeyed Host/X-Forwarded-Host — the app's absolute URLs use YOUR
host — the stored copy's links point to YOUR domain — a redirect/
phishing surface — every requester's links go to YOUR domain.
```

### The scheme-header deception — an http/https downgrade

```text
an unkeyed X-Forwarded-Scheme — the app's absolute URLs use YOUR
scheme — the stored copy's links point to http — a downgrade or a
mixed-content surface.
```

### The UA-dependent deception — a per-UA response

```text
an unkeyed User-Agent — the app personalizes on the UA — the stored
copy serves YOUR UA's response to every requester — a mobile-vs-
desktop or a browser-specific confusion.
```

### The language deception — a localized response

```text
an unkeyed Accept-Language — the app localizes on it — the stored
copy serves YOUR language to every requester.
```

## The injection shapes — the stored payload

### The charset-XSS shape — the verified card's injection

```text
an unkeyed reflected charset — an injected charset XSS stored in
the cached page — the privileged bot's XSS writes files inside the
container — the chain that reaches the flag.
```

### The reflected-payload shape — a stored script

```text
an unkeyed reflected input carries a payload — a JS, a redirect, a
host-rewrite — the stored copy serves it to every requester — a
stored-XSS-like effect through the cache.
```

## The confusable shapes — the boundary

```text
a fetch READS bytes              → web-cors (a real read)
a WRITE                          → web-csrf
a desync                         → web-request-smuggling
a parser diff                    → web-parser-differential
an opaque response + a side-channel → web-xs-leaks (a measure)
a stored response served to others → web-cache-poisoning (a store)
```

## The per-case vector-selection

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
```
