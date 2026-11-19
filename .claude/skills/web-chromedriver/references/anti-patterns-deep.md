# Anti-patterns deep — the named mistakes, with the cost

## "Fire and see" — the blind channel

**The pattern**: submit a guessed payload to the live bot, wait, see
nothing, guess again.

**The cost**: each iteration is a blind coin flip — the live bot
returns ~zero signal (no console, no error, no DOM). A session spent
blind-firing burns the scarcest resource the challenge gives you: bot
visits. The local reproduction converts each iteration into a full-
observability debug step for free.

**The fix**: build the local bot first; develop there; fire once.

## "It worked on my test page" — the wrong reproduction

**The pattern**: confirming a payload on a synthetic page or the
anonymous view, then treating it as ready.

**The cost**: the bot's page is a different DOM, context, cookies —
a payload confirmed on the wrong page is unconfirmed. False positives
("fires locally, dead live") and false negatives ("dead locally,
would have worked") both follow.

**The fix**: test on the same page/context the bot renders — copy the
URL, the auth, the DOM.

## "The response body is the DOM" — reading the wrong document

**The pattern**: judging where a payload landed from the HTTP response
body.

**The cost**: the rendered DOM is a different document — sanitisation,
JS rewriting, and template rendering all change it. A payload judged
"safe" by the response may land in an exploitable context in the DOM,
and vice versa.

**The fix**: read `page.content()`/`GET /source`, not the raw response.

## "A sessionId is a read" — conflating capability and exploit

**The pattern**: treating `POST /session` `sessionId` as proof of a
file read.

**The cost**: the session proves the endpoint answers — a capability.
The read is proven by `file://` `source` returning a file's contents.
A capability claim is not an exploit claim.

**The fix**: the read primitive's own output is the proof — the file
text, not the session id.

## "Skip the canary" — debugging the whole chain blind

**The pattern**: leading with the full multi-stage exfil.

**The cost**: a dead full payload gives no signal about which stage
died — the injection, the read, the encode, or the channel. Each dead
run is a wasted bot visit.

**The fix**: climb the canary ladder — `console.log` -> context ->
read -> encode -> exfil — one property per rung.

## "Keep the session open" — the leaked browser

**The pattern**: creating WebDriver sessions without `DELETE`.

**The cost**: each leaked session leaks a browser process — memory on
a local driver, a held slot on a shared endpoint. On a shared
challenge it can break the challenge's own bot for everyone.

**The fix**: `DELETE`/`driver.quit()` in a `finally`, always.

## "The reproduction is close enough" — the assumption as fact

**The pattern**: reproducing on guessed properties (wait, cookie,
flags) and treating the local confirmation as target-strong.

**The cost**: a reproduction that diverges on any behaviour axis is a
different bot — its confirmations do not transfer. A "confirmed"
payload on unstated assumptions reads as stronger than it is.

**The fix**: copy the spec verbatim; record which properties are
assumptions in the notes.

## "Try another variant" — the spent-layer loop

**The pattern**: five variants of the same payload shape against the
same context.

**The cost**: a spent mechanism layer — the bug is the reproduction,
the context, or the channel, not the payload's nth variant.

**The fix**: when the loop stalls, change layer — the reproduction,
the context (`../web-xss/`), or the channel (`evasion.md`).

## "My tunnel works in my browser" — the unverified channel

**The pattern**: assuming the tunnel is reachable because your own
browser reaches it.

**The cost**: headless clients hit interstitials and filters your
browser skips — `tornadoservice` lost attempts to exactly this.

**The fix**: `goto`/`fetch` your own URL from inside the driver first.

## "The flag-shaped string is the flag" — the candidate as proof

**The pattern**: a `TESTFLAG`/canary/local marker presented as the flag.

**The cost**: the flag comes from a live response — the live exfil or
the `source`/`cookies`/`screenshot` — gated through `pre-flag`. A
development signal is not a flag.

**The fix**: the live response through the gate, always.
