# Preconditions — what must be true before this skill applies

## For the debugging-aid use

- the challenge has an admin bot / report flow that visits your URL
- the payload is client-side (runs in a browser — XSS, DOM, template)
- a local driver exists (`which chromedriver`) or can be installed
- the bot's properties can be read (source) or observed (behaviour)

Without a bot flow or a client-side payload, the debugging use does not
apply — the class is the payload's (`../web-xss/`), and this skill only
provides the test harness.

## For the attack-surface use

- a WebDriver/Grid/CDP endpoint answers `POST /session` (or `GET /json`)
- the session can be created without auth you cannot pass
- a primitive it exposes is live (nav, execute, cookies, screenshot)

Without an answering endpoint, the surface use is dead — the falsifier
is a refused `POST /session` on every plausible port/route.

## For either use

- the challenge is in scope (the driver/bot is part of the target)
- a flag path exists that the browser's reach covers (file, route,
  cookie, DOM, render)
- the payload's work fits the bot's wait / the session's timeouts

## The honest gaps

- **a closed remote app with no bot source** — reproduction is part
  guessing; the confirmed payload is weaker. Record the assumptions.
- **the flag needs the live bot's credential** — local development
  proves the payload *shape*; the live fire is the only exfil test.
- **no local driver and no exposed endpoint** — the skill has nothing
  to drive; install a driver or pivot to a non-browser class.

## The check

```bash
which chromedriver && chromedriver --version    # local driver exists?
curl -s -m5 -X POST http://T:9515/session -d '{...}'  # endpoint answers?
# a report/admin flow in the app?               # bot exists?
```

Three checks answer whether either use applies before the first probe.
