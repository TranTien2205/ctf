# Mechanism catalogue — every primitive, indexed and annotated

## The session-lifecycle mechanisms

### create — `POST /session`

Spawns or attaches to a browser process. The `sessionId` returned is
the handle every later command addresses.

- **input**: `{"capabilities":{"alwaysMatch":{...}}}` (or legacy
  `{"desiredCapabilities":{...}}`)
- **output**: `{"value":{"sessionId":"...","capabilities":{...}}}`
- **the capability negotiation**: `alwaysMatch` applies to all;
  `firstMatch` is a list of alternates; a mismatch returns
  `session not created: No matching capabilities`
- **the process**: each session owns a browser process — the resource
  a leaked session leaks

### destroy — `DELETE /session/{id}`

Terminates the session and its browser. The mandatory cleanup — a
leaked session is a leaked process and, on a shared endpoint, a held
slot.

## The navigation mechanisms

### navigate — `POST /session/{id}/url`

Translates to a DevTools `Page.navigate` — the browser's normal
loader, so every scheme it can resolve works.

- **reach**: `http://`, `https://`, `file://`, `data:`, `about:`,
  `localhost`, internal hosts
- **bound**: returns on the `load` event per `pageLoadStrategy`
  (`normal`/`eager`/`none`); a never-loading page hits `pageLoad`
- **the read-back**: navigation alone returns nothing — pair with
  `source`/`screenshot`/`title` to read what loaded

### history — `/back`, `/forward`, `/refresh`

The browser's history — rarely the primitive you want, but the
mechanism for navigating a multi-step flow the bot follows.

## The read mechanisms

### source — `GET /session/{id}/source`

Serialises the current DOM — the *rendered* document, after JS and
sanitisation, not the response body.

- **the file-read form**: `file://` content arrives wrapped in
  `<html><pre>` — the file text inside
- **the DOM form**: the live tree — where a payload landed, a stored
  flag, hidden fields

### screenshot — `GET /session/{id}/screenshot`

Rasterises the viewport — a real render even headless.

- **carries**: a flag-as-image, a rendered page whose text is mangled
- **the headless note**: `--headless=new` rasterises fully; old
  `--headless` can return blank

### title — `GET /session/{id}/title`

The page title — a quick read of which page the browser is on.

## The script-execution mechanisms

### execute/sync — `POST .../execute/sync`

`Runtime.evaluate` internally; the `return` value serialised over the
JSON wire.

- **reach**: the full JS context — DOM, `fetch`, `localStorage`,
  `document.cookie` — with the browser's origin + cookies
- **serialisation**: JSON-safe only — elements -> `{"element-6066-"}`,
  `undefined`/`function` -> `null`, circular -> error, `Promise` ->
  pending unless async

### execute/async — `POST .../execute/async`

The same, but blocks until `arguments[last]` (the callback) is invoked.

- **the async read**: `fetch('/flag').then(r=>r.text()).then(d)` — the
  resolved text returns, not a pending promise
- **the timeout**: bounded by `timeouts.script` — a never-invoking
  callback hangs to it

## The cookie mechanisms

### read jar — `GET /session/{id}/cookies`

The browser's cookie store for the current origin — the jar, not the
JS view. `HttpOnly` restricts `document.cookie`, not the jar.

### set — `POST /session/{id}/cookies`

Add a cookie — `{"cookie":{"name","value","path","domain","httpOnly",
"sameSite"}}`. The reproduction's credential injection.

### delete — `DELETE /session/{id}/cookies[/{name}]`

Clear the jar / one cookie.

## The element mechanisms

### find — `POST /session/{id}/element[s]`

`{"using":"css selector","value":"..."}` -> an opaque element handle.

- **the stale rule**: a handle dies on DOM mutation/navigation —
  `stale element reference` on reuse

### act — `click`, `value`, `text`, `attribute/{n}`

Interact with a handle — click, type, read text, read an attribute.

## The frame/window mechanisms

### frame — `POST /session/{id}/frame`

Switch the *current frame* `execute`/`source`/`element` operate on —
the boundary JS cannot cross, the driver can.

### window — `POST /session/{id}/window` + `/window/handles`

Switch between open windows/handles — for `window.open` popups and
multi-tab flows.

## The status mechanisms

### status — `GET /status`

Driver/browser version — the detection and the version-match.

### sessions — `GET /sessions` (non-standard)

The active-session list — the leak detector on drivers that support it.
