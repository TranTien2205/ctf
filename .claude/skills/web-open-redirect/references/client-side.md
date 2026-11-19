# Client-side redirects — the meta-refresh and JS-navigation twins

## The model — the redirect without a Location header

```text
server-side:  Location: <param>           <- the header carrier
client-side:  <meta http-equiv="refresh" content="0;url=<param>">
              window.location = <param>
              location.href = <param>
              location.replace(<param>)
              location.assign(<param>)
              history.pushState(..., <param>)
              location.hash = <param>     <- a hash-nav, not a full redirect
```

The client-side twin redirects without a `Location:` header — the evidence
is the verbatim meta-content or JS-assignment value carrying the canary.

## The meta-refresh surface

```bash
# the probe — the param lands in a meta-refresh
curl -s "$BASE/redirect?url=https://attacker.invalid" | grep -i 'refresh'
# <meta http-equiv="refresh" content="0;url=https://attacker.invalid">
#   the 'content' value carries the canary verbatim
```

The `content="0;url=<param>"` — the `url=` inside the content attribute is
the destination. A `content="5;url=<param>"` (a delay) still redirects;
a `content="0;url=<param>"` is instant.

## The JS-navigation surface

```bash
curl -s "$BASE/redirect?url=https://attacker.invalid" | grep -iE 'location|window'
# <script>window.location = "https://attacker.invalid"</script>
# location.href = "<param>"
# location.replace("<param>")
# location.assign("<param>")
# location = "<param>"           <- a bare `location =` is a nav
```

The verbatim assigned value is the evidence. `location=`/`location.href=`/
`location.replace(`/`location.assign(` all navigate; `location.hash=` only
changes the fragment (a hash-nav, not a full redirect — different impact).

## The DOM-source redirect — the param read by the page's own JS

```javascript
// the page's JS reads the param and navigates — the bundle-side surface
const u = new URLSearchParams(location.search).get('next');
location.href = u;                     // <- the param -> the nav-sink
```

```bash
# the bundle-side — grep the JS for a location.* sink fed by a param
curl -s "$BASE/app.js" | grep -oE '(location|window\.location|location\.href|location\.replace|location\.assign|history\.pushState|location\.hash)\s*[=(][^;]*'
# then feed the source: ?next=https://attacker.invalid
```

The DOM-source redirect — the param is read by the page's JS and assigned
to a nav-sink — is the client-side-twin the server-side Location never
shows. `bundle_miner.py` / the JS grep find the sink.

## The `location.hash` flow — the fragment-carried param

```javascript
// the param in the fragment -> the JS reads location.hash -> navigates
// ?#next=https://evil.com -> location.hash = '#next=https://evil.com'
// -> JS parses it -> location.href = 'https://evil.com'
```

The fragment never reaches the server — a `#next=` param is invisible to a
server-side log/probe; the client-side JS reads it. Check the bundle for a
`location.hash` parse feeding a nav-sink.

## The postMessage/history surface

```javascript
window.addEventListener('message', e => { location.href = e.data.url; });
// a postMessage-driven redirect — the 'url' in the message
history.pushState(null, '', attackerUrl);   // a same-origin URL change
//   (pushState can't change the ORIGIN — a same-origin-sink only)
```

`pushState`/`replaceState` can only change the PATH on the same origin —
not a cross-origin redirect. `location.href`/`assign`/`replace`/`meta` can.

## The javascript:/data: scheme in the client-side sink

```bash
# the client-side sink with a javascript: scheme — an XSS twin
curl -s "$BASE/x?url=javascript%3Aalert(1)" | grep -i location
# location.href = "javascript:alert(1)" — a JS-scheme sink -> XSS
# data:text/html,<script>alert(1)</script> — a data:-scheme sink -> XSS
```

The client-side sink accepting a `javascript:`/`data:` scheme is the
XSS-twin — `web-xss`'s DOM-sink territory.

## The client-side-evidence record

```text
confirm: client-side open-redirect
carrier: <meta|location.href|location.replace|location.assign|location.hash>
evidence: 'content="0;url=https://attacker.invalid"' / 'location.href="https://attacker.invalid"' (verbatim)
param:   url  endpoint: /x
```

## The client-side-vs-server-side distinction

| The carrier | The evidence | The bypass surface |
|---|---|---|
| `Location:` header | the verbatim header | the server-side filter/parser |
| `meta refresh` | the `content=` value | a server-side template inject OR a JS-set meta |
| `location.href=` | the assigned value | a DOM-source sink — the param's read |
| `location.hash` | the parsed fragment | the fragment-param — no server hit |

## The client-side negatives

```text
?url=https://evil.com -> window.location="/safe"      <- the JS sanitizes
?url=https://evil.com -> location.href=escape(u)      <- escaped
?url=https://evil.com -> <a href="/x?url=...">         <- reflected not nav
```
