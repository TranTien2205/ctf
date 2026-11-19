# Per-route — the endpoint map, and what each route gives you

## The session routes

| Route | Method | Gives you |
|---|---|---|
| `/session` | POST | a `sessionId` — the foothold |
| `/session/{id}` | DELETE | cleanup — always call |
| `/session/{id}/url` | POST | navigation (file://, http://) |
| `/session/{id}/url` | GET | the current URL |
| `/session/{id}/source` | GET | rendered DOM / file text |
| `/session/{id}/screenshot` | GET | base64 PNG |
| `/session/{id}/title` | GET | the page title |
| `/session/{id}/execute/sync` | POST | JS in the page context |
| `/session/{id}/execute/async` | POST | async JS |
| `/session/{id}/cookies` | GET/POST/DELETE | the cookie jar |
| `/session/{id}/element` | POST | find an element |
| `/session/{id}/timeouts` | POST | set command timeouts |
| `/session/{id}/window/rect` | POST | viewport size |
| `/session/{id}/back` `/forward` `/refresh` | POST | history nav |
| `/status` | GET | driver/browser version |
| `/sessions` | GET | active sessions (non-standard) |

## The Grid routes

| Route | Gives you |
|---|---|
| `:4444/session` | session on a routed node |
| `:4444/status` | node inventory — browsers, versions, OS |
| `:4444/wd/hub/*` | the older Grid3 API shape |
| `:4444/graphql` | Grid4's introspection — node metadata |

## The CDP routes (port 9222, not WebDriver)

| Route | Gives you |
|---|---|
| `GET /json` | targets + `webSocketDebuggerUrl` |
| `GET /json/version` | browser version |
| ws `Page.navigate` | navigation |
| ws `Runtime.evaluate` | JS with `awaitPromise` |
| ws `Page.captureScreenshot` | PNG |
| ws `Network.*` | request/response with bodies |

## Route-probe order

```
/status            -> is a driver answering? version?
/session (POST)    -> can I create a session? capability errors?
/sessions          -> leaked/active sessions? (non-standard)
/json (on 9222)    -> is CDP exposed? target list?
```

## The route-to-primitive map

| You have | Primitive unlocked |
|---|---|
| `POST /session` -> id | everything below |
| `.../url` + `.../source` | file read, loopback, DOM |
| `.../execute/*` | cookie, storage, JS fetch |
| `.../cookies` | the jar incl. HttpOnly |
| `.../screenshot` | rendered read |
| `9222 /json` + ws | full CDP — bodies, intercept |

A `POST /session` that answers is the whole capability set — the
route map is which command to call for which primitive.
