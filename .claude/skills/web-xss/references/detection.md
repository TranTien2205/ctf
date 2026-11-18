# XSS detection — find the context before the payload

XSS is not "does the payload run" — it is "WHERE does the value
land in the document, and what does the parser do to it there".
The entire detection phase is answering that one question. A
payload that works in HTML body does nothing inside a script
string; the context IS the vulnerability.

---

## 1. The marker — what a canary must measure

A marker must be: unique (grep-able), harmless (renders), and
context-tagged (its shape tells you where it landed).

```text
XSS_PROBE_8f3a                -- the base marker
XSS<PROBE>"8f3a'>`            -- metachar canary (each char probed)
xss"probe'<8f3a>              -- variant ordering
```

`tools/web/xss_context.py --url U --param P` sends the metachar
canary and classifies survival per character:

```text
"  -> &quot;    (attribute-quoted context)
'  -> &#39;     (single-quoted attr or entity-encoding)
<  -> &lt;      (html-escaped → body text, not markup)
>  -> &gt;      (same)
`  -> `         (verbatim → template-literal context?)
&  -> &amp;     (html-escaped)
=  -> =         (verbatim)
```

The survival report IS the context map:

| Survived | Encoded | Context |
|---|---|---|
| `"` `'` | — | attribute values likely open |
| `<` `>` | — | markup context — tag injection possible |
| all | — | raw sink or DOM |
| — | `<` `>` `&` | HTML-escaped → body text only |
| — | `"` | double-quoted attr |
| — | `'` | single-quoted attr |
| none | none | value never rendered → stored/deferred or dead |

---

## 2. Where markers land — the context taxonomy

```text
HTML body        <div>XSS_PROBE</div>                  → markup injection
HTML text-esc    <div>XSS&lt;PROBE</div>               → dead for markup;
                                                       try other context
attribute        <div title="XSS_PROBE">               → attr breakout
attr-unquoted    <div title=XSS_PROBE>                 → space breaks it
attr-single      <div title='XSS_PROBE'>               → ' breakout
script-string    <script>var x="XSS_PROBE";</script>   → string break
script-block     <script>// XSS_PROBE</script>          → comment/statement
template-lit     <script>var t=`${XSS_PROBE}`;</script> → `${}` eval
script-raw       <script>var x=XSS_PROBE;</script>      → expression context
JSON-in-script   <script>var d={"k":"XSS_PROBE"};</script>
                                                        → JSON string break
URL attribute    <a href="XSS_PROBE">                  → scheme injection
srcset/src       <img src="XSS_PROBE">                 → URL + load/error
style attr       <div style="color:XSS_PROBE">         → CSS context
css block        <style>body{color:XSS_PROBE}</style>   → CSS context
textarea         <textarea>XSS_PROBE</textarea>         → RCDATA escape
title            <title>XSS_PROBE</title>               → RCDATA
iframe srcdoc    <iframe srcdoc="XSS_PROBE">            → nested doc
svg/math         <svg><desc>XSS_PROBE</desc></svg>      → XML-in-HTML
comment          <!-- XSS_PROBE -->                     → comment escape
noscript         <noscript>XSS_PROBE</noscript>         → noscript context
doctype          <!DOCTYPE XSS_PROBE>                   → rare
HTTP header      X-Header: XSS_PROBE → rendered in error → header→body
```

---

## 3. The probe sequence — five sends that map the landing

```text
1. XSS_PROBE_8f3a                      -- is it rendered at all?
2. XSS<PROBE>"'>`8f3a                  -- which metachars survive?
3. XSS_PROBE_8f3a<script>alert(1)</script>    -- markup eval?
   (only after 2 shows < and > survive)
4. "</XSS_PROBE_8f3a>" + attr probes   -- quote breakout shapes
5. ${XSS_PROBE_8f3a}                   -- template-literal context?
```

Read the RENDERED DOM, not just the response body — a value in a
`<script>` var only reveals its context after parse. In a browser:
view-source for the raw, devtools for the DOM.

---

## 4. Reflection vs stored vs DOM — three different oracles

| Type | Probe | Signal |
|---|---|---|
| reflected | marker in request → marker in response | immediate |
| stored | marker written → marker in LATER response | poll the read page |
| DOM | marker in URL fragment/source → marker in sink after JS runs | needs a browser; the raw HTML may show nothing |

DOM detection without a browser: grep the page's JS for sinks
(`innerHTML`, `document.write`, `eval`, `location.hash` flows);
a value that goes source→sink inside JS is DOM XSS even if the
server response never contains the marker.

```bash
grep -oE 'innerHTML|outerHTML|document\.write|eval\(|location\.(hash|search)|setTimeout\(|setInterval\(|new Function|\.html\(|\.append\(' page.js
```

---

## 5. Viewer confirmation — someone must render it

The flag-path question from SKILL.md step 0: who renders it?

```text
self-XSS    → only you see it — useless unless chained to
              login-CSRF/self-stored paths (rare)
