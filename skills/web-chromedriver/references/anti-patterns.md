# Anti-patterns — the named mistakes to refuse

## "Fire and see"

Submitting a guessed payload to the live bot to "see if it works".
The live bot is a blind channel — each visit returns ~zero signal and
costs the scarcest resource. **Refuse it**: develop in the local
reproduction; fire once confirmed.

## "It worked on my test page"

Confirming a payload on a synthetic page or the anonymous view, then
treating it as ready. The bot's page is a different DOM/context —
authenticated, flag-bearing, framed. **Refuse it**: test on the same
page/context the bot renders.

## "The response body is the DOM"

Judging where a payload landed from the HTTP response body. The
rendered DOM is a different document — sanitisation and JS rewriting
change it. **Refuse it**: read `page.content()`/`GET /source`, not
the raw response.

## "A sessionId is a read"

Treating `POST /session` `sessionId` as proof of a file read. The
session proves the endpoint answers; the read is proven by `file://`
`source` returning a file. **Refuse it**: a capability is not an
exploit.

## "Skip the canary"

Leading with the full multi-stage exfil. A dead full payload gives no
signal about which stage died. **Refuse it**: climb the canary ladder —
`console.log` -> context -> read -> encode -> exfil — one property per
rung.

## "Keep the session open"

Creating WebDriver sessions without `DELETE`. A leaked session leaks a
browser process; on a shared endpoint it can hold the only slot and
break the challenge's bot. **Refuse it**: `DELETE`/`quit()` in a
`finally`, always.

## "The reproduction is close enough"

Reproducing on guessed properties and treating the local confirmation
as target-strong. A reproduction that diverges on any behaviour axis
is a different bot. **Refuse it**: copy the spec verbatim; record
which properties are assumptions.

## "Try another payload variant"

Five variants of the same payload shape against the same context — a
spent mechanism layer, not progress. **Refuse it**: when the loop
stalls, the bug is the reproduction, the context, or the channel —
change layer, not the payload.

## "My tunnel works, I tested it in my browser"

Assuming the tunnel is reachable because your own browser reaches it.
Headless clients hit interstitials and filters your browser skips.
**Refuse it**: `goto`/`fetch` your own URL from inside the driver
first — `tornadoservice` is the recorded cost.

## "The flag-shaped string is the flag"

A `TESTFLAG`/canary/local marker presented as the flag. **Refuse it**:
the flag comes from a live response — the live exfil or the `source`/
`cookies`/`screenshot` — gated through `pre-flag`.

## "Drive the browser for everything"

Reaching for a full driver when a single `curl` would do — the browser
harness is for payloads that need a renderer. A server-side read or a
simple HTTP check does not need one. **Refuse it**: the driver is for
the browser-dependent cases, not a default tool.
