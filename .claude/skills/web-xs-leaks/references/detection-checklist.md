# Detection checklist — a self-audit for finding the XS-leak surface

The checklist that confirms each surface before building the oracle.

---

## The bot — does one exist

```text
[ ] a /report endpoint that takes a URL
[ ] a browser (puppeteer/playwright/selenium/headless)
[ ] a flag-holder session (a flag cookie, an admin context)
[ ] a managed policy (URLBlocklist/URLAllowlist) — a forced sealed shape
[ ] an airgapped bot — no external listener reach
```

## The sub-shape — which one is it

```text
[ ] CLASSIC — the bot visits MY URL → my JS measures a side-channel
[ ] SEALED  — a fixed URL + script-blocked CSP → a declarative/
              server-state channel
[ ] the deciding question — can ANY origin the bot reaches run my JS?
```

## The CSP — what's allowed

```text
[ ] script-src 'none' — no attacker JS → the sealed shape
[ ] style-src 'unsafe-inline' — styles survive → the CSS oracle
[ ] font-src 'self' * — a font wildcard → the @font-face exfil
[ ] img-src 'self' — a bg-image exfil blocked
[ ] default-src 'unsafe-inline' — a broad hole → check each directive
```

## The reflected secret — is it CSS-matchable

```text
[ ] a secret in an ATTRIBUTE — a CSS-selector target
    (data-secret, value=, placeholder=, a custom data-*)
[ ] a secret in TEXT — a @font-face unicode-range target
[ ] a secret the page renders — a readable surface
```

## The server-state surface — what mutates

```text
[ ] a redis LRU store — the eviction channel
[ ] a counter — the read-back channel
[ ] a one-shot token — the single-use flag
[ ] a rate-limit bucket — the quota channel
[ ] a 'last seen' timestamp — the recency channel
[ ] a session/store mutation — the GET's side-effect
```

## The CSS-injection surface — can I inject a stylesheet

```text
[ ] a custom-CSS/theme surface
[ ] a <link rel=stylesheet> the page loads
[ ] a font-family/unicode-range surface
[ ] an @import surface
```

## The classic-surface — what the JS measures

```text
[ ] a frame-count surface — a per-result iframe
[ ] a status surface — a 200/404 search
[ ] a timing surface — a slow-vs-fast path
[ ] a cache-probe surface — a cached resource
[ ] a :visited surface — a history read
[ ] a window.open surface — a navigation check
```

## The delivery — does the page reach the bot

```text
[ ] a /report endpoint — the URL the bot opens
[ ] a data: URL — an airgapped/null-origin case
[ ] a stored page — a same-origin case
[ ] a fragment — a #id the bot's page reads
```

## The exfil — does the data reach me

```text
[ ] a listener — the classic exfil
[ ] a write-back — an airgapped case
[ ] a DOM-writeback — a screenshotting bot
[ ] a server-state read — a counter/recency/token
```

## The control pair — is it buildable

```text
[ ] an always-true condition — a URL/selector that always hits
[ ] a never-true condition — a URL/selector that never hits
[ ] both controls are buildable — the channel's discrimination is testable
```

## The feasibility — is the channel viable

```text
[ ] the secret's TTL — the leak+decode+submit fits the window
[ ] the request rate — the markers fit the rps cap
[ ] the bits/visit — the channel's bandwidth is enough
[ ] the char-set — the alphabet is searchable
[ ] the bot's context — a flag-holder session
```

## The confusables — is it really an XS-leak

```text
[ ] a fetch READS bytes — web-cors
[ ] a WRITE — web-csrf
[ ] a JSONP/postMessage broadcast — a real read primitive
[ ] a stored response — web-cache-poisoning
[ ] a script-tag serve — a real read primitive
[ ] the response is OPAQUE — web-xs-leaks (a measure)
```

## The falsifier — is the surface dead

```text
[ ] a sealed shape with no CSS oracle AND no server-state channel
[ ] an airgapped bot with no server-state read
[ ] a secret not in an attribute AND not in text
[ ] a managed-policy bot with no declarative channel
```
