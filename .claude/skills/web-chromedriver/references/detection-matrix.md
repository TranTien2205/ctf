# Detection matrix — signal x use, the decision grid

## The endpoint-exposure matrix

| Probe | sessionId | Refused | Error |
|---|---|---|---|
| `:9515` POST /session | bare driver exposed | no driver on 9515 | config/auth gate |
| `:4444` POST /session | Grid node | no Grid | Grid capability/auth |
| `/wd/hub/session` | Grid3-style endpoint | not a Grid3 | — |
| `/session` (app path) | app-proxied driver | not proxied | — |
| `:9222` GET /json | CDP exposed | no CDP | — |

Any `sessionId` -> the attack surface is live. All refused -> dead.

## The bot-flow matrix

| Signal | Debugging aid applies |
|---|---|
| "report to admin" / "admin will visit" | yes — a bot visits |
| supplied bot script | yes — reproduce it exactly |
| flag needs a state only a renderer makes | yes — payload must run in a browser |
| "bot" is a server fetch, no JS/cookies | NO — this is `../web-ssrf/` |

## The primitive matrix

| Primitive | Probe | Live if |
|---|---|---|
| file read | nav `file:///etc/passwd` | source carries the file |
| JS read | `execute` `return 1+1` | returns 2 |
| loopback | nav `localhost/admin` | source differs from external |
| cookie jar | `GET /cookies` | returns the jar |
| DOM | `GET /source` | returns the rendered tree |
| screenshot | `GET /screenshot` | returns non-blank PNG |
| CDP | `GET /json` on 9222 | returns target list |

## The reproduction-fidelity matrix

| Property | From bot source | From observation | Assumed |
|---|---|---|---|
| URL it visits | the goto arg | your submission | your URL |
| credential | the cookie/login it sets | — | a flag cookie |
| wait | the setTimeout/wait_for | the response delay | 5 s |
| flags | the args array | headers/behaviour | `--headless --no-sandbox` |

The "Assumed" column is the risk — record it, and treat a locally-
confirmed payload on assumed properties as weaker.

## The decision grid

```
POST /session answers?     --yes--> attack surface -> primitive matrix
                             --no--+
admin bot + payload?         --yes--> debugging aid -> reproduction
                             --no--> class dead (record why)
```

The two questions run in parallel — a challenge can offer both, and
the surface use is tested first because it is the cheaper read.
