# CTF shapes — the XS-leak designs that appear in challenges

The named challenge patterns, with the mechanics that identify them.

---

## The "search and count" shape — the frames.length oracle

```text
a search endpoint that renders one <iframe> per matching result —
frames.length is readable cross-origin — 'how many frames' = a count
oracle. the secret is the search's domain — a prefix search leaks it
one char at a time.
```

## The "hit or miss" shape — the status oracle

```text
a search that 200s on a hit, 404s on a miss — an <img>/<script>/<link>
onload vs onerror is the bit. a prefix search leaks the secret one
char at a time through the boolean oracle.
```

## The "slow or fast" shape — the timing oracle

```text
a search whose response time differs with the result — a no-cors
fetch's timing measures it — a slow-vs-fast threshold is the bit.
```

## The "cached or not" shape — the cache-probe oracle

```text
a resource the victim's browser cached — a second load is faster —
'was it cached' = 'was the URL visited' — a history/cache oracle.
```

## The "visited or not" shape — the history oracle

```text
a link to a visited URL styles :visited differently — a 404 URL
never enters history — 'is it styled visited' = 'was it visited'.
```

## The "CSS match" shape — the attribute-selector oracle

```text
a reflected secret in an attribute — a CSS attribute-selector
matches it — a matching rule loads a font/URL — the requested URL
IS the match. a sealed shape's workhorse.
```

## The "font load" shape — the unicode-range oracle

```text
a font-src wildcard — one @font-face per alphabet char, each a
unicode-range + a distinct URL — the browser downloads a face only
when a char in its range renders — the requested URLs ARE the set.
the HTB Stylish shape.
```

## The "store recency" shape — the LRU-eviction channel

```text
a redis LRU store — a GET that touches a key refreshes it — flood
the store → the survivors are the bot's GETs — a thousand-bit
channel. the blast_radius: the flood destroys other keys.
```

## The "counter" shape — the read-back channel

```text
a GET that increments a counter you can read — 'the counter is N+1'
→ the bot's GET ran → the candidate matched.
```

## The "one-shot" shape — the single-use token

```text
a GETDEL/single-use nonce — 'did it survive' is one bit and burns
the check — spend it LAST.
```

## The "rate-limit" shape — the quota channel

```text
a bucket with a remaining count — a consumed quota = 'the GET ran'.
```

## The "meta-refresh" shape — a same-site navigation

```text
a meta-refresh issued BY THE TARGET is a same-site navigation —
it carries the Lax cookie a cross-site fetch wouldn't — the sealed
shape's whole design avoids the cross-site cookie question.
```

## The "same-origin CSS + privileged URL" shape — the verified card

```text
a unicode-range leak recovers a token's char-set; a second
stylesheet's @font-face src is the SAME-ORIGIN privileged URL —
the bot's font load is the privileged GET. the channel that read
the token becomes the channel that spends it.
```

## The "managed-policy" shape — a forced sealed case

```text
URLBlocklist ['*'] + URLAllowlist — the bot can ONLY visit the
target's origin — a declarative/server-state channel is the only
one that works.
```

## The "airgapped bot" shape — a server-state exfil

```text
a bot that can't reach attacker.com — a server-state channel
(counter/recency/token), a write-back, or a DOM-writeback — not an
external exfil.
```

## The "data: URL" shape — a null-origin case

```text
a bot that opens a data: URL — an opaque/null origin — the channel
is a same-origin leak or a server-state read.
```

## The "stored page" shape — a same-origin leak

```text
a stored page on the target's origin — a same-origin CSS/JS channel
— the Lax cookie rides.
```

## The per-shape channel-selection

```text
a bot + a URL-submit + JS runs          → frames/onload/timing
a bot + a URL-submit + JS blocked       → CSS-selector oracle
a bot + a fixed URL + a font wildcard   → @font-face oracle
a bot + a redis LRU                     → the eviction channel
a bot + a counter/quota                 → the counter channel
a bot + a one-shot token                → the single-use flag
a managed-policy bot                    → a declarative channel only
an airgapped bot                        → a server-state/write-back
a same-origin stored page               → a same-origin channel
```
