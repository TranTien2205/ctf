# Glossary deep — the terms, with their precise semantics

| Term | Precise meaning |
|---|---|
| WebDriver | W3C-standard HTTP+JSON remote-control protocol for a browser; the portable API |
| session | a WebDriver browsing context leased by `POST /session`; owns a browser process |
| sessionId | the opaque id `POST /session` returns; addresses the session in every command |
| capability | a key in the session-create JSON selecting browser/options — `browserName`, `goog:chromeOptions` |
| `goog:chromeOptions` | Chrome's vendor capability — `args` (flags), `binary` (binary path), `prefs`, `debuggerAddress` |
| alwaysMatch | the capabilities object applied to every session-create |
| firstMatch | a list of alternative capability sets the driver may satisfy |
| chromedriver | the WebDriver binary for Chrome/Chromium; default port `9515` |
| geckodriver | the WebDriver binary for Firefox; speaks Marionette internally |
| Selenium | the reference WebDriver client library (Python/Java/C#/JS) |
| Playwright | a browser-control library with built-in console/network observability |
| Puppeteer | a Node browser-control library speaking CDP natively |
| Grid | Selenium's session-routing hub on `:4444`; fans out to browser nodes |
| node | a browser instance a Grid routes sessions to, selected by capability |
| CDP | Chrome DevTools Protocol — the native, richer protocol, port `9222` |
| `webSocketDebuggerUrl` | the ws:// endpoint a CDP target exposes for attach |
| headless | a browser running without a window; `--headless` (old impl) or `--headless=new` |
| admin bot | a challenge's headless browser that visits user-supplied URLs holding a flag/session |
| blind channel | the live bot — accepts your URL, returns no console/error/DOM |
| reproduction | a local bot matching the challenge's bot on URL, cookie, wait, flags, version |
| canary | a minimal payload proving JS execution before the real payload |
| exfil | the request carrying the flag off the page to your listener |
| interstitial | a confirm page a tunnel inserts before your URL — breaks headless clients |
| write-back | stashing the flag on the app's own origin to read back, when egress is blocked |
| `file://` | the URL scheme a browser navigates to a local file — the read primitive |
| `HttpOnly` | a cookie attribute hiding it from `document.cookie` (jar-readable via `GET /cookies`) |
| `SameSite` | cookie attribute controlling cross-site sending — `Strict` drops it on cross-site nav |
| `navigator.webdriver` | `true` in a driven browser — the automation tell |
| `sendBeacon` | `navigator.sendBeacon` — fire-and-forget request surviving navigation |
| `pageLoadStrategy` | capability: `normal`/`eager`/`none` — when `goto` returns |
| `execute/sync` | WebDriver command running JS, returning its `return` value serialised |
| `execute/async` | WebDriver command running JS, blocking until its last-arg callback fires |
| stale element | an element reference invalidated by DOM mutation — throws on use |
| current frame | the document `execute`/`source`/`element` operate on — top unless switched |
| candidate | a flag-shaped string not yet gated by `pre-flag` |
| development evidence | local-bot signals — prove the reproduction, not the target |
| impact evidence | live exfil / `file://` `source` — the only flag proof |
| kill map | the measured dead-end record, each cell with a re-open condition |
