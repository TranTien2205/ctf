# Per-boundary — which neighbour class owns which question

## The flag-in-a-file question

- **Here**: the WebDriver endpoint is the *vehicle* — `file://` nav or
  `execute` `fetch("file://")` is the read primitive.
- **`../file-read-primitives/`**: owns *what* to read — source paths,
  flag location, config, escalation. Once the read works, route there.

Boundary: the primitive is here; the read strategy is file-read-primitives.

## The internal-route question

- **Here**: the browser reaching `localhost` is a position — its origin.
- **`../web-ssrf/`**: owns server-side fetches the app makes. A bot that
  is actually a `curl`-like server fetch is SSRF, not a browser — the
  tell is whether JS/DOM/cookies exist in the "visitor" (browser = this
  skill, bare fetch = SSRF).

Boundary: JS+DOM+cookies = browser (here); bare HTTP client = SSRF.

## The payload-context question

- **Here**: driving the browser to *test* the payload.
- **`../web-xss/`**: owns *which* payload — context discovery, sink
  selection, sanitiser bypass, the injection itself.

Boundary: "how do I run it" = here; "what is it" = web-xss.

## The bot-as-CSRF question

- **Here**: reproducing the bot to debug.
- **`../web-csrf/`**: owns the forged state-change the bot's session
  performs — the mechanism is the request, not the browser.

Boundary: debugging harness = here; the state-change mechanism = CSRF.

## The auth/Grid question

- **Here**: an open endpoint is the capability.
- **`../web-auth-session/`**: owns bypassing auth that gates the driver
  — a token, a login, a Grid credential.

Boundary: open endpoint = here; gated endpoint's auth = auth-session.

## The CDP vs WebDriver boundary

- **Here**: WebDriver (`9515`) is the portable command set.
- **CDP (`9222`)**: still this skill — a richer API on the same
  browser-control class, not a different class.

## The "is it a bot at all" boundary

- **Here**: a real headless browser.
- **`../web-ssrf/` or `../file-read-primitives/`**: a server-side fetch
  or a proxy that only *looks* like a bot.

The discriminator: does the "visitor" run JavaScript, hold cookies,
and render? A headless browser does all three; a `curl`/`requests`
fetch does none. Confirm with a JS-execution canary before assuming
the browser class.

## The decision table

| You observe | Class |
|---|---|
| `POST /session` answers | here (attack surface) |
| admin bot + your payload | here (debug aid) -> web-xss for the payload |
| `file://` read works | here -> file-read-primitives for targets |
| a server-side URL fetch | web-ssrf, not here |
| a forged request mechanism | web-csrf, not here |
| auth gates the endpoint | web-auth-session first |
