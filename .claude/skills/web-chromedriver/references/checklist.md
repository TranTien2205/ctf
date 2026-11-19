# Checklist — the run-down, in order

## Before anything

- [ ] in scope — the driver/bot is part of the challenge
- [ ] `which chromedriver` — local driver exists
- [ ] decide the use: attack surface vs debugging aid

## Attack surface

- [ ] `POST /session` answers -> `sessionId`
- [ ] `nav file:///etc/passwd` + `source` — file read live?
- [ ] `execute return 1+1` — JS live?
- [ ] `nav localhost/*` — loopback surface?
- [ ] `GET /cookies` — jar readable?
- [ ] locate the flag's surface
- [ ] read it through the live primitive
- [ ] `pre-flag` the candidate
- [ ] `DELETE` the session

## Debugging aid

- [ ] read the bot source -> URL, cookie, wait, flags
- [ ] local driver with the same flags + browser version
- [ ] set the cookie, navigate to the same URL, wait the same time
- [ ] four hooks on: console, pageerror, request, response
- [ ] canary -> does it execute?
- [ ] iterate until the full payload fires locally
- [ ] check the exfil channel from inside the driver
- [ ] fire at the live bot once
- [ ] listener carries the flag-shaped value
- [ ] `pre-flag` the candidate

## Always

- [ ] `DELETE` every session created
- [ ] record dead ends in the kill map with re-open conditions
- [ ] distinguish development evidence from a flag
- [ ] record which reproduction properties are assumptions

## If stalled

- [ ] reproduction mismatch? -> re-derive the bot's properties
- [ ] channel dead? -> tunnel/CDN/alternate channel check
- [ ] context wrong? -> route to `../web-xss/`
- [ ] mechanism layer spent? -> `tools/decide.py` -> escalate
