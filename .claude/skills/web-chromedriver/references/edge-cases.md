# Edge cases — the states that break the simple model

## The bot authenticates before visiting

Some bots log in or set a session cookie before navigating to your URL
— so the page your payload renders on is the *authenticated* view, not
the anonymous one. Reproduce the auth step: `add_cookie` or perform
the same login the bot does, then navigate. A payload tested on the
anonymous page may land in a different DOM than the bot sees.

## The flag is a cookie scoped to a path or domain

The bot's flag cookie may be `HttpOnly` (invisible to `document.cookie`
— read it via a request it rides, not JS), `SameSite=Strict` (dropped
on a cross-origin load — your payload must run on the same site), or
scoped to a path your URL does not share. Read the bot's cookie setup
and test whether your payload's context can reach it at all.

## The payload must survive a redirect or frame

A bot that navigates through a redirect, or renders your payload in an
iframe, changes the JS context — `window.top` vs the frame's `window`,
and a `fetch` relative URL resolves against the frame's origin. Test
the payload in the same frame/redirect structure the bot uses.

## The bot waits on an event, not a timer

`wait_for_selector`, `networkidle`, a promise resolution — the payload
must trigger the wait's condition, not just run within a timer. A
`networkidle` wait means every background fetch the payload makes
extends the window; a `wait_for_selector` waits for a DOM node the
payload may need to create.

## Multiple pages / the bot visits several URLs

A bot that visits your URL *then* an internal page, or visits your URL
inside a loop, changes which context the payload fires in and when.
Match the visit sequence — a payload that fires on the first page may
be destroyed by the second's navigation.

## The driver runs an old Chromium

An old headless mode (`--headless` vs `--headless=new`), a different
CSP engine, an older JS — the challenge's bot may behave differently
than your current browser. Read the pinned version from the bot's
Docker/`package.json` and match the browser version when local and
live diverge.

## The endpoint requires auth or a capability

A Selenium Grid or a managed driver may require a token, a specific
capability set, or only allow a single session. The `POST /session`
may need an auth header or a `platformName` it accepts. Read the
endpoint's error response — it usually names the missing capability.

## The file read returns binary or huge

A `file://` read of a binary or a multi-MB file can hang the source
return or mangle it. Read a small text path first to prove the
primitive; for a binary, `execute` `fetch` + base64 inside the page
and read the string back.

## The session is shared / other teams

On a shared challenge instance a leaked session from another run (or
another team) may hold the only session slot. `DELETE` your sessions
and, if the endpoint supports it, list/clean leaked ones before
starting.

## The bot's origin differs from the app's

A bot that visits `http://localhost/` while the app is on a public URL
— or vice versa — changes which origin your payload's `fetch` is
same-origin with. Confirm the bot's actual origin from its URL
handling, not the public one you see.
