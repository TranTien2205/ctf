# Browser behavior — the per-browser XS-leak surface

Each browser's side-channel behavior — what leaks and what doesn't.

---

## 1. Chromium (Chrome/Edge) — the dominant CTF bot

```text
- frames.length            — readable cross-origin — a count oracle
- onload/onerror           — fire on subresource loads — a hit/miss
- :visited                 — partitioned since Chrome 105 — a
                             rendering side-channel (a repaint cost),
                             not a computed-style query
- performance.now()        — a coarse-but-readable timing
- a cache-probe            — a partitioned cache — a same-site read
- a font-face unicode-range— downloads only on a range hit
- a managed policy         — URLBlocklist/URLAllowlist — a forced
                             sealed shape
- a SameSite=Lax default   — a cross-site fetch doesn't carry the
                             cookie; a same-site navigation does
```

## 2. Firefox — the occasional bot

```text
- frames.length            — readable cross-origin
- onload/onerror           — fire on subresource loads
- :visited                 — a rendering side-channel
- a cache                  — a partitioned cache
- a font-face unicode-range— downloads on a range hit
- a SameSite=Lax default   — a cross-site fetch doesn't carry the
                             cookie
```

## 3. WebKit/Safari — a rare CTF bot

```text
- a stricter ITP           — a more aggressive cookie restriction
- a SameSite=Lax default   — a cross-site fetch doesn't carry the
                             cookie
- a partitioned cache      — a same-site read
```

## 4. JSDOM — the no-render bot

```text
- NO rendering engine      — no CSS, no fonts, no :visited — the
                             visual/CSS channels are dead
- a frames.length          — the DOM count is still readable
- a performance.now()      — a timing channel survives
- the deciding question    — is the bot a REAL browser or a JSDOM
```

## 5. The headless-vs-headed question — the bot's render surface

```text
- a headless browser       — still renders — the CSS/font channels
                             work
- a JSDOM                  — no render — the CSS/font channels dead
- a screenshotting bot     — a DOM-writeback is the read-back
```

## 6. The SameSite default — the cookie's reach

```text
a SameSite=Lax cookie      — a cross-site fetch doesn't carry it;
                             a same-site navigation does
a SameSite=Strict cookie   — a same-site navigation doesn't carry
                             it on a first-party-only case
a SameSite=None + Secure   — a cross-site fetch carries it — a
                             credentialed read
a meta-refresh             — a same-site navigation — bypasses the
                             Lax gate
```

## 7. The :visited partition — the history read's limit

```text
modern Chrome partitions :visited per top-frame site — a link to a
URL the victim visited on ANOTHER site doesn't style visited — the
history read is a same-site or a rendering-side-channel only.
```

## 8. The cache partition — the cache-probe's limit

```text
a partitioned cache (per top-frame site) — a resource cached on
site A isn't shared with site B — the cache-probe is a same-site
read, not a cross-site one.
```

## 9. The managed-policy bot — the forced sealed shape

```text
Chrome managed policy — URLBlocklist ['*'] + URLAllowlist — the bot
can ONLY visit the target's origin — a declarative/server-state
channel is the only one that works.
```

## 10. The COOP/COEP surface — a cross-origin-opener-policy gate

```text
a COOP same-origin window — window.open returns a cross-origin-
isolated handle — a navigation check is still readable.
a COEP require-corp page — a cross-origin subresource needs a CORP
header — an unmarked resource fails — an onload/onerror oracle.
```

## The per-browser oracle-availability

```text
oracle               Chrome    Firefox   Safari   JSDOM
frames.length        yes       yes       yes      yes
onload/onerror       yes       yes       yes      yes
timing               yes       yes       yes      yes
cache-probe          same-site same-site same-site no
:visited             render    render    render   no
CSS-selector         yes       yes       yes      no
@font-face           yes       yes       yes      no
scrollHeight         yes       yes       yes      no
history.length       yes       yes       yes      yes
```

## The render-vs-DOM split — the bot's channel surface

```text
a REAL browser (Chrome/Firefox/Safari) — the CSS/font/render
channels work
a JSDOM — only the DOM/timing/count channels survive — no CSS, no
fonts, no :visited
the deciding question: does the bot render?
```
