# Dangerous DOM APIs — the complete sink reference

Every DOM API that turns attacker data into code/markup/URL-side
effect. The audit list — grep the target's JS for each name.

---

## 1. The innerHTML family — the #1 sink

```javascript
el.innerHTML = x           -- parses x as HTML — handlers fire;
                           -- <script> does NOT run via innerHTML
el.outerHTML = x           -- replaces el itself
el.insertAdjacentHTML('beforebegin'|'afterbegin'|'beforeend'|'afterend', x)
Range.createContextualFragment(x)
el.setHTML(x)              -- new Sanitizer-API
```

`<script>` inside innerHTML is inserted-but-not-run — the scripts
don't execute on assignment. Handler attrs DO bind. jQuery's
`.html()` differs — jQuery extracts and evals scripts itself.

---

## 2. document.write/writeln — parse-time eval

```javascript
document.write(x)
document.writeln(x)
```

Parses x as full document markup — `<script>` INSIDE it RUNS
(unlike innerHTML). Only during initial page parse; after
DOMContentLoaded it rewrites the whole page.

---

## 3. The eval-family — code-from-string

```javascript
eval(x)
window.eval(x)  self.eval(x)  top.eval(x)  parent.eval(x)
new Function(x)()     Function(x)
setTimeout(x, n)                  -- string arg = eval
setInterval(x, n)                 -- string arg = eval
setImmediate(x)                    -- IE
execScript(x)                      -- IE
```

The Function-constructor family — every `X.constructor` chain
reaches it (`gadgets.md` §6).

---

## 4. The URL-assignment family

```javascript
location = x
location.href = x
location.assign(x)
location.replace(x)
window.location = x
document.location = x
top.location = x
parent.location = x
frames[i].location = x
```

Any `javascript:`/`data:` in these runs code (javascript:) or
loads a document (data:).

---

## 5. The el.attr-URL family — URL-bearing attrs

```javascript
el.href = x        a.href = x       -- needs click
el.src = x         iframe/embed/object src — loads on set
el.action = x      form.action — on submit
el.formaction = x  button/input formaction — on click
el.data = x        object.data — loads on set
el.codebase = x    object/applet codebase — legacy
el.poster = x      video poster — image-load only
el.cite = x        blockquote cite — no effect
el.background = x  body/table background — image-load only
el.longdesc = x    img longdesc — no effect
el.profile = x     head profile — dead
el.usemap = x      img usemap — #ref
el.manifest = x    html manifest — dead API
el.srcdoc = x      iframe srcdoc — markup context!
```

`srcdoc` is the special one — it's markup-context not URL-context.

---

## 6. The event-attr family — code in attrs

```javascript
el.setAttribute('onclick', x)        -- x IS code
el.setAttribute('onerror', x)
el.setAttribute('onload', x)
   -- any on* name — the attr value is JS
el.onclick = function(){...}          -- assign a FUNCTION — different:
el.onclick = 'alert(1)'               -- string-assignment doesn't run!
```

setAttribute('on*', string) binds the string as the handler —
fires on the event. `.onclick = string` does NOT run — the
property wants a function. The distinction matters.

---

## 7. The script-family — script-loading APIs

```javascript
s = document.createElement('script');
s.src = x;                          -- script-src URL — needs a real
                                     script URL (javascript: NO,
                                     data:text/javascript YES)
s.text = x;                          -- inline script text — code!
s.textContent = x;                   -- same
s.innerHTML = x;                     -- same
document.head.append(s)

import(x)                            -- dynamic module import —
                                     URL context
new Worker(x)                        -- worker URL
new SharedWorker(x)
navigator.serviceWorker.register(x)  -- SW URL — needs same-origin
```

---

## 8. The jQuery sink family — the library's own

```javascript
$(x)                        -- $(html) creates elements + evals scripts
$(el).html(x)               -- parses + EVALS <script> in x!
$(el).append(x)             -- same
$(el).prepend(x)            -- same
$(el).before(x)             -- same
$(el).after(x)              -- same
$(el).replaceWith(x)        -- same
$(el).wrapInner(x)          -- same
$(el).wrapAll(x)            -- same
$.parseHTML(x)              -- explicit parser — evals scripts
$.globalEval(x)             -- direct eval
$.getScript(x)              -- remote script
$(el).load(x)               -- remote html+scripts
$(el).load(url, cb)          -- the deprecated ajax loader
jQuery.parseHTML(x)          -- namespace form
```

jQuery's DOM-writers EVAL scripts — `<script>alert(1)</script>`
in `.html(x)` runs, unlike raw innerHTML.

---

## 9. The `insertAdjacent*` family — position-marked inserts

```javascript
el.insertAdjacentHTML('beforebegin', x)
el.insertAdjacentHTML('afterbegin', x)
el.insertAdjacentHTML('beforeend', x)
el.insertAdjacentHTML('afterend', x)
el.insertAdjacentText(...)              -- text-only — safe
el.insertAdjacentElement(...)           -- element-only — safe
```

Only the HTML variant parses markup — Text/Element are safe.

---

## 10. The `setHTML`/Sanitizer API — the new gate

```javascript
el.setHTML(x)                          -- sanitized by default
el.setHTML(x, {sanitizer: s})          -- explicit sanitizer
el.setHTMLUnsafe(x)                    -- the UNSAFE variant — raw!
```

`setHTMLUnsafe` is the opt-out — grep for it. The Sanitizer-API
is new — most code doesn't use it yet.

---

## 11. The `DOMParser`/`parseFromString` family

```javascript
new DOMParser().parseFromString(x, 'text/html')
   -- parses x into a detached document — scripts DON'T run in the
      detached doc, but handlers BIND — if the parsed nodes get
      appended to the live DOM, handlers fire
```

The detached-doc → live-doc transfer is where it fires.

---

## 12. The `cloneNode`/`importNode`/`adoptNode` — node-carriers

```javascript
document.importNode(node)             -- imports a parsed node
document.adoptNode(node)              -- same
el.cloneNode(true)                     -- clones handlers too
```

These carry already-parsed nodes into the live DOM — if the source
node had a handler it survives the transfer.

---

## 13. The `customElements`/shadow-DOM sinks

```javascript
el.attachShadow({mode:'open'})         -- shadow root — innerHTML
   inside it is the same sink, scoped to the shadow tree
shadowRoot.innerHTML = x
```

Shadow-DOM innerHTML is a normal sink — scoped to the shadow root
(CSP still applies, the page's own querySelector can't see in).

---

## 14. The "assignment-that-parses" traps

```javascript
el.textContent = x          -- SAFE — text, not markup
el.innerText = x            -- SAFE — text
el.nodeValue = x            -- SAFE — text
document.title = x          -- SAFE — title is text context
```

The text-only set — writing these never parses markup. The
mistake: thinking `innerText` is `innerHTML` — they're different.

---

## 15. The grep list — the audit regexes

```text
innerHTML|outerHTML|insertAdjacentHTML|document\.write|createContextualFragment
eval\(|new Function|setTimeout\(|setInterval\(|setImmediate|execScript
location\s*=|\.href\s*=|\.src\s*=|\.action\s*=|\.formaction|\.data\s*=
setAttribute\(['"]on|\.srcdoc|\.setHTMLUnsafe
\.html\(|\.append\(|\.prepend\(|\.before\(|\.after\(|\.replaceWith\(
\.load\(|\.parseHTML|\.globalEval|\.getScript
import\(|new Worker|SharedWorker|register\(
DOMParser|parseFromString|importNode|adoptNode|cloneNode|attachShadow
```

Run against the bundle + source-maps — each hit is a candidate
sink to trace back to a source.
