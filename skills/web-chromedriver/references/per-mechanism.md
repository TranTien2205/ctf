# Per-mechanism — the reachable primitives, one row each

## The navigation primitive

- **What**: `POST /session/{id}/url` -> the browser loads any URL.
- **Reaches**: `file://`, `http://localhost/`, internal services, the
  app's own origin.
- **Read-back**: `GET /source`, `GET /screenshot`, `GET /title`.
- **Falsifier**: navigation to the scheme/host errors or is refused.
- **Budget**: cheap — the read is one navigate + one source.

## The JS-execution primitive

- **What**: `POST /session/{id}/execute/sync` and `/execute/async`.
- **Reaches**: the page's JS context — DOM, cookies, `fetch`, storage.
- **Read-back**: the `return` value serialised to JSON.
- **Falsifier**: `execute` returns a permissions/disabled error.
- **Budget**: cheap — richer than navigation for reads.

## The cookie primitive

- **What**: `GET/POST/DELETE /session/{id}/cookies`.
- **Reaches**: the browser's cookie jar for its origins.
- **Read-back**: `GET /cookies` returns them (not HttpOnly-flagged
  ones via JS, but via the jar).
- **Falsifier**: the flag cookie is not in the jar / not readable.
- **Note**: `GET /cookies` bypasses `document.cookie`'s HttpOnly block
  — it reads the jar, not the JS view.

## The local-bot reproduction primitive

- **What**: a local driver you own, matching the challenge's bot.
- **Reaches**: console, DOM, network, screenshot — the observability.
- **Falsifier**: cannot reproduce faithfully (no source, no observable
  properties, closed remote).
- **Budget**: the development loop — bounded by the five-probe rule
  per mechanism layer, not by bot visits.

## The screenshot primitive

- **What**: `GET /session/{id}/screenshot` -> base64 PNG.
- **Reaches**: whatever the page renders — a flag drawn as an image, a
  rendered file.
- **Falsifier**: renders blank / the flag is not in the rendered view.
- **Note**: the PNG is the artifact — read text with `source` first.

## The CDP primitive

- **What**: DevTools protocol over `9222` or via `newCDPSession`.
- **Reaches**: network bodies, request interception, `Runtime.evaluate`
  with `awaitPromise`, `Page.captureScreenshot`.
- **Falsifier**: `9222` not exposed / CDP not available.
- **Note**: reach for it when WebDriver cannot answer — not a default.

## The loopback-origin primitive

- **What**: the browser's position on the challenge host -> `localhost`.
- **Reaches**: routes the app serves only locally — admin, debug, API.
- **Falsifier**: `localhost` returns nothing the external view lacks.
- **Note**: same read-back as navigation — `source`/`screenshot`.

## The same-origin-context primitive

- **What**: `execute` inherits the browser's origin + cookies.
- **Reaches**: same-origin APIs, `document.cookie`, `localStorage`,
  the flag page the origin can fetch.
- **Falsifier**: the flag is not reachable from the browser's origin.
- **Note**: the richest single primitive — JS + origin + cookies.

## The primitive-selection table

| Goal | First primitive | Fallback |
|---|---|---|
| file read | navigation `file://` | `execute` `fetch("file://")` |
| flag cookie | `GET /cookies` | `execute` `document.cookie` |
| internal route | `localhost` navigation | `execute` `fetch("localhost")` |
| flag page text | `localhost`/origin nav + `source` | `execute` `fetch` the page |
| rendered flag | `screenshot` | `source` for the text |
| observe payload | local bot + four hooks | CDP for bodies |
