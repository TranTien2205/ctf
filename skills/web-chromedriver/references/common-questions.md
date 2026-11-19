# Common questions — the ones that come up every time

## "The live bot fired nothing — is my payload dead?"

Not necessarily — the most common cause is the *channel*, not the
payload. Check whether a headless client can reach your tunnel at all
(`goto` your own URL from inside the driver). A tunnel interstitial
kills the exfil even when the payload fires perfectly.

## "It works locally but not at the bot — why?"

Almost always the reproduction, not the payload. Re-derive the bot's
URL, cookie, wait, and flags from its source — a divergence on any of
them is a different bot. Check the browser version too.

## "`document.cookie` is empty but the flag should be a cookie"

The cookie is probably `HttpOnly` — invisible to JS. Read the jar via
`GET /session/{id}/cookies`, or exfil it through a same-origin request
the cookie rides automatically.

## "`POST /session` is refused — is the class dead?"

At that endpoint, yes — but check the other ports/routes (`:4444`,
`/wd/hub`, `:9222` for CDP) before declaring the whole surface dead.
If all are refused, the attack-surface use is dead; the debugging-aid
use may still apply if a bot flow exists.

## "My `execute` returns a permissions error"

The endpoint allows navigation but not script — navigation-only reads
(`file://`, `localhost`, `source`, `screenshot`) still work; the
JS-in-browser primitive is dead. Some drivers gate `execute` behind a
capability — read the error.

## "The payload needs more time than the bot waits"

Shorten the async chain — use `sendBeacon`, an `Image` src, or a
same-origin write that completes before the bot navigates away. A
payload that cannot fit the wait is dead regardless of correctness.

## "How do I know it's a browser bot and not a server fetch?"

Send a JS-execution canary — a real headless browser runs it (a
`fetch`, a `document.title` change, a request to your listener); a
`curl`-style server fetch does not. The discriminator is JS + DOM +
cookies, not the "bot" label.

## "The page renders but my source read is empty/mangled"

Try the `screenshot` — a flag rendered visually may not be in the text
source. Also check whether the read landed on the right page (a
redirect, a frame) — `GET /url` confirms where the browser actually is.

## "Can I just use Playwright instead of raw curl?"

Yes — Playwright/Selenium are wrappers over the same commands. Reach
for Playwright when you want the console/network hooks built in;
reach for `curl` when no library is installed or you want the raw
protocol.

## "Is a `sessionId` proof of file read?"

No — it proves the endpoint answers, not that a read works. The read
is proven by `file://` `source` returning a file's contents.

## "The flag I exfil'd — is it the flag?"

A flag-shaped string is a *candidate* until `tools/hooks.py pre-flag`
gates it against a live response — same as every class.
