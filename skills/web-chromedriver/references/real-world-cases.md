# Real-world cases — the patterns as they appear in CTF

## The "report to admin" pattern

The most common shape: a form or endpoint where you submit a URL or a
note, and "the admin will review it". A headless bot visits your URL
holding a flag cookie or an admin session. The skill's role: reproduce
the bot locally, develop the exfil payload, fire once.

- **signal**: a report/flag/contact form that mentions admin review
- **the bot's spec**: usually a supplied `bot.js`/`admin.py` or a
  compose service named `bot`
- **the flag**: the bot's cookie or a same-origin flag page

## The exposed Selenium/ChromeDriver port

A challenge (or a real pentest) leaves a driver port open — `9515`,
`4444`, `9222`. The skill's role: the file-read and loopback pivot.

- **signal**: a high port answering `POST /session` or `GET /json`
- **the reach**: `file://` read, `localhost` routes, the cookie jar
- **the flag**: a file, an internal route, a cookie

## The bot that renders a flag page

A challenge where the bot visits a page that renders the flag — a
screenshot or a DOM read of the bot's page carries it.

- **signal**: the bot renders something only it can see
- **the reach**: `GET /screenshot` or `source` of the bot's view
- **the flag**: in the rendered output

## The admin-bot CSRF chain

A bot that performs an action when it visits your URL — a like, a
flag-submit, a state change. The payload triggers the action in the
bot's authenticated context. Overlaps `../web-csrf/` for the mechanism;
this skill supplies the reproduction.

- **signal**: the bot performs a state change on visit
- **the reproduction**: the bot's auth + the action endpoint
- **the flag**: the state change's result

## The headless-vs-real-bot trap

A challenge that treats a real headless bot differently — it checks
`navigator.webdriver`, runs different logic for "is a bot". The
reproduction must match the bot's flags so the payload faces the same
environment.

- **signal**: the app behaves differently for the bot's visits
- **the read**: `navigator.webdriver` and the fingerprint from inside
- **the fix**: match the bot's automation flags

## The pattern-to-skill map

| Pattern | Skill's role |
|---|---|
| report-to-admin | local reproduction + exfil |
| exposed driver port | file-read + loopback capability |
| bot renders flag | screenshot/source of the bot's view |
| bot does an action | reproduction + `../web-csrf/` |
| headless-checked bot | match automation flags |

Each is a real CTF shape; the skill's corpus covers the browser-
control layer each needs.
