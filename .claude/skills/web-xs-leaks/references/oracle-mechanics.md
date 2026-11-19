# Oracle mechanics — how each channel actually works

The browser-side mechanism behind every XS-leak oracle.

---

## 1. The frames.length mechanism — a DOM property

```text
window.frames is a DOM collection of the window's sub-frames — its
.length is the count. the SOP gates the frame's CONTENT, not the
parent's view of how many children it has — 'how many <iframe>' is
readable; 'what's inside them' isn't. a per-result iframe count is
a count oracle — 'how many frames' = 'how many results'.
```

## 2. The onload/onerror mechanism — a load event

```text
a subresource load fires load on success, error on failure — the
EVENT is a browser-side signal, not a response read. the SOP gates
the response body, not the load's outcome — 'did it load' is
readable; 'what it returned' isn't. a 200-vs-404 difference is the
hit/miss oracle.
```

## 3. The timing mechanism — a measurable clock

```text
performance.now() is a high-resolution clock — a no-cors fetch's
COMPLETION is a measurable event (a promise resolves, a load fires)
— 'how long' is readable even when 'what' isn't. a slow query vs a
fast rejection — the timing threshold is the bit.
```

## 4. The cache-probe mechanism — a partitioned cache

```text
a cached resource loads faster — the second load's timing differs —
'was it cached' = 'was the URL visited'. the cache is partitioned
per top-frame site — a resource cached on site A isn't shared with
site B — the probe reads 'was it cached on THIS site' — a same-site
or a same-partition read.
```

## 5. The :visited mechanism — a render-side-channel

```text
a computed-style query returns the UNVISITED style (a privacy
partition) — but the RENDERING cost differs: a :visited link
repaints; an unvisited one doesn't. the channel is a render-side-
channel (a repaint cost, a font-load trigger on a :visited selector)
— not a computed-style read.
```

## 6. The CSS-selector mechanism — the style engine

```text
a CSS attribute-selector is a DECLARATIVE match — the browser's
style engine evaluates it on every render — no JS needed. a matching
rule sets a custom property; an element consuming thousands of them
as background layers fetches exactly the matched URLs — the
requested URLs ARE the match. the style engine IS the oracle.
```

## 7. The @font-face mechanism — the font-matching engine

```text
a font-face's unicode-range declares which chars it covers — the
browser's font-matching engine downloads the face ONLY when a char
inside the range actually renders. one @font-face per alphabet char
+ a shared family + the secret's element = the requested font URLs
ARE the character-set of the rendered text — the font engine IS
the oracle.
```

## 8. The multi-layer background mechanism — the parallel fetch

```text
a multi-layer background-image references each var() — an unmatched
property resolves to 'none' (no fetch); a matched one to a url()
(a fetch) — the browser fetches exactly the matched URLs — the
requested URLs ARE the matched selectors. a thousand rules = a
thousand parallel fetches.
```

## 9. The LRU mechanism — the recency map

```text
a redis --maxmemory-policy allkeys-lru — a GET that touches a key
refreshes it (marks it recently-used) — flood the store to force
eviction → the surviving keys are the recently-touched ones — the
bot's GETs — the SURVIVOR SET is the leak. a store with K keys
carries K bits per visit.
```

## 10. The counter mechanism — a readable mutation

```text
a GET that increments a readable counter — 'the counter is N+1
after the bot's visit' → the bot's GET ran → the candidate matched.
the counter's value IS the leak — a server-state read, not a
browser-side measure.
```

## 11. The one-shot-token mechanism — a consumed state

```text
a GETDEL/single-use nonce — 'did the token survive the bot's visit'
is one bit — a spent token is gone — the consumed-or-not IS the
leak — a server-state read.
```

## 12. The meta-refresh mechanism — a same-site navigation

```text
a meta-refresh issued BY THE TARGET is a same-site navigation — the
browser treats it as a top-level navigation on the same site — the
Lax cookie rides. the sealed shape's whole design exploits this —
the bot's privileged request is a same-site navigation the target
itself issues.
```

## 13. The window.open mechanism — a navigation check

```text
did the navigation happen — a redirect check — a page that redirects
on a hit vs stays on a miss — the window's state (open, closed,
navigated) is the bit — a browser-side measure.
```

## 14. The scrollHeight mechanism — a content-size leak

```text
the page's content height differs with the result count — a
content-length leak — the iframe's scrollHeight is readable on a
same-origin or a same-document case — a size oracle.
```

## 15. The resource-timing mechanism — a load-duration read

```text
the PerformanceResourceTiming API records a subresource's load
duration — a 'was it loaded' + 'how long' read — a cache oracle —
the API's entries are the leak.
```

## 16. The history.length mechanism — a navigation count

```text
window.history.length is readable cross-origin — 'how many entries'
= 'how many navigations happened' — a count oracle — the history
stack's length IS the leak.
```
