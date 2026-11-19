# Per-endpoint deep — each endpoint, its internals and its use

## `POST /session` — the create

**The mechanism**: the driver spawns (or attaches to) a browser
process and returns a `sessionId` handle. The `capabilities` JSON
selects the browser and its launch options.

**The negotiation**: `alwaysMatch` applies to every session;
`firstMatch` is a list of alternates the driver may satisfy. A
mismatch returns `session not created: No matching capabilities`. The
legacy `desiredCapabilities` form is for pre-W3C drivers/Grids.

**The use**: the foothold — a `sessionId` = the endpoint is exposed.

**The edge**: on a single-browser driver, a second `POST /session`
may fail or take the browser over; on a Grid, the capabilities select
which node you land on.

## `DELETE /session/{id}` — the destroy

**The mechanism**: terminates the session and its browser process.

**The use**: the mandatory cleanup — a leaked session leaks a browser
and possibly a held slot. `driver.quit()` is this.

**The edge**: on a shared endpoint, another team's leaked session is
not yours to kill — note it; killing it is a shared-instance write.

## `POST /session/{id}/url` — the navigate

**The mechanism**: translates to `Page.navigate` — the browser's
normal loader, so `file://`, `http://`, `localhost`, `data:` all work.

**The use**: the file-read and loopback primitive — navigate, then
`GET /source` to read.

**The bound**: returns on the `load` event per `pageLoadStrategy` —
`normal` waits for full load, `eager` for `DOMContentLoaded`, `none`
immediately. A never-loading page hits `timeouts.pageLoad`.

## `GET /session/{id}/source` — the DOM/file read

**The mechanism**: serialises the current DOM — the *rendered*
document after JS and sanitisation, not the response body.

**The use**: the default read-back — a `file://` read returns the file
wrapped in `<html><pre>`; a page returns its live tree.

**The edge**: a `file://` read of a binary mangles it — use `execute`
`fetch` + base64 for binary.

## `POST /session/{id}/execute/sync` — the sync JS

**The mechanism**: `Runtime.evaluate` in the page; the `return` value
serialised over the JSON wire.

**The use**: the richest read — `document.cookie`, `localStorage`,
`fetch('/flag')`, a DOM query — with the browser's origin + cookies.

**The serialisation**: JSON-safe only — elements -> `{"element-6066-"}`,
`undefined`/`function` -> `null`, circular -> error, `Promise` ->
pending.

## `POST /session/{id}/execute/async` — the async JS

**The mechanism**: the same, but blocks until `arguments[last]` (the
callback) is invoked.

**The use**: for `fetch` chains and timers — the resolved value
returns, not a pending promise.

**The bound**: `timeouts.script` — a never-invoking callback hangs to it.

## `GET /session/{id}/cookies` — the jar read

**The mechanism**: reads the browser's cookie store for the current
origin — a process-level jar, not the JS view.

**The use**: the `HttpOnly` read — the jar sees cookies
`document.cookie` cannot. A flag-as-HttpOnly-cookie is readable here.

## `GET /session/{id}/screenshot` — the render read

**The mechanism**: rasterises the viewport — a real render even
headless.

**The use**: a flag-as-image or a mangled-text flag — the PNG is the
artifact.

**The edge**: old `--headless` can render blank; `--headless=new`
rasterises fully.

## `GET /status` — the version read

**The mechanism**: the driver's own status — version, ready state.

**The use**: detection (is a driver listening?) and the version-match
(driver vs browser major).

## `GET /sessions` — the leak detector (non-standard)

**The mechanism**: lists the active sessions on drivers that support it.

**The use**: the leak detector — a session that refuses to create
often has a leaked one holding the browser.

## `GET /json` — the CDP attach (port 9222)

**The mechanism**: lists CDP targets with `webSocketDebuggerUrl` — the
attach point for the richer DevTools protocol.

**The use**: when WebDriver cannot answer — response bodies, request
interception, `Runtime.evaluate`+`awaitPromise`, precise frame control.
