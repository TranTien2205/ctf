# Per-route deep — the route map, with what each buys and how to hit it

## The session routes, annotated

`POST /session`
- buys: the `sessionId` — the foothold everything hangs off
- hit it: `{"capabilities":{"alwaysMatch":{"browserName":"chrome"}}}`
- legacy form: `{"desiredCapabilities":{"browserName":"chrome"}}`
- a JSON error names the missing capability

`DELETE /session/{id}`
- buys: cleanup — releases the browser process
- always: a leaked session is a leaked browser; on a shared endpoint it
  can hold the only slot

`POST /session/{id}/url` + `GET /session/{id}/url`
- buys: navigation (file://, localhost, external) + current URL
- the file-read and loopback primitive is a navigation + a read-back

`GET /session/{id}/source`
- buys: the rendered DOM / file text — the default read
- wraps a `file://` read in `<html><pre>` — parse it out

`POST /session/{id}/execute/sync` and `/async`
- buys: JS in the page — origin + cookies inherited
- sync: `return` value serialised; async: the last-arg callback
- the richest read — `document.cookie`, `localStorage`, `fetch`

`GET /session/{id}/cookies`
- buys: the cookie jar — `HttpOnly` included
- the read `document.cookie` cannot do (JS view restriction)

`GET /session/{id}/screenshot`
- buys: a base64 PNG of the viewport — the rendered read
- a flag-as-image or a mangled-text flag

`POST /session/{id}/element` and `/elements`
- buys: element handles — `click`, `value`, `text`, `attribute`
- the handle goes stale on DOM mutation/navigation

`POST /session/{id}/frame` and `/window`
- buys: frame/window switching — `execute` runs on the current frame
- a payload in an iframe is invisible until you switch into it

`GET /status`
- buys: driver/browser version — the detection and version match

`GET /sessions` (non-standard)
- buys: the active-session list — the leak detector

## The Grid routes

| Route | Buys |
|---|---|
| `:4444/session` | a session routed to a node |
| `:4444/status` | the node inventory — browsers/versions/platforms |
| `:4444/wd/hub/*` | the older Grid3 API shape |
| `:4444/graphql` | Grid4 introspection — node metadata |

## The CDP routes (port 9222 — not WebDriver)

| Route | Buys |
|---|---|
| `GET /json` | targets + `webSocketDebuggerUrl` |
| `GET /json/version` | browser version |
| ws `Page.navigate` | navigation |
| ws `Runtime.evaluate` | JS with `awaitPromise` |
| ws `Network.getResponseBody` | response bodies WebDriver cannot give |

## The route-to-goal map

| Goal | Route |
|---|---|
| get a session | `POST /session` |
| read a file | `url` + `source` |
| run JS | `execute/*` |
| read the jar | `cookies` |
| read rendered | `screenshot` |
| richer JS/HTTP | `9222 /json` -> ws CDP |
