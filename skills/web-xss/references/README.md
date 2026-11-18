# web-xss references — navigation

The corpus — pick by what the injection point looks like, not by
where you want to end up. `../SKILL.md` is the entry contract;
these files carry the payload-level depth.

## Start here — detection and context

| File | When to open |
|---|---|
| `workflow.md` | the end-to-end procedure: probe → context → payload → proof |
| `detection.md` | you don't yet know WHERE the value lands — marker protocol + context probes |
| `contexts.md` | the reflection is visible but the context is unclear — five-context map |
| `dom-xss.md` | the value never reaches the response — JS-side source→sink flows |
| `source-sink-table.md` | the complete DOM source × sink pair table |
| `dangerous-apis.md` | every DOM API that turns data into code/markup — audit grep list |
| `postmessage.md` | a `message` listener takes your input — origin-check bypasses |

## Per-context payload sets

| File | Context |
|---|---|
| `html-context.md` | value lands between tags — full tag space |
| `attribute-context.md` | value inside `attr="..."` — quote escapes + URL schemes |
| `js-context.md` | value inside `<script>` — string/comment/template escapes |
| `protocols.md` | `javascript:`/`data:`/`vbscript:` scheme vectors |
| `svg-deep.md` | SVG-context vectors — beyond `onload` |
| `markdown-render.md` | markdown/wiki renderers — link-scheme + raw-html |
| `reflected-xss.md` | param→response reflections incl. headers/path carriers |
| `headers-xss.md` | UA/Referer/Cookie/Host headers as carriers |

## The defense-side files

| File | Content |
|---|---|
| `filter-bypass.md` | string/tag/quote/paren/space filters — bypass taxonomy |
| `encodings.md` | entity/percent/unicode/hex encoding variants |
| `unicode-deep.md` | normalization, confusables, overlong UTF-8 |
| `charset-tricks.md` | UTF-7/UTF-16/charset-declaration (legacy layer, honest limits) |
| `mutation-xss.md` | mXSS — sanitizer reparse bugs, namespace confusion |
| `csp.md` | the policy read + per-directive bypass shapes |
| `waf-specific.md` | ModSecurity/Cloudflare/AWS/Akamai per-vendor quirks |
| `gadgets.md` | DOM clobbering + sanitizer CVEs + Angular escapes + Function-chain |
| `dom-clobbering.md` | deep clobbering reference — id/name globals, toString tricks |

## The payload corpus

| File | Content |
|---|---|
| `payload-dictionary.md` | the big categorized payload index — 20+ sections |
| `events.md` | every `on*` handler — autofire vs interaction, full reference |
| `polyglots.md` | multi-context payloads + construction method |
| `cheatsheet.md` | the quick-reference tables — context→payload |

## Delivery, exfil and escalation

| File | Content |
|---|---|
| `stored-xss.md` | plant→trigger→collect — stored-field inventory |
| `blind-xss.md` | blind-XSS — marker channels, no-render feedback |
| `second-order-dom.md` | localStorage/cookie/name carriers, deferred sinks |
| `upload-xss.md` | .svg/.html uploads + filename-as-vector |
| `exfil-methods.md` | exfil channel matrix — CSP-gated selection |
| `css-exfil.md` | no-JS exfil via attribute selectors + beacons |
| `bot-chains.md` | admin-bot workflows — flag-location cases |
| `self-xss-to-real.md` | self→real escalation bridges (honest limits) |
| `framework-sinks.md` | Angular/Vue/React/jQuery/framework sinks |
| `devtools-workflow.md` | local-browser test loop before spending bot cycles |

## Reading order

```text
don't know context      → detection.md → contexts.md
context known           → the context's file → payload-dictionary.md
filter blocks           → filter-bypass.md → encodings.md / mutation-xss.md
CSP present             → csp.md → gadgets.md
WAF present             → waf-specific.md
framework seen          → framework-sinks.md
stored field            → stored-xss.md → bot-chains.md
no render visible        → blind-xss.md → exfil-methods.md
can't pick a context    → polyglots.md → cheatsheet.md
JS-side sink            → dom-xss.md → source-sink-table.md
```

Every payload here is a candidate — confirm against the marker in
the RAW response plus actual execution before calling it a hit.
Reflection alone is inconclusive.
