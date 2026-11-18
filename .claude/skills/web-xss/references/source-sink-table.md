# Source → sink reference — the complete pair table

The DOM-XSS companion to `dom-xss.md` — every source, every sink,
the pairs that matter, organized by what the source yields.

---

## Sources — organized by attacker-control reach

### URL-derived (you control via the link)

```javascript
location.hash               -- '#x' → 'x' after slice(1)
location.search              -- '?x=..' → after the '?'
location.href                -- whole URL string
location.pathname            -- path segment
location                     -- Location object → stringified
document.URL                 -- same as location.href
document.documentURI         -- same
document.baseURI             -- the <base> URL — clobberable
new URLSearchParams(s).get(k) -- parsed param
```

### Frame/window-derived (opener/parent controlled)

```javascript
window.name                  -- the opener-set name — SURVIVES nav
window.opener.*              -- the opener window — if still open
parent.*                     -- parent frame's values
top.*                        -- top frame
frames[i].*                  -- sibling frames
document.referrer            -- the referring URL — attacker-set
history.state                -- pushState'd data
```

### Storage-derived (persisted, cross-page)

```javascript
localStorage.x                -- persists across sessions
sessionStorage.x              -- per-tab
indexedDB.x                   -- structured store
document.cookie               -- cookie values
Cache/CacheStorage            -- service-worker cache
```

### Message-derived

```javascript
e.data in a 'message' listener      -- postMessage
e.data in a worker listener          -- worker.postMessage
BroadcastChannel message              -- cross-tab channel
```

### Browser-derived (limited attacker control)

```javascript
navigator.userAgent           -- UA — only if attacker-set
navigator.language
navigator.plugins
performance.getEntries()      -- timing entries
window.performance.*          -- perf data
RegExp.$1/$&                  -- last regex match
```

---

## Sinks — organized by what the write does

### HTML-parse sinks (markup context — tags become DOM)

```javascript
el.innerHTML = x
el.outerHTML = x
el.insertAdjacentHTML(pos, x)
document.write(x)
document.writeln(x)
Range.createContextualFragment(x)
el.setHTML(x)                          -- Sanitizer API
el.srcdoc = x                          -- iframe srcdoc attr
$(el).html(x)   $(el).append(x)   $(el).prepend(x)   -- jQuery
$(el).before(x)   $(el).after(x)   $(el).replaceWith(x)
$(x)                                   -- jQuery creation
$.parseHTML(x)
el.setAttribute('innerHTML', x)        -- attr-form (same effect)
```

### Code-eval sinks (JS-string context — runs as code)

```javascript
eval(x)
new Function(x)()    Function(x)
setTimeout(x, n)     setInterval(x, n)      -- string arg
setImmediate(x)      execScript(x)           -- IE
el.setAttribute('on*', x)                  -- attr-form of handler
el.onclick = x                             -- x must be a function
window.eval(x)  top.eval(x)  self.eval(x)
setTimeout.call(null, x)                   -- call-form
```

### URL-navigation sinks (URL context — `javascript:`/`data:`)

```javascript
location = x   location.href = x   location.assign(x)
location.replace(x)   location.hash = x
window.location = x   document.location = x
el.href = x   el.src = x   el.action = x   el.data = x
el.formaction = x   el.poster = x   el.codebase = x
iframe.src = x   object.data = x   embed.src = x
form.action = x   button.formaction = x   input.formaction = x
history.pushState(s,t,x)   history.replaceState(s,t,x)
navigator.registerProtocolHandler(s,x,t)
```

### Storage sinks (data-context — persist for later)

```javascript
localStorage.x = y   sessionStorage.x = y
document.cookie = x   indexedDB.put(x)
```

A storage sink isn't XSS itself — it's a second-order carrier:
write attacker data, later a page reads it into an HTML sink.

### CSS sinks (style context)

```javascript
el.style.cssText = x   el.setAttribute('style', x)
el.style.background = x   el.style.backgroundImage = x
el.style.listStyleImage = x
```

CSS-only exfil paths live in `css-exfil.md`.

### Worker/module sinks

```javascript
new Worker(x)   new SharedWorker(x)   import(x)
navigator.serviceWorker.register(x)
```

---

## The pair-completeness table — every source × every sink class

| Source class | HTML-parse | Code-eval | URL-nav | Storage | CSS |
|---|---|---|---|---|---|
| location.hash | ✓ | ✓ | ✓ | — | — |
| location.search | ✓ | ✓ | ✓ | — | — |
| window.name | ✓ | ✓ | ✓ | ✓ | — |
| document.referrer | ✓ | ✓ | ✓ | — | — |
| localStorage | ✓ | ✓ | ✓ | ✓ | — |
| postMessage | ✓ | ✓ | ✓ | ✓ | ✓ |
| document.cookie | ✓ | ✓ | ✓ | ✓ | — |
| history.state | ✓ | ✓ | — | ✓ | — |
| URLSearchParams | ✓ | ✓ | ✓ | — | — |
| navigator.* | — | — | — | — | — |

✓ = the pair is exploitable with the right payload shape.
— = the pair doesn't reach a code-exec path.

---

## The "transforms that kill the flow" list

```javascript
// between source and sink — what breaks the chain:
encodeURIComponent(x)           -- kills < > " ' — html-safe
encodeURI(x)                     -- same for full-URL
escape(x)                        -- deprecated — same idea
parseInt(x)                      -- only digits remain
parseFloat(x)                    -- digits + . survive
Number(x)                        -- numeric coercion
x.replace(/<[^>]*>/g,'')          -- naive tag-strip
x.replace(/<script/gi,'')         -- string-strip
DOMPurify.sanitize(x)             -- real sanitizer
textContent-only path            -- never parsed as markup
x.split('').map(...).join('')    -- char-transform
```

A transform either kills the flow (encode) or preserves it
(decode). Multi-transform chains matter — a `decodeURIComponent`
before innerHTML keeps the flow alive.

---

## The "transforms that keep the flow alive" list

```javascript
decodeURIComponent(x)           -- the decoded form reaches the sink
unescape(x)                      -- same
atob(x)                          -- b64 decode
String(x)                        -- string-coerce — no-op for strings
x.toString()                     -- same
x.concat(y)                      -- concat — both parts reach sink
x.split(',').join(',')           -- roundtrip — no-op
x.slice(1)                       -- substring — rest still reaches
x.toLowerCase()                  -- case-fold — tags still parse
x.toUpperCase()                  -- same
```

Each source→sink pair runs through zero or more transforms —
the flow survives if no killer-transform is between them.
