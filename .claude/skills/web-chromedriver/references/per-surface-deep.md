# Per-surface deep — each reachable surface, with reads and yields

## The file surface (`file://`)

The browser's filesystem, read as the driver's user — the richest
single surface on an exposed endpoint.

| Path | Yields |
|---|---|
| `/etc/passwd` | users — the canary that proves the read |
| `/flag`, `/flag.txt` | the flag, direct |
| `/proc/self/environ` | env vars — `FLAG`, secrets, paths |
| `/proc/self/cmdline` | how the driver/app launched |
| `/proc/self/mounts` | mounts -> flag filesystem locations |
| `/app/*`, `/srv/*`, `/var/www/*` | app source, config, flag |
| `/root/*`, `/home/*/*` | dotfiles, keys, the flag |
| `~/.ssh/id_rsa`, `~/.aws/credentials` | credentials |

Reads: `nav file://` + `source` (text), or `execute` `fetch` + base64
(binary).

## The loopback surface (`localhost`, `127.0.0.1`, `[::1]`)

The browser's network position — the app itself plus internal services.

| Route | Yields |
|---|---|
| `localhost:APP/admin` | the internal admin panel |
| `localhost:APP/debug`, `/actuator`, `/metrics` | introspection |
| `localhost:INTERNAL/*` | a second service on another port |
| `localhost:APP/flag` | a flag route served internally |
| `127.0.0.1`/`[::1]` aliases | loopback when `localhost` is filtered |

Reads: `nav localhost` + `source`, or `execute` `fetch("localhost")`.

## The origin surface (the app's own origin)

The browser carries the challenge's origin + its cookies — same-origin
reads and writes.

| Resource | Yields |
|---|---|
| the flag page the origin fetches | the flag via `execute` `fetch` |
| `localStorage`/`sessionStorage` | tokens, the flag |
| the authenticated API | session-gated data |
| a same-origin write endpoint | a stash for the flag (write-back) |

Reads: `execute` `fetch`/`localStorage`, or `GET /source` after nav.

## The DOM surface

The rendered tree — a stored flag, a hidden field, the payload's
landing context.

| Read | Yields |
|---|---|
| `GET /source` | the rendered DOM — flag text, hidden inputs |
| `execute` `document.*` | specific nodes, attributes, the flag element |

## The cookie-jar surface

`GET /session/{id}/cookies` — the jar, `HttpOnly` included. A flag
stored as an HttpOnly cookie is readable here when invisible to JS.

## The screen surface

`GET /session/{id}/screenshot` — the rendered page as PNG. A flag
rendered visually, or a page whose text source is mangled.

## The network surface

What the browser fetches — internal endpoints, the exfil, the services
behind it. Via CDP `Network` or the local bot's request hook.

## The surface-priority map

| Priority | Surface | Why first |
|---|---|---|
| 1 | `/flag`, `/proc/self/environ` | highest-yield direct reads |
| 2 | `localhost` flag/admin route | internal-only flag path |
| 3 | cookie jar / localStorage | flag-in-credential cases |
| 4 | origin flag page | flag the bot's origin can fetch |
| 5 | DOM / screenshot | rendered or stored flag |
