# Detection deep — the endpoint hunt in detail

## The port map, exhaustively

| Port | Likely | Probe |
|---|---|---|
| 9515 | chromedriver default | `POST /session` |
| 4444 | Selenium Grid hub | `POST /session`, `GET /status` |
| 9516, 9517 | alternate chromedriver | `POST /session` |
| 4723 | Appium (WebDriver-derived) | `POST /session` |
| 9222 | Chrome remote debugging (CDP) | `GET /json` |
| 5555, 7055 | geckodriver / older | `POST /session` |

The probe for every driver port is the same `POST /session` — only the
port changes. `9222` is the exception: it is CDP, so `GET /json` is
the probe, not `POST /session`.

## Reading the response correctly

A real driver's `POST /session` returns:

```json
{"value":{"sessionId":"...","capabilities":{"browserName":"chrome",...}}}
```

The shape to look for is `value.sessionId`. Error responses name the
problem:

- `session not created` -> browser/version/flag problem at the driver
- `No matching capabilities` -> your capability set is unsatisfiable
- `unauthorized`/`401` -> the endpoint is gated, not absent

A refused connection or 404 is the absence signal; a JSON error is an
answering-but-failing driver — a different state.

## The capability-negotiation probe

When a plain `POST /session` fails, the endpoint may want a specific
capability. Try:

```json
{"capabilities":{"alwaysMatch":{"browserName":"chrome"}}}
{"capabilities":{"alwaysMatch":{"browserName":"firefox"}}}
{"capabilities":{"alwaysMatch":{}}}
{"desiredCapabilities":{"browserName":"chrome"}}   // legacy wire protocol
```

The legacy `desiredCapabilities` form matters — older drivers/Grids
speak the pre-W3C protocol and reject the `capabilities` shape.

## The Grid status probe

`GET /status` and `GET /wd/hub/status` on `:4444` return the hub's
inventory — nodes, browsers, versions, platforms, free slots:

```json
{"value":{"ready":true,"nodes":[{"slots":[{"session":null,"stereotype":
  {"browserName":"chrome","platformName":"linux"}}]}]}}
```

A node's `stereotype` tells you which `capabilities` to send to land
on it. This is free recon — the hub names its own attack surface.

## The CDP probe

`GET http://TARGET:9222/json` returns a target list:

```json
[{"id":"...","type":"page","url":"about:blank",
  "webSocketDebuggerUrl":"ws://.../devtools/page/..."}]
```

`type:page` targets with a `webSocketDebuggerUrl` are attachable —
each is a tab you can drive over CDP. `GET /json/version` names the
browser version.

## The app-proxied endpoint

Some challenges proxy the driver behind the app's own port —
`/session`, `/wd/hub/session`, `/webdriver/session` on the app's URL.
Probe the app port for the WebDriver routes, not just the driver
ports. A proxied driver is the same capability with the app's origin.

## The white-box read

In source, detection is a `grep` away:

```
webdriver|chromedriver|geckodriver|selenium|webdriverio
puppeteer|playwright|headless|--remote-debugging-port
new webdriver|webdriver.Chrome|launch\(|browser.newPage
```

The spawn line names the port and the flags — both the detection and
the reproduction spec in one read.
