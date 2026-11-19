# Extended deep — the XS-leak mechanics, exhaustively

The complete mechanics of every channel — the why behind each oracle.

---

## 1. Why frames.length is readable cross-origin

```text
the window.frames API exposes the COUNT of sub-frames — a property
of the window object, not the frame's content. the SOP gates the
frame's DOM, not the parent's view of how many children it has —
'how many <iframe>' is readable; 'what's inside them' isn't. the
count is the oracle.
```

## 2. Why onload/onerror fire cross-origin

```text
a subresource load (an <img>, a <script>, a <link>) fires load on
success and error on failure — the EVENT is a browser-side signal,
not a response read. the SOP gates the response body, not the load's
outcome — 'did it load' is readable; 'what it returned' isn't.
```

## 3. Why timing leaks — the clock's reach

```text
performance.now() is a high-resolution clock readable by any
script — a no-cors fetch's COMPLETION is a measurable event (a
promise resolves, a load fires) — 'how long' is readable even when
'what' isn't. the timing is the oracle.
```

## 4. Why a cache-probe leaks — the partition's reach

```text
a cached resource loads faster — the second load's timing differs —
'was it cached' = 'was the URL visited'. the cache is partitioned
per top-frame site — a resource cached on site A isn't shared with
site B — the probe reads 'was it cached on THIS site' — a same-site
or a same-partition read.
```

## 5. Why :visited leaks — the render-side-channel

```text
a computed-style query returns the UNVISITED style (a privacy
partition) — but the RENDERING cost differs: a :visited link
repaints; an unvisited one doesn't. the channel is a render-side-
channel (a repaint cost, a font-load trigger on a :visited selector)
— not a computed-style read.
```

## 6. Why a CSS-selector oracle is declarative — the style engine

```text
a CSS attribute-selector is a DECLARATIVE match — the browser's
style engine evaluates it on every render — no JS needed. a
matching rule sets a custom property; an element consuming
thousands of them as background layers fetches exactly the matched
URLs — the requested URLs ARE the match. the style engine IS the
oracle.
```

## 7. Why @font-face reads the rendered text — the font-matching engine

```text
a font-face's unicode-range declares which chars it covers — the
browser's font-matching engine downloads the face ONLY when a char
inside the range actually renders. one @font-face per alphabet char
+ a shared family + the secret's element = the requested font URLs
ARE the character-set of the rendered text — the font engine IS
the oracle.
```

## 8. Why the multi-layer background fetches the matched URLs

```text
a multi-layer background-image references each var() — an unmatched
property resolves to 'none' (no fetch); a matched one to a url()
(a fetch) — the browser fetches exactly the matched URLs — the
requested URLs ARE the matched selectors. a thousand rules = a
thousand parallel fetches.
```

## 9. Why a sorted secret's set IS the answer — the ordering

```text
'take N random chars, sort them' — the ordering is KNOWN (sorted) —
the character-set fully determines the string. sort the leaked set
→ the token. the set IS the answer — no ordering work needed.
```

## 10. Why an unsorted secret needs a beam search — the ordering

```text
an unsorted secret's char-set doesn't order it — a set of n-grams
(each a substring the channel confirmed) stitches into the secret
— a beam search keeps the top-W candidates at each extension — a
noise-aware reconstruction.
```

## 11. Why the LRU channel is high-bandwidth — the survivor set

```text
a redis --maxmemory-policy allkeys-lru — a GET that touches a key
refreshes it (marks it recently-used) — flood the store to force
eviction → the surviving keys are the recently-touched ones — the
bot's GETs — the SURVIVOR SET is the leak. a store with K keys
carries K bits per visit — a thousand-bit channel.
```

## 12. Why the meta-refresh bypasses SameSite — the same-site navigation

```text
a meta-refresh issued BY THE TARGET is a same-site navigation — the
browser treats it as a top-level navigation on the same site — the
Lax cookie rides. the sealed shape's whole design exploits this —
the bot's privileged request is a same-site navigation the target
itself issues.
```

## 13. Why the sealed shape needs no JS — the declarative/server-state

```text
a script-blocked CSP removes attacker JS — the ONLY channels are:
- a DECLARATIVE channel (a CSS selector → a font/URL load — the
  style engine does the work, not JS)
- a SERVER-STATE channel (a mutation the GET caused — a counter, a
  recency, a token — read back later)
the deciding question: can ANY origin the bot reaches run one line
of your JS? a 'no' forces the sealed shape.
```

## 14. Why the control pair is mandatory — the noise

```text
a side-channel is NOISY — a failed run and a negative answer look
identical:
- the selector doesn't match (a broken channel)
- the secret doesn't match (a true negative)
the always-true control proves the channel works; the never-true
control proves the measurement isn't ambient noise. without both,
a 'no signal' is uninterpretable — 'no leak' vs 'broken channel' is
undecidable.
```

## 15. Why the one-shot token spends last — the burned check

```text
a GETDEL's 'did it survive' is one bit AND burns the check — a spent
token is gone. the cheaper channels (a counter, a recency, a CSS
oracle) narrow the answer first — the one-shot's one bit is spent
on the LAST narrowing, not the first.
```

## 16. Why the feasibility arithmetic matters — the bound

```text
a secret of N bits needs a channel carrying ≥N bits total:
- a one-bit channel × M visits = M bits — the visit count matters
- a char-set channel × 1 visit = the whole set — a single visit
- a recency channel × 1 visit = thousands of bits — a single visit
the channel's bandwidth × the visit count × the rate cap × the TTL
= the feasibility bound — a low-bandwidth channel × a rate cap × a
short TTL is an infeasible leak.
```
