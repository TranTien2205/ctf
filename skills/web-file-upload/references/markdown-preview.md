# Markdown / Rst / Textile Upload — the rendered-document XSS path

## The shape — a markup file that gets rendered to HTML

Upload `.md`, `.rst`, `.textile`, `.adoc`, `.org` — a preview or docs
feature renders it. The rendered HTML inherits the app's origin — the
same stored-XSS story as `html-upload.md`, through a markup parser
instead of a raw HTML file.

## What survives through a markdown renderer

```markdown
[click](javascript:alert(1))
<img src=x onerror=alert(1)>        <!-- raw HTML passthrough -->
<a href="javascript:...">           <!-- attribute injection -->
![img](x" onerror="alert(1))        <!-- broken-out attribute -->
<script>alert(1)</script>            <!-- raw tags if passthrough -->
```

Most renderers allow raw HTML inline (`markdown` python lib, marked,
remark without sanitize, pandoc) — a raw `<script>` survives; a
`sanitize`-mode strips it.

## The `javascript:` URL — the scheme check

`[x](javascript:...)` — renderers differ:

- `marked`/`remark` without sanitize → emits `href="javascript:..."` — clickable XSS
- `markdown-it` default → renders `href` as-is? — no, markdown-it passes
  it through; the LINK VALIDATION is a plugin (`validateLink`)
- `kramdown`/RDiscount → sometimes filters `javascript:` scheme
- python `markdown` → passes raw HTML, and link hrefs verbatim

Probe:

```markdown
[p](javascript:ALERT_MARK) and <a href="javascript:ALERT_MARK2">q</a>
```

Check the rendered HTML for `javascript:` surviving in an `href`.

## Rst/sphinx — the raw directive

```rst
.. raw:: html

   <script>alert(1)</script>
```

`.. raw:: html` emits the block verbatim — enabled unless `raw_enabled =
False` in the docutils config — common in self-hosted docs.

## AsciiDoc — `++++` passthrough blocks and `link:` macros

```asciidoc
++++
<script>alert(1)</script>
++++

link:javascript:alert(1)[click]
```

## The file-content vs file-serve distinction

The payload lives in the FILE; the exploit needs the RENDER step:

- upload → fetch → server returns `text/plain`/`text/markdown` → dead
- upload → fetch → server renders to html in-page → alive, same-origin XSS
- upload → "preview" endpoint converts → alive if preview serves html

The fetch's `Content-Type` is the check — `text/html` means rendered;
`text/markdown`/`text/plain` means source.

## The "the render sanitizes" tier — what survives each sanitizer

- `bleach`/`DOMPurify` → strips scripts, most attributes — `web-xss`'s
  sanitizer-bypass corpus
- `markdown` + `safe_mode` → escapes HTML — dead for raw tags; `javascript:`
  links sometimes still pass
- `remark`+`rehype-sanitize` → strict allowlist — bypass via allowed-tag
  quirks (iframe srcdoc, svg, mathml) — `skills/web-xss/references/mutation-xss.md`

## The blind-spot — math/emoji/toc extensions

Extensions that eval template-like content (`{{ }}`, katex expressions,
emoji shortcodes) — a template-injection primitive inside markdown —
`web-ssti` if the doc reaches a template render.

## Falsifiers

- file serves as `text/markdown`/`text/plain`, never rendered
- render sanitizes all tags AND `javascript:` scheme AND raw directives
  are disabled

## Output to record

- the rendered-HTML location + the verbatim markup that survived unescaped
