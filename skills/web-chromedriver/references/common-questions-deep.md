# Common questions deep — the FAQ with the reasoning

## "Why not just fire the payload at the live bot and iterate?"

Because each iteration costs a bot visit and returns ~zero signal.
The live bot accepts your URL and reports nothing — no console, no
error, no DOM. A local browser gives you the full trace per iteration
for free. The local loop is the fast path; the blind loop is the slow
one, and it burns the scarcest resource (bot visits).

## "I reproduced the bot and my payload fires — why did the live bot do nothing?"

The reproduction diverged from live. Check each behaviour axis: the
URL it visits, the credential it carries, the wait it allows, the
flags it runs, the browser version. A difference on any of them means
your local test was on a different bot. The second most common cause
is the *channel* — the exfil never left (tunnel interstitial, egress,
CSP), which is a different failure than the payload.

## "The flag is supposed to be a cookie but document.cookie is empty"

The cookie is `HttpOnly` — hidden from the JS view. Read the jar via
`GET /session/{id}/cookies`, or exfil it by having the payload make a
same-origin request the cookie rides automatically and reading the
response.

## "`POST /session` works but `file://` returns an error page"

Two possibilities: the scheme is blocked at the driver (try `execute`
`fetch("file:///...")` — a different primitive), or the path does not
exist/unreadable (try `/etc/passwd` to distinguish). A scheme block
and a missing file are different kill states.

## "How is the exposed endpoint different from SSRF?"

Both reach internal surfaces, but the mechanism differs: SSRF is the
*app's* HTTP client fetching a URL; a WebDriver endpoint is a *browser*
running JS, holding cookies, rendering. The discriminator: does the
"visitor" run JavaScript and hold a cookie jar? A browser does; a
`curl`-like fetch does not. The endpoint is a browser foothold, not a
server fetch.

## "Do I need Playwright/Selenium, or is curl enough?"

`curl` is enough — every primitive is a plain HTTP call. The libraries
buy convenience (Playwright's console/network hooks are the strongest
reason to use it); the protocol is the same either way. Use `curl`
when no library is installed or you want the raw commands.

## "The bot waits only 2s but my payload needs an async fetch chain"

Fit the work inside the wait — a fire-and-forget `sendBeacon`/`Image`
survives navigation and needs no round-trip; a two-hop read+exfil
needs the wait to cover both. Measure the payload's time, do not
guess it fits.

## "Is a `sessionId` proof the endpoint is exploitable?"

No — it proves the endpoint answers. Exploitability needs a live
primitive (a `file://` read returning a file, an `execute` running
JS). A session is a capability; the read is the exploit.

## "My payload worked on my test page — why not the bot's?"

The bot's page is a different DOM/context — authenticated view, flag
page, a frame. Test on the same page/context the bot renders, not a
synthetic one.
