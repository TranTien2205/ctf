# Workflow checklist deep — the run, itemised

## Phase 0: scope and setup

- [ ] the driver/bot is inside the supplied challenge scope
- [ ] `which chromedriver` — a local driver exists
- [ ] `chromedriver --version` matches the browser's major version
- [ ] the use is classified: attack surface, debugging aid, or both
- [ ] the flag's expected carrier is noted (cookie/file/route/DOM/render)

## Phase 1: detection

- [ ] handout grepped: `webdriver|chromedriver|geckodriver|selenium|
      webdriverio|puppeteer|playwright|headless|remote-debugging|bot|admin`
- [ ] a bot script found -> its URL/cookie/wait/flags/version extracted
- [ ] `POST /session` probed on `:9515` — `sessionId`?
- [ ] `POST /session` probed on `:4444` — Grid?
- [ ] `POST /session` probed on the app port / `/wd/hub` — proxied?
- [ ] `GET :9222/json` probed — CDP targets?
- [ ] `GET :4444/status` probed — Grid node inventory?
- [ ] a bot flow located (report form / admin visit / stored field)

## Phase 2a: attack surface — primitive map

- [ ] `file:///etc/passwd` + `source` -> `root:x:0:0`? (file read)
- [ ] `execute/sync` `return 1+1` -> `2`? (JS)
- [ ] `execute` `fetch("file:///etc/passwd")` -> file text? (JS file read)
- [ ] `localhost/{admin,debug,api}` + `source` -> internal content? (loopback)
- [ ] `GET /cookies` -> cookie list? (jar)
- [ ] `GET /screenshot` -> non-blank PNG? (render)
- [ ] flag's surface located (file/route/cookie/storage/DOM/render)

## Phase 2b: debugging aid — reproduction

- [ ] bot spec extracted into a table (URL/credential/wait/flags/version)
- [ ] local driver launched with the spec's flags + version
- [ ] the credential set (`add_cookie` exact name/domain/path/flags)
- [ ] navigated to the spec's URL, waited the spec's wait
- [ ] `page.content()` verified vs the live view on the DOM axes
- [ ] assumed properties recorded as assumptions

## Phase 3a: attack surface — the read

- [ ] the flag read through the matching live primitive
- [ ] the proving bytes saved (`source`/`cookies`/`screenshot`/`execute` body)
- [ ] `tools/hooks.py pre-flag` the candidate
- [ ] `DELETE` the session

## Phase 3b: debugging aid — the development loop

- [ ] four hooks on: `console`, `pageerror`, `request`, `requestfailed`
- [ ] canary fired -> execution confirmed (`console.log` marker)
- [ ] staged markers -> each payload stage located
- [ ] the context dumped (url/origin/frame/cookie/storage)
- [ ] the full payload fires cleanly in the reproduction
- [ ] the exfil channel checked from inside the driver (own tunnel -> your body?)
- [ ] the payload's time measured vs the bot's wait
- [ ] the confirmed payload fired at the live bot once
- [ ] the listener captured the flag-shaped value
- [ ] `tools/hooks.py pre-flag` the candidate
- [ ] `DELETE` every session; drivers killed

## Phase 4: close

- [ ] the working payload + channel recorded in the notes
- [ ] every dead end recorded in the kill map with its re-open
- [ ] development vs impact evidence distinguished in the record
- [ ] the assumed reproduction properties listed

## The stall checklist

- [ ] reproduction? -> re-derive each property; the version
- [ ] context? -> `../web-xss/` for the injection class
- [ ] channel? -> `evasion.md` / `evasion-scenarios.md`
- [ ] read blocked? -> `execute`/`localhost`/CDP alternates
- [ ] not a browser? -> `../web-ssrf/` for the fetch class
- [ ] auth gate? -> `../web-auth-session/` first
- [ ] mechanism layer spent? -> `tools/decide.py` -> escalate rung
- [ ] class dead? -> record the compound kill state
