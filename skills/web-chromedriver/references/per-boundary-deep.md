# Per-boundary deep — the class edges, justified

## vs web-xss — the harness, not the payload

`web-chromedriver` drives the browser the XSS payload *runs in*; it
does not construct or classify the payload. The boundary:

- "which context does the value land in / which sink / which bypass" -> `../web-xss/`
- "did my payload fire in a real renderer / did the exfil leave" -> here

The skill is the *test harness* and the *read primitive* — the
vulnerability class lives in `web-xss`. Conflating them leads to
debugging the injection here when the bug is a context problem there.

## vs web-ssrf — the browser, not the fetch

Both reach internal surfaces (`localhost`, `file://`). The boundary is
the mechanism:

- **webdriver**: a *browser* — runs JS, holds cookies, renders
- **ssrf**: a *bare HTTP client* — the app's fetch, no JS/DOM/cookies

The discriminator: send a JS-execution canary. A browser runs it; a
`curl`-like fetch does not. A "bot" that is actually a server-side
fetch is `../web-ssrf/`, not this class.

## vs file-read-primitives — the primitive, not the strategy

The `file://` navigation is *one* file-read primitive.
`../file-read-primitives/` owns the *read strategy* — which paths, the
flag-location hunt, the escalation to execution.

- **here**: the WebDriver-specific `file://`/`execute`-file read
- **there**: LFI, XXE, path params, and *what to read next*

Once the read works, route to file-read-primitives for the read plan.

## vs web-csrf — the harness, not the forged request

A bot-delivered state change is `../web-csrf/`'s mechanism — the forged
request the bot's session performs. This skill reproduces the bot to
*debug*; the CSRF class covers the state-change mechanism itself.

- **here**: reproduce/drive the bot
- **there**: the forged-request mechanism and its protection bypasses

## vs web-auth-session — the gate, not the driver

A token-gated Grid or an auth-walled driver endpoint routes the *auth
bypass* to `../web-auth-session/` — the WebDriver surface opens only
after the auth does.

- **here**: the open endpoint's capability
- **there**: bypassing the auth that gates it

## vs CDP — same class, richer API

CDP (`9222`) is *not* a different class — it is a richer API on the
same browser-control surface. WebDriver is the portable command set;
CDP is the native deeper one. Both are this skill.

## The routing rule

`web-chromedriver` is the *browser-control layer*. Stay while the
question is "drive a real browser"; leave when the question is a
payload class (`web-xss`), a different primitive (`web-ssrf`,
`file-read-primitives`), or an auth gate (`web-auth-session`).
