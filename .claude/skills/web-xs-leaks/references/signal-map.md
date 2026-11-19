# Signal map — every XS-leak signal, indexed

The complete signal-to-surface map — what each observation names.

---

## The bot signals — the victim-viewer

```text
a /report endpoint            → a delivery surface — the classic shape
a puppeteer/playwright        → a real browser — the render channels
a selenium/chromedriver       → a real browser — the render channels
a JSDOM                       → no render — the DOM/timing channels
a headless/incognito          → a fresh-session case
a URLBlocklist/URLAllowlist   → a managed policy — a forced sealed shape
a setCookie/flag cookie       → the flag-holder session
```

## The CSP signals — the channel's gates

```text
script-src 'none'             → no attacker JS → the sealed shape
style-src 'unsafe-inline'     → styles survive → the CSS oracle
font-src 'self' *             → a font wildcard → the @font-face exfil
img-src 'self'                → a bg-image exfil blocked
default-src 'unsafe-inline'   → a broad hole → check each directive
connect-src 'self'            → same-origin fetches only → a write-back
a CSP nonce                   → an inline-script gate
```

## The reflected-secret signals — the CSS-matchable surface

```text
a data-secret/value= attribute → a CSS-attribute-selector target
a <div id=secret> text node    → a @font-face unicode-range target
a setAttribute                 → a CSS-selector target
an innerHTML/textContent       → a rendered-text target
```

## The server-state signals — the sealed channel

```text
a redis LRU / maxmemory       → the eviction channel
a counter/incr                → the counter channel
a GETDEL/GETEX                → the one-shot-token channel
a rate-limit/remaining        → the quota channel
a last.?seen/timestamp        → the recency channel
a session-mutation            → the session channel
```

## The CSS-injection signals — the declarative channel

```text
a custom.*css/theme           → a stylesheet carrier
a <style>/<link rel=stylesheet> → a stylesheet carrier
a font-family/@font-face      → the unicode-range surface
an @import                    → a stylesheet import
```

## The classic-surface signals — the client-side measure

```text
a per-result iframe           → frames.length — a count oracle
a 200/404 search              → onload/onerror — a hit/miss oracle
a slow-vs-fast path           → timing — a slow/fast oracle
a cached resource             → cache-probe — a cached/uncached
a redirect                    → window.open — a navigation check
a content-size leak           → scrollHeight — a size oracle
a navigation count            → history.length — a count oracle
```

## The exfil signals — the read-back channel

```text
a reachable listener          → the classic exfil
an airgapped bot              → a write-back / a server-state read
a screenshotting bot          → a DOM-writeback read
a comment/note endpoint       → a write-back surface
a DNS-resolvable subdomain    → a DNS exfil
```

## The secret-type signals — the reconstruction

```text
a sorted()/sorted charset     → a sorted secret — the set IS the answer
an unsorted secret            → an n-gram beam search
a fixed-length secret         → a per-position or a count oracle
```

## The signal-to-channel map — which surface names which oracle

```text
signal                             channel
a script-src 'none'                sealed shape → CSS/server-state
a font-src wildcard                @font-face exfil
a style-src unsafe-inline          CSS-selector oracle
a redis LRU                        eviction channel
a counter                          counter channel
a GETDEL                           one-shot-token channel
a rate-limit                       quota channel
a last-seen                        recency channel
a data-secret attribute            CSS-selector oracle
a text-node secret                 @font-face oracle
a /report + a URL + JS runs        classic shape
a managed-policy bot               declarative/server-state only
an airgapped bot                   server-state/write-back
a JSDOM                            DOM/timing/count only
a sorted secret                    char-set → sort → answer
an unsorted secret                 n-gram beam search
a per-result iframe                frames.length
a 200/404 search                   onload/onerror
a slow-vs-fast path                timing
a cached resource                  cache-probe
```

## The class-boundary signals — when it's NOT an XS-leak

```text
a fetch READS bytes              → web-cors (a real read)
a WRITE                          → web-csrf
JS on the target origin          → web-xss
a stored response                → web-cache-poisoning
a JSONP/script-tag serve         → a real read primitive
a postMessage '*' broadcast      → a real read primitive
a `*` ACAO public read           → a CORS question
an opaque response + a channel   → web-xs-leaks (a measure)
```
