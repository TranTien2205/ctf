# Troubleshoot scenarios — the failure, the diagnosis, the fix

## Scenario: "session not created"

**Symptom**: `POST /session` returns an error, no `sessionId`.

| Error text | Diagnosis | Fix |
|---|---|---|
| `This version of ChromeDriver only supports version N` | driver/browser version mismatch | match `chromedriver --version` to browser major |
| `chrome not reachable` / `no such binary` | browser binary missing | set `binary`/`binary_location` |
| `DevToolsActivePort` | container needs flags | `--no-sandbox --disable-dev-shm-usage --headless` |
| `No matching capabilities` | capability set unsatisfiable | relax or match the stereotype |
| `unauthorized`/`401` | endpoint gated | auth bypass first |
| hangs (no response) | a leaked session holds the driver | `GET /sessions` -> DELETE, or `pkill` |

## Scenario: "payload fires locally, dead at the bot"

**Symptom**: local bot runs it clean; live bot reports nothing.

1. **reproduction mismatch** — re-derive URL/cookie/wait/flags/version;
   a divergence on any = a different bot
2. **channel dead** — `goto` your tunnel inside the driver; interstitial/
   refused = the channel, not the payload
3. **context wrong** — the bot's page differs (auth, frame); test on the
   same DOM
4. **timing** — payload needs more than the bot's wait; measure vs `wait`
5. **not a browser** — JS canary to the "bot"; a bare fetch is `../web-ssrf/`

## Scenario: "`file://` read returns an error page"

| Observation | Diagnosis | Fix |
|---|---|---|
| `net::ERR_INVALID_URL`/`ERR_BLOCKED` | scheme blocked at driver | `execute` `fetch("file://")` — JS primitive |
| `ERR_FILE_NOT_FOUND` | the path is wrong | try `/etc/passwd` — distinguishes "no file" from "no read" |
| a Chrome error page rendering | nav blocked | `execute`/`fetch` form |
| empty body | file empty or binary | try a text canary; binary -> base64 `execute` |

## Scenario: "`execute` returns a permissions error"

- the endpoint allows navigation but gates script — navigation reads
  (`file://`, `localhost`, `source`, `screenshot`) still live
- `execute/async` may be allowed where sync is gated — try it
- CDP `Runtime.evaluate` on `9222` is a separate primitive — try it
- some drivers gate `execute` behind a capability — read the error

## Scenario: "the exfil never reaches the listener"

| Signal | Diagnosis | Fix |
|---|---|---|
| `REQ` logged, listener silent | tunnel unreachable/interstitial | `goto` own tunnel inside driver; a tunnel without a confirm page |
| `requestfailed` `RESP:0` | egress filtered / CSP | same-origin write-back; img/script subresource |
| no `REQ` at all | the exfil branch never ran | the payload's logic — read the console |
| `ERR_SSL` | cert rejected | `--ignore-certificate-errors` or http:// |
| beacon/Image works, fetch doesn't | `connect-src` blocks fetch | the subresource channel |

## Scenario: "local reproduction won't match live"

| Divergence | Fix |
|---|---|
| different DOM/context | the bot's URL/auth/frame — re-derive |
| cookie missing | `add_cookie` exact name/domain/path/flags |
| payload needs more wait | shorten the async chain; beacon/Image |
| version behaviour differs | pin the bot's browser version |
| headless fingerprint differs | match the bot's automation flags |

## Scenario: "the whole thing hangs"

- `goto` hangs -> `pageLoadStrategy=eager`/`none`, or a `pageLoad` timeout
- `execute/async` never returns -> the callback never fired; add a
  `setTimeout` fallback inside the script
- the browser hangs -> a payload crashed the renderer; kill + recreate,
  `--disable-dev-shm-usage`
- `file://` crawl hangs -> bounded `pageLoad`; target the path directly

## The diagnosis-first rule

Each scenario's symptom routes to a *diagnosis* before a fix — the
four channels (console/error/network/DOM) name the failing stage, and
the fix is for that stage, not a blanket retry.
