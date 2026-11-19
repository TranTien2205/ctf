# Troubleshoot — the failure modes and the fix for each

## The driver will not start / session will not create

| Symptom | Cause | Fix |
|---|---|---|
| `session not created: Chrome version` | driver/browser major-version mismatch | match `chromedriver --version` to `chrome --version` major |
| `chrome not reachable` | no browser binary | set `binary` / `binary_location` |
| `DevToolsActivePort` error | missing flags in container | add `--no-sandbox --disable-dev-shm-usage --headless` |
| hangs on session create | a leaked prior session holds the port | `pkill chromedriver` / delete leaked sessions |
| `unknown error` on Linux container | `/dev/shm` too small | `--disable-dev-shm-usage` |

## The local bot does not match the live one

| Symptom | Cause | Fix |
|---|---|---|
| payload fires locally, dead at bot | reproduction mismatch | re-derive flags/wait/cookie/context from the bot source |
| page renders differently | wrong URL, wrong route, missing auth | navigate to the exact URL the bot visits, set its cookie |
| payload needs longer than the wait | bot's `setTimeout` too short | shorten the payload's async chain to fit the wait |
| cookie-based flag missing locally | you did not set the bot's cookie | `add_cookie` with the same name/domain/path as the bot |

## The exfil does not leave

| Symptom | Cause | Fix |
|---|---|---|
| `REQ` to tunnel, no listener hit | tunnel unreachable / interstitial | fetch your own URL from inside the driver first |
| `RESP: 0` | CSP blocks the origin | use an allowed origin/scheme, or a same-origin channel |
| `net::ERR_SSL` | cert the browser rejects | `--ignore-certificate-errors` or an http:// listener |
| fetch never issued | the exfil branch did not run | the payload's logic, not the channel — read the console |

## The injected error hook returns nothing

`window.__e` empty after the payload -> the hook was set on the wrong
frame, or the payload ran in a different context than your hook's
frame. Re-inject the hook into the same document/frame the payload
lands in (`switch_to.frame` / `frame.evaluate` for Playwright).

## The `file://` read returns an error

| Observation | Fix |
|---|---|
| navigation to `file://` errors | the endpoint blocks `file://` — try `execute` `fetch("file:///...")`, or accept the class is dead here |
| `source` returns a Chrome error page | the path does not exist or is unreadable — try a known path (`/etc/passwd`) to distinguish "no file" from "no read" |
| source is empty | the file read works but the file is empty or binary — try a text path first |
| only the challenge root reads | the driver is sandboxed to a dir — enumerate the readable root |

## Timeout / hang

- `page.goto` hangs -> the page never reaches `load`; use
  `wait_until="domcontentloaded"` or a shorter `page_load_timeout`
- `execute_async` never returns -> the callback was never invoked;
  add a `setTimeout` fallback in the script
- the whole browser hangs -> a payload crashed the renderer; kill and
  recreate the session, add `--disable-dev-shm-usage`

## The screenshot is blank

`--headless` old mode sometimes renders nothing — use `--headless=new`,
or the screenshot captures before the payload paints; add a wait.

## The driver exists but the challenge's version differs

The challenge's bot may run an old Chromium with different behaviour
(an old headless mode, a different sanitiser timing). When local and
live diverge and the reproduction is otherwise faithful, the browser
*version* is the next suspect — read the bot's `package.json`/Docker
`FROM` for the pinned version and match it.
