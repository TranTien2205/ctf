# Detection surface — where to look for the endpoint and the bot

## The endpoint's hiding places

| Place | Signal |
|---|---|
| a high port on the host | `9515`,`4444`,`9516`,`4723`,`9222` |
| a proxied app route | `/session`, `/wd/hub/*`, `/webdriver` |
| a container's exposed port | docker-compose `ports:` in the handout |
| a process in the source | `chromedriver`,`geckodriver`,`selenium` spawn |
| a separate "bot" or "admin" service | its own container/port in compose |
| `X-Powered-By` / banner | `WebDriver`, `Selenium` |

## The bot's hiding places

| Place | Signal |
|---|---|
| `bot.js`,`admin.py`,`visit.js` in the handout | the bot source itself |
| a "report" form/endpoint | the submission that triggers it |
| a docker-compose service named `bot`/`admin`/`browser` | the bot container |
| a puppeteer/playwright/selenium import in source | the bot's driver |
| the challenge description | "the admin will check your submission" |

## The white-box reads

In a supplied handout, the fastest detection is the source:

- `grep` for `webdriver`, `puppeteer`, `playwright`, `chromedriver`
- find the bot script — read its URL, cookie, wait, flags
- find the driver spawn — the port it listens on, the flags
- find where `POST /session` or a driver client is created

The bot source is both the detection and the reproduction spec — one
read answers two questions.

## The black-box reads

Without source, detect by observation:

- the report flow ("admin will visit") implies a bot
- a port scan (within scope) for the driver ports
- response headers that betray a driver/Grid (`via`,`X-Selenium`)
- a `POST /session` probe on the likely ports — the direct test

## The surface-to-action map

| Found | Next |
|---|---|
| driver port answering | attack surface -> `attack-surface.md` |
| bot source | reproduce -> `local-bot.md` |
| bot flow, no source | reproduce from observation -> `local-bot.md` |
| Grid | `grid-remote.md` |
| CDP port | `cdp.md` |
| nothing | the class is dead — record the kill state |
