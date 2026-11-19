# Summary — the whole skill in one page

## What it is

Two uses of the same thing — a WebDriver session you control:

1. **Debugging aid** — reproduce the challenge's admin bot locally so a
   client-side payload is a normal debug loop, not a blind channel.
2. **Attack surface** — a driver/Grid/CDP endpoint the challenge exposes
   is a file-read and loopback capability.

## The decision

```
POST /session answers? --yes--> attack surface -> file/JS/loopback reads
                    \--no-> bot flow exists? --yes--> reproduce + develop
                                          \--no-> class dead
```

## The commands that matter

```bash
POST   /session                    # create -> sessionId
POST   /session/{id}/url           # navigate (file://, localhost)
GET    /session/{id}/source        # rendered DOM / file text
POST   /session/{id}/execute/sync  # JS in the page
GET    /session/{id}/cookies       # the jar (incl. HttpOnly)
GET    /session/{id}/screenshot    # PNG
DELETE /session/{id}               # always
```

## The debugging loop

```
reproduce bot -> four hooks on -> canary -> read the four channels
-> iterate until confirmed -> fire live once -> listener carries flag
```

## The reads (attack surface)

| Flag lives in | Read |
|---|---|
| a file | `file://` nav + source |
| an internal route | `localhost` nav + source |
| a cookie | `GET /cookies` (or `execute` `document.cookie`) |
| a same-origin page | `execute` `fetch` |
| rendered | `screenshot` |

## The traps

- fire blind at the live bot -> develop locally first
- wrong reproduction (flags/wait/cookie) -> copy the bot's spec
- tunnel interstitial -> check the channel from inside the driver
- leaked sessions -> always `DELETE`
- response body vs rendered DOM -> read the DOM
- `TESTFLAG` is not the flag -> live exfil through `pre-flag`

## The anchors

- `apexsurvive` — local bot debugging for a stored-XSS chain
- `tornadoservice` — the tunnel interstitial that costs bot visits

## Routing out

- payload context -> `../web-xss/`
- the "bot" is a server fetch -> `../web-ssrf/`
- a file read -> `../file-read-primitives/`
- a forged state change -> `../web-csrf/`
