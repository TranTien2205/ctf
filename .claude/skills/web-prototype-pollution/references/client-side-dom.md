# Client-side DOM pollution — the browser-side twin

Client-side prototype pollution happens entirely in JavaScript: the
attacker's URL/fragment/input reaches a client-side `merge`/`extend`
or a `set(obj, path, val)` helper, and `__proto__` lands on
`Object.prototype` in the page context. Every later object literal in
that page inherits it — including the objects the app's own JS builds
for sinks (innerHTML, script src, template compile).

---

## 1. The sources — where the polluted value comes from

| Source | Shape | Parse helper |
|---|---|---|
| `location.search` | `?__proto__[x]=1` | qs, jQuery.param, URLSearchParams+loop |
| `location.hash` | `#__proto__[x]=1` | hash routers, deep-link parsers |
| `location.hash` JSON | `#{"__proto__":{"x":1}}` | `JSON.parse(atob(hash))` |
| form inputs merged to config | `<input name="__proto__.x">` | jQuery.serialize → merge |
| `postMessage` payload | `window.addEventListener('message', ...)` | `_.merge(state, e.data)` |
| stored JSON | localStorage, a saved "settings" object | `JSON.parse` → merge |
| server-reflected JSON | an API response the client merges | `_.merge(ui, resp)` |
| cookie | `prefs={"__proto__":...}` | `JSON.parse(Cookies.get())` |

The fragment (`#`) is the classic source — no server sees it, so CSP
and server filters are irrelevant; only the client code matters.

## 2. The sinks — what the polluted property buys

A polluted property is only useful if the page's own JS reads it with
a fallback. The DOM-pollution sink list:

| Polluted property | The sink that reads it | Buys |
|---|---|---|
| `__proto__.innerHTML` | `el.innerHTML = data || obj.innerHTML` | HTML injection |
| `__proto__.sourceURL`/`sourceMap` | devtool comment writers | script context |
| `__proto__.src` | `script.src = obj.src` | script load → XSS |
| `__proto__.href` | `a.href = obj.href` | navigation |
| `__proto__.url`/`uri` | fetch(url), XHR.open | SSRF-in-browser / request hijack |
| `__proto__.onerror`/`onload` | handler assignment | JS execution |
| `__proto__.template`/`html` | template compile | SSTI-equivalent |
| `__proto__.gadget`/`callback` | callback lookup by name | code path selection |
| `__proto__.sanitize`/`filter` | `obj.sanitize || default` | disable the sanitizer |
| `__proto__.allowed`/`whitelist` | allowlist check | allowlist corruption |
| `__proto__.debug`/`dev` | feature-flag gate | hidden surfaces on |
| `__proto__.admin`/`role` | `user.role || 'guest'` | client-side role check |
| `__proto__.textContent` vs `innerHTML` | `el[prop] = v` where prop polluted | the write-where primitive |

The property names that matter are the ones the app's JS reads —
`bundle_miner.py` on the page's JS shows which property names are
looked up, and the read site decides which pollution key to try.

## 3. DOM clobbering — the other half

DOM clobbering is prototype pollution's sibling: not writing to
`Object.prototype` but creating NAMED elements that shadow the
properties JS reads:

```html
<a id="config" href="javascript:alert(1)"></a>
<img name="x" src="y">
<form name="submit"><input name="action"></form>
```

`window.config`, `document.x`, `form.action` resolve to elements —
an attacker-controlled `id`/`name` on an element overwrites a property
the page expected to be a string/object. The sink list:

| Clobbered | The read | Result |
|---|---|---|
| `id`/`name` on `<a>` | `location.href = config.href` | javascript: uri nav |
| `<img name=x src>` | `x.src` | controlled src |
| `id` on `<form>` | `form.action`, `form.method` | request hijack |
| `id` on any element | `window.<id>` | global shadowing |
| two same-`id` elements | `document.<id>` → collection | type confusion |

NovaCore (confirmed chain): the DOM-clobber was one link in a
hop-by-hop → cache → polyglot chain — the clobbered property became
the `src` of a script the page injected.

## 4. The end-to-end path — pollution to XSS

```
source (?#__proto__[innerHTML]=<img onerror=alert()>)
   → client merge lands on Object.prototype
   → app's own code: el.innerHTML = data || cfg.innerHTML
   → the fallback reads the polluted innerHTML
   → the img fires → XSS
```

The discriminating probe is a benign marker first:
`?__proto__[ppmarker]=1` then look for `ppmarker` reachable on a fresh
`{}` in the console — `({}).ppmarker === 1` proves the write; the sink
property is the second step.

## 5. Pollution sources that bypass filters

- **`constructor[prototype]`** in the query — the qs parser builds the
  nested object the same as `__proto__`:
  `?constructor[prototype][x]=1`.
- **`a[__proto__][x]`** — nested under a real key the merge walks.
- **Percent-encoded brackets**: `?%5f%5fproto%5f%5f[x]=1` — qs decodes
  `__proto__` after a string-level `__proto__` filter has already run.
- **JSON-in-hash**: `#{"__proto__":...}` — a `JSON.parse` of the hash
  is not a "query parameter" and skips param-level key filters.
- **`Object.create` + assignment**: `?x[__proto__][y]=1` via a library
  that does `obj.x = obj.x || {}; obj.x.y = v` — `obj.x` is `{}`,
  `obj.x.__proto__` is `Object.prototype`.

## 6. The browser-context readback

Confirm in the console/evaluator of the affected page:

```js
({}).marker              // polluted on Object.prototype
Object.prototype.marker  // direct
''.marker                // inherited on strings too
[].marker
document.createElement('div').marker
```

Every fresh object type should carry it — `Object.prototype` is the
root of all of them.

## 7. The defense list — what a denial looks like

- `Object.freeze(Object.prototype)` early in the app — writes throw or
  no-op (test with `({}).x = 1` first).
- The merge uses `Object.keys`/`for..of`/`hasOwnProperty` — `__proto__`
  key is skipped entirely.
- A key blacklist `['__proto__','constructor','prototype']` — reach
  through `constructor.prototype` or case/encoding variants.
- Trusted Types / CSP block the sink even when pollution lands —
  pollution confirmed, no XSS; record that separately (the class is
  proven; the sink is gated).

## 8. The verify checklist

1. Source reachable (`?#` param parsed by a merge).
2. Merge vulnerable (`__proto__` lands on `Object.prototype`, verified
   by `({}).marker`).
3. A sink reads the polluted property with a fallback (found in the
   bundle source, named by `bundle_miner`).
4. The sink's context is executable (script src, innerHTML, template).
5. CSP/Trusted Types do not block the sink — or the sink type is
   exempt (inline allowed, a gadget src domain allowed).