stored XSS  → any visitor renders → admin bot = the viewer
reflected   → the bot must VISIT YOUR URL — report/contact form,
              or a URL parameter the bot clicks
DOM         → same — bot loads the page, JS moves the marker
              into the sink
```

If there's no viewer (no bot, no shared page), the flag is not
reachable via XSS — check the other classes.

---

## 6. Sanitizer fingerprint — what class of filter

Probe the sanitizer's BEHAVIOUR, not its name:

```text
send <b>x</b>          → renders bold?            HTML allowed
send <script>          → stripped entirely?        tag filter
send <script>          → <script removed?          blacklist removal
send <scrip<script>t>  → <script>?                  nested-strip
send <SCRIPT>          → survives?                  case-sensitive filter
send <sCrIpT>          → survives?                  mixed-case filter
send <img src=x>       → renders img?               img allowed
send <img src=x onerror=alert(1)> → event attr gone?  attr filter
send javascript:alert(1) → survives in href?         scheme filter
send <svg>             → renders?                   svg allowed
send <math>            → renders?                   mathml allowed
send a" onclick="x     → " stripped or escaped?     quote handling
send <div title="x" onmouseover="alert(1)">
                     → onmouseover stripped?      handler filter
```

Each answer narrows the bypass family — `filter-bypass.md` maps
each observation to the transform that survives.

---

## 7. Encoding-awareness probes — what the app does before rendering

```text
send &lt;              → renders as < or stays &lt;?
send &#60;             → entity decoded?
send %3C               → URL-decoded before render?
send \u003c            → JS-escape decoded?
send &#x3c;            → hex entity decoded?
```

A value that gets entity-decoded once → single-encoded payload.
Double-decoded → double-encode. `encodings.md` §3 for the layer
stack.

---

## 8. The rendering pipeline — where filters sit

```text
input → [WAF] → [app validation] → [DB storage]
      → [sanitizer on READ] → [template escaping]
      → [response] → [browser parser] → [DOM sanitizer (DOMPurify)]
      → [final DOM]
```

The payload must survive EVERY layer. A probe that dies at WAF
never reaches the sanitizer — identify WHICH layer killed it by
which send disappears: WAF = 403/block page; app validation =
400/error; sanitizer = 200 but mangled; template escaping = entities
in response; DOM sanitizer = clean response but broken DOM.

---

## 9. DOM-XSS source discovery — grep the bundle

```javascript
// the classic sources to grep for in JS:
location.hash          location.search         location.href
document.URL           document.documentURI    document.referrer
document.cookie        window.name             localStorage
sessionStorage         postMessage             indexedDB
history.state          performance.timing      RegExp.$1
// jQuery/UA params:
$.url().param()        $.query                 URLSearchParams
```

and sinks:

```javascript
innerHTML outerHTML insertAdjacentHTML document.write document.writeln
eval setTimeout(string) setInterval(string) new Function
location.href= location.assign location.replace
srcdoc src= href= action= formaction=
$.html() $.append() $.prepend() $.after() $.before() $.wrap()
$.parseHTML() $(html_string)
Range.createContextualFragment    Element.setHTML (new, rare)
```

A source→sink pair with no sanitizer between = DOM XSS candidate.

---

## 10. Falsifiers — when it's NOT XSS

- Marker never appears in response NOR in any later page → the
  value isn't reflected anywhere; no XSS surface on this param.
- Marker appears entity-encoded on EVERY render → the escaping is
  consistent; markup injection dead unless another context exists.
- The "payload runs" but only in YOUR browser on YOUR crafted page
  → self-XSS, no viewer — chain or drop.
- Bot never visits → no viewer → no flag path.
- Sanitizer strips every payload family after 2 variants each →
  `LOOP_DISCIPLINE` pivot — wrong class or wrong layer.

---

## 11. The decision order

```text
1. marker rendered?            → no = dead param, next param
2. metachars survive?          → the context map (§2)
3. which context?              → html / attr / js / url / css / dom
4. filter fingerprints?        → case? tags? handlers? scheme?
5. encoding layers?            → single/double decode, entity decode
6. viewer exists?              → bot form / stored page / shared view
7. only then pick the payload
```

Every section of this corpus keys off the context found here —
`contexts.md` is the full per-context grammar; the event/tag
matrix is `events.md`; the payload corpus is `payload-dictionary.md`.
