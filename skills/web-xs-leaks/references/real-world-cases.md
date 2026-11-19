# Real-world cases — where XS-leaks appear in actual challenges

The named shapes with the mechanics that identify them.

---

## The classic shapes — the bot visits YOUR URL

### A bot that opens an attacker URL — the /report shape

```text
a /report endpoint that takes a URL; a puppeteer bot that opens it
in an incognito context carrying the flag-holder's cookie. your
page's JS measures a side-channel — frames.length, onerror, timing.
the flag is in the bot's session — the channel reads under it.
```

### A search that renders a frame per result — the count oracle

```text
a search endpoint that renders one <iframe> per matching result —
frames.length is readable cross-origin. 'how many frames' = 'how
many results' = a count oracle. the classic XS-leak shape.
```

### A search that 404s a miss — the error oracle

```text
a search endpoint that 200s on a hit, 404s on a miss — a
subresource's onload vs onerror is the bit. an <img>/<script>/<link>
load carries the event — a hit/miss oracle.
```

### A slow-vs-fast search — the timing oracle

```text
a search whose response time differs with the result count —
performance.now() on a no-cors fetch measures it. a slow-vs-fast
threshold = a boolean oracle.
```

### A cached-resource timing — the cache-probe

```text
a resource the victim's browser cached — a second load is faster —
'was it cached' = 'was the URL visited' = a history/cache oracle.
```

### A :visited history read — the link-styling oracle

```text
a link to a URL the victim visited styles :visited differently —
a 404 URL never enters history — 'is it styled visited' = 'was it
visited' = a history oracle.
```

## The sealed shapes — no attacker JS

### A CSP script-blocked target — the forced sealed shape

```text
'script-src none' — the bot can't run your JS — the ONLY channel
is a declarative one (a CSS selector → a font/URL load) or a
server-side mutation the GET caused.
```

### A CSS-selector oracle — the attribute-match channel

```text
a reflected secret in an attribute (data-secret, value, etc.) —
a CSS attribute-selector matches it — a matching rule loads a
font/URL — the requested URL IS the match.
```

### A unicode-range @font-face — the char-set channel

```text
a font-src wildcard ('self' *) allows an external font — one
@font-face per alphabet char, each with a unicode-range + a distinct
URL — the browser downloads a face only when a char in its range
renders — the requested URLs ARE the character-set.
```

### An LRU-eviction store — the recency channel

```text
a redis with --maxmemory-policy allkeys-lru — a GET that touches a
key refreshes it — flood the store → the survivors are the bot's
GETs — a thousand-bit-per-visit channel.
```

### A counter/state endpoint — the read-back channel

```text
a GET that increments a counter you can read — 'the counter is N+1
after the bot's visit' → the bot's GET ran → the candidate matched.
```

### A one-shot token — the single-use flag

```text
a GETDEL/single-use nonce — 'did the token survive the bot's visit'
is one bit and burns the check — spend it LAST.
```

## The hybrid shapes — the mixed case

### A CSS oracle + a same-origin privileged request — the verified card

```text
the HTB Stylish shape — a unicode-range leak recovers a token's
char-set; a second stylesheet's @font-face src is the SAME-ORIGIN
privileged URL — the bot's font load is the privileged GET that no
external client could fire. the channel that read the token becomes
the channel that spends it.
```

### A server-state channel + a sorted secret — the direct answer

```text
a sorted secret's char-set fully determines it — a char-set oracle
returns the answer directly — no ordering work needed.
```

## The delivery variants — the bot's path

```text
a /report that takes a URL     → the classic shape (if JS runs)
a managed-policy bot           → a forced sealed shape
a stored page                  → a same-origin case
a data: URL                    → an airgapped/null-origin case
a fixed-URL bot                → the sealed shape
```

## The confusable cases — the boundary

```text
a JSONP endpoint            → a real read primitive, not a leak
a postMessage broadcast     → a real read primitive, not a leak
a CORS * ACAO               → a real read, not a measure
a stored response           → a cache-poison, not a leak
a fetch that READS bytes    → web-cors
a WRITE                     → web-csrf
```

## The per-case channel-selection

```text
a bot that visits your URL + a frame-count  → frames.length
a bot that visits your URL + a 200/404      → onload/onerror
a bot that visits your URL + a slow-vs-fast → timing
a script-blocked CSP + a style hole         → CSS-selector oracle
a script-blocked CSP + a font wildcard      → @font-face oracle
a script-blocked CSP + a redis LRU          → the eviction channel
a script-blocked CSP + a counter            → the counter channel
a script-blocked CSP + a one-shot token     → the single-use flag
```
