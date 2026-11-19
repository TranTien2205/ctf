# Glossary — the terms this skill uses

| Term | Meaning |
|---|---|
| WebDriver | the W3C HTTP+JSON protocol for driving a browser |
| chromedriver | the WebDriver binary for Chrome/Chromium; listens on `:9515` |
| geckodriver | the WebDriver binary for Firefox |
| msedgedriver | the WebDriver binary for Edge |
| session | a WebDriver browsing context; `POST /session` creates it, `DELETE` destroys it |
| sessionId | the id returned at session creation; used in every command path |
| capabilities | the JSON a session-create sends to pick browser/options |
| `goog:chromeOptions` | Chrome's capability namespace — `args`, `binary`, `prefs` |
| Selenium | a WebDriver client library (Python/Java/etc.) |
| Playwright | a browser-control library with richer observability than WebDriver |
| Puppeteer | a Node browser-control library over CDP |
| Grid | Selenium's session-routing hub (`:4444`) — fans out to nodes |
| node | a browser instance a Grid routes sessions to |
| CDP | Chrome DevTools Protocol — richer than WebDriver, port `9222` |
| headless | a browser running without a window — `--headless`/`--headless=new` |
| admin bot | a challenge's headless browser that visits user-supplied URLs |
| blind channel | the live bot — gives no console/error/DOM feedback |
| reproduction | a local bot matching the challenge's bot on URL/cookie/wait/flags |
| canary | a minimal payload proving execution before the real payload |
| exfil | the request that carries the flag off the page to your listener |
| interstitial | a "click to continue" page a tunnel inserts — breaks headless clients |
| write-back | storing the flag in a same-origin location you read back |
| `file://` | the file-scheme URL a browser navigates to — a file read |
| `HttpOnly` | a cookie flag hiding it from `document.cookie` (readable via the jar) |
| `navigator.webdriver` | `true` in a driven browser — the automation tell |
| `--no-sandbox` | Chrome flag dropping the sandbox — needed as root in containers |
| `--disable-dev-shm-usage` | Chrome flag using /tmp for shared memory |
| `sendBeacon` | `navigator.sendBeacon` — fire-and-forget exfil surviving navigation |
| candidate | a flag-shaped string not yet gated by `pre-flag` |
| kill map | the measured dead-end record with re-open preconditions |
| development evidence | local-bot signals — prove the payload, not the target |
| impact evidence | live exfil / `file://` source — the only flag proof |
