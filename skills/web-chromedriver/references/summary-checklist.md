# Summary checklist — the one-page run-down

## Which use?

- [ ] `POST /session` answers -> attack surface
- [ ] a bot flow exists -> debugging aid
- [ ] neither -> class dead

## The commands (always close the session)

```bash
POST   /session            -> sessionId
POST   .../url             -> navigate (file://, localhost)
GET    .../source          -> DOM / file text
POST   .../execute/sync    -> JS return value
GET    .../cookies         -> the jar (HttpOnly too)
GET    .../screenshot      -> PNG
DELETE /session/{id}       -> always
```

## Attack surface — the reads

- [ ] `file:///etc/passwd` + `source` -> canary proves the read
- [ ] `file:///flag` or `/proc/self/environ` -> the flag
- [ ] `execute return 1+1` -> JS live?
- [ ] `localhost/*` + `source` -> internal route?
- [ ] `GET /cookies` -> flag cookie (HttpOnly)?
- [ ] `execute` `localStorage`/`fetch("/flag")` -> storage/origin flag?
- [ ] `GET /screenshot` -> rendered flag?

## Debugging aid — the loop

- [ ] bot spec extracted (URL/cookie/wait/flags/version)
- [ ] local driver + same flags/version -> faithful reproduction
- [ ] four hooks on: console/pageerror/request/requestfailed
- [ ] canary -> exec confirmed
- [ ] staged markers -> payload iterates to confirmed
- [ ] channel checked from inside the driver (own tunnel -> your body?)
- [ ] payload fits the bot's wait
- [ ] fire live once -> listener -> `pre-flag`

## The reads by flag location

| Flag is | Read |
|---|---|
| a file | `file://` nav + `source` |
| a cookie | `GET /cookies` / `execute` `document.cookie` |
| storage | `execute` `localStorage` |
| a route | `localhost` nav + `source` |
| a page | `execute` `fetch` or `source` |
| rendered | `GET /screenshot` |
| exfil'd | the listener / a write-back |

## The traps

- [ ] not blind-firing at the live bot — develop locally
- [ ] reproduction copied verbatim — no guessed axes
- [ ] the DOM read, not the response body
- [ ] canary before the full payload
- [ ] channel verified from inside, not assumed
- [ ] `DELETE`d every session
- [ ] `pre-flag` gated the candidate — a marker is not the flag

## The anchors

`apexsurvive` — local-bot debugging works. `tornadoservice` — the
channel check is the skipped step.
