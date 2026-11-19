# Chrome flags — what each does and when the bot sets it

## The reproduction-critical flags

| Flag | Effect | Reproduce when |
|---|---|---|
| `--headless` / `--headless=new` | no window, old vs new headless impl | always — and match old/new to the bot |
| `--no-sandbox` | drop the sandbox (needed as root in container) | inside Docker, almost always |
| `--disable-gpu` | no GPU | containers, almost always |
| `--disable-dev-shm-usage` | use /tmp not /dev/shm | small /dev/shm containers |
| `--user-agent=X` | override UA | the bot spoofs a specific UA |
| `--window-size=WxH` | viewport | affects layout-based payloads |

## The behaviour-changing flags

| Flag | Effect | Reproduce when |
|---|---|---|
| `--disable-web-security` | no same-origin policy | the challenge intends cross-origin reads |
| `--allow-running-insecure-content` | mixed content allowed | the payload needs http:// on an https:// page |
| `--ignore-certificate-errors` | accept self-signed/bad certs | the challenge uses a self-signed cert |
| `--disable-blink-features=AutomationControlled` | hide `navigator.webdriver` | the bot hides automation |
| `--disable-features=X` | turn off a named feature | the bot's source names one |
| `--proxy-server=X` | route through a proxy | the bot's traffic is proxied |

## The detection/stealth flags

| Flag | Effect |
|---|---|
| `--disable-blink-features=AutomationControlled` | `navigator.webdriver` stays `undefined` |
| `--user-agent` | removes `HeadlessChrome` from the UA |
| `--lang=X` | sets `navigator.language` |

## Reading the flags from the bot's source

The bot's launch line is the spec — copy it verbatim:

```javascript
// puppeteer
puppeteer.launch({args: ['--no-sandbox','--disable-gpu','--disable-dev-shm-usage']})
// playwright
chromium.launch({args: [...]})
// selenium
options.add_argument('--no-sandbox')
```

Then set the same `args` array in your local driver. A flag the bot
sets that you do not, or vice versa, is a reproduction mismatch.

## The version flags

`--headless` (old) and `--headless=new` are different implementations —
the old is a separate code path, the new is the full browser. The
challenge's bot specifies which; matching the *wrong* headless mode is
a common reproduction mismatch that changes rendering and timing.

## Flags that break things locally

| Flag | Breaks |
|---|---|
| `--disable-web-security` | some local setups refuse it with other flags |
| `--single-process` | unstable, avoid unless the bot uses it |
| `--remote-debugging-port` | opens a second control channel — different from WebDriver |

Only set the flags the bot actually sets — each extra flag is a
divergence from the reproduction.

## The capability vs flag distinction

In WebDriver the flags go inside `goog:chromeOptions.args`; the
browser binary goes in `binary`. A flag passed at the wrong level
(session capability vs launch arg) is silently ignored — verify it
took effect by reading `chrome://version` via `execute` when it
matters.
