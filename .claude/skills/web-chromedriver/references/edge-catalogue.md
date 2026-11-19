# Edge catalogue — the unusual states, indexed

## Authentication and session edges

| Edge | What breaks | The fix |
|---|---|---|
| bot pre-authenticates | payload tested on anonymous page, bot sees authed page | reproduce the login/`add_cookie` before the payload |
| flag cookie HttpOnly | `document.cookie` can't see it | `GET /cookies` jar, or same-origin ride |
| flag cookie SameSite=Strict | dropped on cross-origin nav | payload must run on the same site |
| Grid requires a token | `POST /session` 401 | auth bypass -> `../web-auth-session/` |
| endpoint serialises sessions | second `POST /session` queues/fails | clean leaked sessions; one at a time |

## Context and frame edges

| Edge | What breaks | The fix |
|---|---|---|
| payload in an iframe | top-frame `execute`/hooks miss it | `switch_to.frame`/`page.frame` into it |
| cross-origin iframe | payload can't read top's DOM | exfil via cookie/top.nav, not DOM read |
| bot navigates away | payload destroyed mid-run | fire-and-forget exfil; same-origin write |
| multiple bot pages | payload context changes per page | reproduce the full visit sequence |
| a `window.open` popup | new context, separate frame tree | track the popup handle |

## Environment edges

| Edge | What breaks | The fix |
|---|---|---|
| driver != app host (Grid node) | `localhost`/`file://` are the NODE's | reads land on the node's fs/network |
| old Chromium | different headless mode/CSP/JS | match the pinned version |
| `--disable-web-security` bot | cross-origin reads work locally | only if the bot sets it — an axis |
| container `/dev/shm` too small | driver crashes under load | `--disable-dev-shm-usage` |
| version mismatch | session won't create | match `chromedriver` to browser major |

## Read and render edges

| Edge | What breaks | The fix |
|---|---|---|
| file is binary | `file://` renders mojibake/download | `execute` `fetch` + base64 |
| file is huge | `source` hangs | read a small canary first, target the path |
| flag is an image | text `source` misses it | `GET /screenshot` |
| page renders blank | old `--headless` mode | use `--headless=new` |
| read lands on wrong page | redirect/frame | `GET /url` confirms where it is |

## Channel edges

| Edge | What breaks | The fix |
|---|---|---|
| tunnel interstitial | fetch returns confirm HTML | a tunnel without it; check from inside |
| egress filter | `REQ` leaves, `RESP:0`/no listener | same-origin write-back |
| CSP blocks connect-src | `fetch` refused | img/script subresource |
| CSP blocks all | nothing leaves | write-back, or the app is the channel |
| TLS/SNI filtered | `ERR_SSL` | an http:// listener or allowed host |

## The edge-to-module map

| Edge kind | Module |
|---|---|
| auth/session | `local-bot.md`, `edge-cases.md` |
| context/frame | `multi-page.md`, `observability.md` |
| environment | `troubleshoot.md`, `local-bot-deep.md` |
| read/render | `attack-surface-deep.md`, `troubleshoot-deep.md` |
| channel | `evasion.md`, `evasion-deep.md` |
