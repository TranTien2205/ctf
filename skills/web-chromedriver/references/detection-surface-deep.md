# Detection surface deep — every hiding place, indexed

## The endpoint's hiding places, in depth

### A bare driver port

`chromedriver` defaults to `9515`; `geckodriver` to `4444` (clashing
with Grid's hub port); `msedgedriver` to `9515`; Appium to `4723`.
Each answers `POST /session` — the probe is identical across them.

```
9515  chromedriver / msedgedriver
4444  Selenium Grid hub / geckodriver
9516  alternate chromedriver
4723  Appium
5555  older selenium RC / geckodriver
7055  legacy geckodriver
9222  Chrome remote debugging (CDP — not WebDriver)
```

### A Selenium Grid

`:4444` answering both `POST /session` and `GET /status` — the hub.
The status names its nodes, their browsers/versions/platforms, and the
`stereotype` capabilities to send to land on each. A Grid4 also exposes
`/graphql` for node introspection.

### A proxied driver

Some challenges route the driver behind the app's own port —
`/session`, `/wd/hub/session`, `/webdriver/session`, `/api/webdriver`.
Probe the app port for the WebDriver routes, not just the driver
ports. A proxied driver carries the app's origin — a slightly
different surface (the app's auth may gate it).

### A CDP endpoint

`--remote-debugging-port=9222` opens DevTools over HTTP+WebSocket —
`GET /json` returns targets. A richer API than WebDriver but a
different surface — the probe is `GET /json`, not `POST /session`.

### A container's exposed port

`docker-compose` `ports:` in the handout names an exposed driver —
a `bot`/`admin`/`browser`/`selenium` service with `9515:9515` or
`4444:4444` published. The compose file is the detection shortcut.

## The bot's hiding places, in depth

### A supplied bot script

`bot.js`, `admin.py`, `visit.js`, `bot/index.js`, `admin/bot.py` —
the bot's spec. Read it for URL/credential/wait/flags/version.

### A report/admin-visit flow

A "report to admin", "flag for review", "contact admin", "request a
visit" form — your submission triggers a bot to view it. The flow's
existence is the bot detection; its source may or may not be supplied.

### A compose bot service

`bot:`, `admin:`, `browser:`, `visitor:` service in compose — the
bot's container. Its `build:`/`image:` names the bot's environment;
its `depends_on`/`links` names what it can reach.

### A driver import in app source

`require('puppeteer')`, `from playwright`, `from selenium`, `new
webdriver`, `webdriver.Chrome` — the bot's driver library embedded in
the app's code. The import names the mechanism even when the bot
script is elsewhere.

### The challenge text

"the admin will check your submission", "a bot will visit", "an admin
reviews reports" — the bot flow stated outright, even when nothing
else reveals it.

## The surface-to-module map

| Found | Open |
|---|---|
| driver port | `attack-surface.md`, `per-endpoint.md` |
| Grid | `grid-remote.md` |
| CDP port | `cdp.md` |
| bot script | `local-bot.md`, `local-bot-deep.md` |
| bot flow | `local-bot.md` |
| compose bot service | `local-bot.md`, `detection-playbook.md` |
| driver import | `local-bot.md` |
| nothing | the class is dead — record why |
