# Summary — XS-leaks in one page

The whole class, condensed.

---

## The class in one line

A bot reads under the victim's session — the response is opaque but
a side-channel (frame-count, error, timing, cache, CSS-match,
server-state) leaks a bit or a character-set.

## The two sub-shapes — name yours first

```
CLASSIC — the bot visits YOUR URL → your JS measures a side-channel
SEALED  — a fixed URL + script-blocked CSP → a declarative/server-state
          channel

the deciding question: can ANY origin the bot reaches run one line
of your JS? a 'no' forces the sealed shape.
```

## The channel inventory

```
CLASSIC (client-side):
  frames.length    — a count oracle (one <iframe> per result)
  onload/onerror   — a hit/miss oracle (a 200 vs a 404)
  performance.now  — a timing oracle (a slow vs fast response)
  cache-probe      — a cached-vs-uncached timing
  :visited         — a history read
  window.open      — a navigation check

SEALED (declarative/server-state):
  CSS selector     — an attribute-match → a font/URL load
  @font-face       — a unicode-range → a character-set
  LRU eviction     — the surviving keys are the leak
  counter++        — the next value is the leak
  one-shot token   — the consumed-or-not bit
```

## The CSS oracle — the sealed-shape workhorse

```css
body[secret^="ab"]{--m:url('/leak/ab')}
#trig{background-image:var(--m,none)}
/* the requested URL IS the matched selector */

@font-face{font-family:x;src:url('/leak/61');unicode-range:U+0061}
#secret{font-family:x;display:block !important}
/* the requested font URLs ARE the character-set */
```

## The mandatory control pair

```css
body[secret]{--yes:url('/leak/YES')}
body[nosuchattr]{--no:url('/leak/NO')}
/* YES hits + NO doesn't → the channel works */
/* NO hits → 'no leak' is a broken channel, not a negative */
```

## The feasibility arithmetic — before building

```
- secret's TTL → the whole leak+decode must fit the window
- request rate → thousands of markers need tens-hundreds rps
- bits/visit   → a token=1, a recency=thousands, a CSS=a char-set
- char-set     → a sorted/limited alphabet reduces the search
- the context  → a flag-holder session, not a plain visitor
```

## The reconstruction — assembling the secret

```
a boolean oracle     → a binary-search extend
a char-set (sorted)  → sort the set — the direct answer
an n-gram set        → a beam search over overlaps
a one-bit channel    → N queries for a multi-bit secret
```

## The confusables — the class boundary

```
a fetch READS bytes        → web-cors (a real read, not a measure)
a WRITE                    → web-csrf
a script-tag serve (JSONP) → a real read primitive, not a leak
a broadcast (postMessage *)→ a real read primitive, not a leak
a stored-resp (a cache)    → web-cache-poisoning
the response is OPAQUE     → web-xs-leaks (the side-channel measure)
```

## The falsifier — when it's not an XS-leak

```
a sealed shape with no CSS oracle and no server-state channel —
the oracle surface is dead → a different class.
```

## The confirm — the proof standard

```
a channel that fires is a candidate — the confirm is the
reconstructed + VERIFIED secret (submit it, confirm acceptance,
or a confidence score above a threshold). 'the oracle fired' is
never the confirm — 'the secret leaked and verifies' is.
```
