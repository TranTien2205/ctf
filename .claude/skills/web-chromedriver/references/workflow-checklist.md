# Workflow checklist — the ordered run-down

## Phase 0: setup

- [ ] scope confirmed — the driver/bot is part of the challenge
- [ ] `which chromedriver` + version check
- [ ] use classified: attack surface vs debugging aid

## Phase 1: detection

- [ ] handout grepped for `webdriver|chromedriver|bot|puppeteer|playwright`
- [ ] `POST /session` probed on `:9515`/`:4444`/proxied route
- [ ] `GET :9222/json` probed for CDP
- [ ] bot flow located (report form / admin visit)

## Phase 2a: attack surface

- [ ] `POST /session` -> `sessionId`
- [ ] `file:///etc/passwd` + `source` — file read live?
- [ ] `execute return 1+1` — JS live?
- [ ] `localhost/*` + `source` — loopback live?
- [ ] `GET /cookies` — jar readable?
- [ ] flag's surface located
- [ ] flag read through the live primitive

## Phase 2b: debugging aid

- [ ] bot spec extracted (URL/cookie/wait/flags/version)
- [ ] local driver, same flags + version
- [ ] cookie set, navigate, wait — page matches live?
- [ ] four hooks on (console/pageerror/request/requestfailed)
- [ ] canary -> execution confirmed
- [ ] full payload fires locally
- [ ] exfil channel checked from inside the driver

## Phase 3: fire + confirm

- [ ] live bot fired once (aid) / flag in hand (surface)
- [ ] `tools/hooks.py pre-flag` the candidate
- [ ] flag confirmed

## Phase 4: close

- [ ] every session `DELETE`d
- [ ] local drivers killed
- [ ] working payload + channel recorded
- [ ] dead cells in the kill map with re-open conditions

## If stalled

- [ ] reproduction? -> re-derive properties
- [ ] context? -> `../web-xss/`
- [ ] channel? -> `evasion.md`
- [ ] read blocked? -> `execute`/`localhost`/CDP alternates
- [ ] layer spent? -> `tools/decide.py` -> escalate
