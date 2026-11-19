# Detection deep 2 — the endpoint taxonomy and the bot taxonomy

## The endpoint taxonomy

### Type 1: bare driver

A `chromedriver`/`geckodriver`/`msedgedriver` process listening on a
port. The simplest surface — `POST /session` -> a session -> the full
primitive set. No routing, no nodes, one browser per session.

- **probe**: `POST :9515/session`
- **signature**: `sessionId` + `browserName` in the response
- **the reach**: the driver's own host — `file://` is its filesystem,
  `localhost` is its loopback

### Type 2: Selenium Grid

A hub on `:4444` routing sessions to nodes. The capability negotiation
picks the node — the browser/version/platform you get is whichever
node your `capabilities` match.

- **probe**: `POST :4444/session`, `GET :4444/status`
- **signature**: a `sessionId` + a `/status` node inventory
- **the reach**: the *node's* host — `file://`/`localhost` are the
  node's, which may differ from the app's

### Type 3: proxied driver

A driver routed behind the app's HTTP port — `/session`, `/wd/hub/*`,
`/api/webdriver`. The same commands, the app's origin.

- **probe**: `POST /session` on the app port
- **signature**: a WebDriver `sessionId` on the app's own port
- **the reach**: the driver's host, accessed through the app's route —
  the app's auth may gate it

### Type 4: CDP endpoint

`--remote-debugging-port=9222` — DevTools over HTTP+WebSocket. A
different, richer API than WebDriver.

- **probe**: `GET :9222/json`
- **signature**: a JSON target list with `webSocketDebuggerUrl`
- **the reach**: attach over ws -> `Page.navigate`, `Runtime.evaluate`,
  `Network.*` — the full protocol

### Type 5: managed/cloud driver

A BrowserStack-style or docker-selenium managed driver — `POST
/session` with its own capability space and auth. Rarer in CTF, same
command set.

## The bot taxonomy

### Type A: the supplied-script bot

`bot.js`/`admin.py` in the handout — the spec is explicit. Copy its
URL/credential/wait/flags/version verbatim.

### Type B: the report-flow bot

A form/endpoint that triggers a bot to view your submission — the
flow exists but the source may not. Reproduce from observation; flag
assumptions.

### Type C: the stored-content bot

A comment/note/profile field the admin views — the bot renders your
stored content. The payload is stored; the bot's visit renders it.

### Type D: the flag-page bot

A bot that visits a page rendering the flag — your payload reads the
page or the bot's context for the flag. The read may be a `source`/
`screenshot` of the bot's view, or an exfil.

### Type E: the action bot

A bot that performs a state change when it visits — a like, a submit,
a flag action. Overlaps `../web-csrf/` for the mechanism; this skill
supplies the reproduction.

## The discriminator probes

```
browser or fetch?     -> JS canary: a real browser runs JS
driver or Grid?       -> GET /status: a Grid returns node inventory
WebDriver or CDP?     -> GET /json: CDP returns targets
endpoint or aid?      -> POST /session: a sessionId = endpoint
bot or no bot?        -> a report/admin flow exists = bot
```

## The taxonomy-to-skill map

| Type | Module |
|---|---|
| bare driver | `attack-surface.md`, `per-endpoint.md` |
| Grid | `grid-remote.md` |
| proxied driver | `attack-surface.md` |
| CDP | `cdp.md` |
| supplied bot | `local-bot.md`, `local-bot-deep.md` |
| report-flow bot | `local-bot.md` |
| flag-page bot | `attack-shapes.md` shape 7 |
| action bot | `../web-csrf/` + `local-bot.md` |
