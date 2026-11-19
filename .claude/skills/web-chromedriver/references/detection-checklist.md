# Detection checklist — run in order, stop at first live

## Endpoint detection

- [ ] read the handout for `webdriver|chromedriver|puppeteer|playwright|bot`
- [ ] `GET :9515/status` — a bare driver?
- [ ] `GET :4444/status` — a Grid?
- [ ] `POST :9515/session` — `sessionId`? -> attack surface live
- [ ] `POST :4444/session` — Grid session?
- [ ] `GET :9222/json` — CDP exposed?
- [ ] proxied `/session` or `/wd/hub/session` on the app port?

## Bot detection

- [ ] a report/admin-visit flow in the app?
- [ ] a bot script in the handout (`bot.js`,`admin.py`)?
- [ ] a `bot`/`admin`/`browser` compose service?
- [ ] a puppeteer/playwright/selenium import in source?
- [ ] challenge text mentions "admin will visit/check"?

## Primitive detection (once a session exists)

- [ ] `nav file:///etc/passwd` + `source` — file read?
- [ ] `execute return 1+1` — JS?
- [ ] `nav localhost/admin` + `source` — loopback?
- [ ] `GET /cookies` — jar readable?
- [ ] `GET /screenshot` — non-blank PNG?

## Reproduction detection

- [ ] bot source -> copy URL/cookie/wait/flags
- [ ] no source -> observe, mark assumptions
- [ ] local driver matches version/flags?
- [ ] local bot reaches the same page as live?

## Falsifier check (if nothing is live)

- [ ] all `POST /session` refused -> attack surface dead
- [ ] no bot flow AND no source -> debugging aid dead
- [ ] both dead -> class dead, record the kill state

## The one-line summary

Read source first; probe `POST /session` next; if a session exists,
test file/JS/loopback in order; if no endpoint but a bot flow exists,
reproduce it; if neither, the class is dead.
