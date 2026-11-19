# Per-surface — where the browser can reach, and what each surface holds

## The file surface (`file://`)

The browser's filesystem, read as the driver's user:

| Path | Holds |
|---|---|
| `/etc/passwd` | users — the always-present canary |
| `/flag`, `/flag.txt` | the flag, direct |
| `/app/*`, `/srv/*` | app source, config, flag |
| `/proc/self/environ` | env vars — secrets, paths |
| `/root/.ssh/*`, `~/.aws/*` | keys, credentials |
| `/proc/self/cmdline` | how the driver/app was launched |

## The loopback HTTP surface (`http://localhost/*`)

The browser's own network position — routes only it can reach:

| Route | Holds |
|---|---|
| `localhost:APPPORT/admin` | internal admin panel |
| `localhost:APPPORT/debug` `/actuator` `/metrics` | debug/introspection |
| `localhost:INTERNALPORT/*` | internal services on other ports |
| `localhost:PORT/flag` | a flag route the app serves internally |

## The app's own origin surface

The browser carries the challenge's origin + any cookies — same-origin
reads and writes the external unauthenticated view cannot make:

| Endpoint | Holds |
|---|---|
| the flag page the origin can fetch | the flag, via `execute` `fetch` |
| `localStorage`/`sessionStorage` | tokens, the flag |
| the authenticated API | data gated to the bot's session |
| a same-origin write endpoint | a place to stash the flag (write-back) |

## The DOM surface

The rendered tree — where a stored flag, a hidden field, or the
payload's landing context lives:

| Read | Holds |
|---|---|
| `GET /source` | the rendered DOM — flag text, hidden inputs |
| `execute` `document.*` | specific nodes, attributes, the flag element |

## The cookie-jar surface

`GET /session/{id}/cookies` reads the jar — including `HttpOnly`
cookies `document.cookie` cannot see. A flag stored as an HttpOnly
cookie is readable here when JS cannot see it.

## The screen surface

`GET /screenshot` — the rendered page as a PNG. Holds a flag rendered
visually, a captcha-like flag image, or a page whose text source is
mangled but the render is clean.

## The network surface (via CDP or the bot)

What the browser fetches — internal endpoints it hits, the exfil it
sends, the services behind it. Reachable through CDP `Network` or the
local bot's request hook.

## The surface-to-read map

| Flag lives in | Surface | Read |
|---|---|---|
| a file | `file://` | nav + `source` |
| an internal route | `localhost` | nav + `source` |
| the DOM | DOM | `source`/`execute` |
| a cookie (HttpOnly) | jar | `GET /cookies` |
| a cookie (JS-visible) | DOM/JS | `execute` `document.cookie` |
| localStorage | DOM/JS | `execute` `localStorage` |
| rendered image | screen | `screenshot` |
| a same-origin API | origin | `execute` `fetch` |
