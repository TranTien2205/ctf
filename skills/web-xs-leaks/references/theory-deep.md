# Theory deep — the information-theoretic and browser-architecture basis

Why each XS-leak channel exists and why it carries the bandwidth it does.

---

## 1. The SOP side-channel — the response is opaque, its shape isn't

```text
the same-origin policy gates the RESPONSE BODY — the bytes. it
doesn't gate:
- how many <iframe> a page renders (frames.length is readable)
- whether a subresource load errors (onload/onerror fire)
- how long a load takes (performance timing)
- whether a URL is in history (:visited styling)
- whether a resource is cached (a cache-probe timing)
each is a 1-bit-or-more leak per load — the browser's BEHAVIOR is
the oracle, not the response's content.
```

## 2. The information-theoretic bound — bits per visit

```text
each observable carries log2(possible-states) bits:
- a boolean (hit/miss)         = 1 bit
- a count (0..N)               = log2(N) bits
- a char-set (subset of 62)    = a character-SET (the whole set at once)
- a recency channel            = thousands of bits (which keys survive)
the channel's bandwidth = bits-per-visit × visits — the feasibility
arithmetic for the whole secret.
```

## 3. Why a CSS selector reads an attribute — the declarative match

```text
a CSS attribute-selector (body[secret^="ab"]) is a DECLARATIVE
match — no JS needed — the browser's style engine evaluates it on
every render. a matching rule sets a custom property; an element
consuming thousands of them as background layers fetches exactly
the matched URLs — the requested URLs ARE the match. the channel's
bandwidth is the number of parallel rules — thousands of selectors
= thousands of URLs = a char-set or a whole secret.
```

## 4. Why @font-face leaks a char-set — the on-demand font

```text
a font-face's unicode-range declares which chars it covers — the
browser's font-matching engine downloads the face ONLY when a char
inside the range actually renders. one @font-face per alphabet char
+ a shared family + the secret's element = the requested font URLs
ARE the character-set of the rendered text. the bandwidth is the
whole set in ONE load — no sequential queries.
```

## 5. Why a sorted secret is cheap — the set IS the answer

```text
a secret built by 'take N random chars, sort them' is fully
determined by its character SET — the ordering is known (sorted).
a char-set oracle returns the answer directly — no ordering work
needed. an UNSORTED secret's set doesn't order it — an n-gram/beam
reconstruction is required.
```

## 6. Why the LRU channel is high-bandwidth — the recency map

```text
a redis --maxmemory-policy allkeys-lru — a GET that touches a key
refreshes it (marks it recently-used). flood the store to force
eviction → the surviving keys are the recently-touched ones — the
bot's GETs — the SURVIVOR SET is the leak. a store with K keys
carries K bits per visit — a thousand-bit channel.
```

## 7. Why the control pair is mandatory — the noise problem

```text
a side-channel is NOISY — a failed run and a negative answer look
identical:
- the selector doesn't match (a broken channel)
- the secret doesn't match (a true negative)
the always-true control proves the channel works; the never-true
control proves the measurement isn't ambient noise. without both,
a 'no signal' is uninterpretable — you can't tell 'no leak' from
'broken channel'.
```

## 8. Why SameSite doesn't save a sealed design — the same-site case

```text
SameSite=Lax/Strict gates CROSS-SITE requests — a cross-site fetch
doesn't carry the cookie. but a bot's request to the target ITSELF
is same-SITE — the cookie rides. a sealed design where the bot only
ever visits the target is unaffected by SameSite — the cookie
always rides. the cross-site cookie question only matters in the
CLASSIC shape.
```

## 9. Why the meta-refresh bypasses the Lax gate — a same-site navigation

```text
a meta-refresh issued BY THE TARGET is a same-site navigation — the
browser treats it as a top-level navigation on the same site — the
Lax cookie rides. the sealed shape's whole design exploits this —
the bot's privileged request is a same-site navigation the target
itself issues.
```

## 10. Why the :visited channel is a render side-channel — the partition

```text
modern browsers partition :visited per top-frame site — a computed-
style query can't read it — but the RENDERING cost differs: a
:visited link repaints; an unvisited one doesn't. the channel is a
render-side-channel (a repaint cost, a font-load trigger), not a
computed-style read.
```

## 11. Why the sealed shape exists — the no-JS constraint

```text
the sealed shape exists because a script-blocked CSP or a managed
policy removes attacker JS — the ONLY channels are:
- a DECLARATIVE channel (a CSS selector → a font/URL load — the
  style engine does the work, not JS)
- a SERVER-STATE channel (a mutation the GET caused — a counter,
  a recency, a token — read back later)
the deciding question: can ANY origin the bot reaches run one line
of your JS? a 'no' forces the sealed shape.
```

## 12. Why the response's shape is the leak — the observable taxonomy

```text
the leak isn't 'what the response says' — it's 'how the browser
behaved loading it':
- a page that renders one frame per result → frames.length
- a search that 404s on a miss → onload/onerror
- a slow-vs-fast query → performance.now()
- a reflected attribute → a CSS selector match
- a server-state mutation → a counter/recency/token read
each is a different observable of the same opaque response — the
shape, not the bytes, is the leak.
```

## 13. Why the one-shot token spends last — the burned check

```text
a GETDEL/single-use token's 'did it survive' is one bit AND burns
the check — a spent token is gone. the cheaper channels (a counter,
a recency, a CSS oracle) narrow the answer first — the one-shot
token's one bit is spent on the last narrowing, not the first.
```

## 14. Why the channel's bandwidth matters — the feasibility bound

```text
a secret of N bits needs a channel carrying ≥N bits total:
- a one-bit channel × M visits = M bits — the visit count matters
- a char-set channel × 1 visit = the whole set — a single visit
- a recency channel × 1 visit = thousands of bits — a single visit
the channel's bandwidth × the visit count × the rate cap = the
feasibility bound — a low-bandwidth channel × a rate cap × a TTL
is an infeasible leak.
```
