# Common mistakes — the ways this skill is misapplied

## Firing blind at the live bot

The single most expensive mistake: submitting a guessed payload to the
report-bot and waiting to see if it works. The live bot is a blind
channel — every visit is a coin flip you cannot inspect. Develop
locally first; fire once confirmed.

## Testing on the wrong reproduction

A local bot that does not match the challenge's bot — different flags,
a guessed wait, a missing cookie, the wrong URL — produces false
positives (fires locally, dead at the bot) and false negatives (dead
locally, would have worked). Reproduce exactly; read the bot source.

## Reading the response body instead of the rendered DOM

The response body and the rendered DOM are different documents —
sanitisation and JS rewriting change the latter. Judging a payload's
context from the raw response instead of `page.content()` reads the
wrong document.

## Skipping the canary

Leading with the full exfil payload instead of a `console.log`/`fetch`
canary conflates "did it execute" with "did the exfil leave" — two
different bugs, one dead visit each. Prove execution first.

## Not checking the tunnel from inside the driver

Assuming the tunnel is reachable because it works in your own browser.
Headless clients hit interstitials and filters your browser skips.
`tornadoservice` lost attempts to exactly this — `page.goto` your own
URL inside the driver before the payload.

## Leaking sessions

Creating sessions and never `DELETE`-ing them. A leaked session holds
a browser process — on a local driver it leaks memory, on a shared
endpoint it can hold the only session slot. Always delete.

## Mismatched driver and browser versions

`chromedriver` must match the browser's major version. A version
mismatch fails at session creation with a version error, not at the
payload — check `chromedriver --version` vs the browser's before
assuming the payload is the problem.

## Confusing development evidence with a flag

A `console.log` marker or a `TESTFLAG` listener hit is development
evidence — proof the payload works locally, not a flag. Only the live
bot's exfil or the exposed endpoint's `file://` source carries the
flag, and it goes through `pre-flag` like any class.

## Over-iterating on one mechanism layer

Five variants of the same payload shape against the same context is a
spent mechanism layer, not progress. When the local loop stalls, the
bug is the reproduction, the context, or the channel — change layer,
do not re-roll the payload.

## Ignoring the wait budget

A payload with a 5-second async chain fired at a bot that waits 2
seconds is dead regardless of correctness. Match the payload's work
to the bot's wait — read it from the bot source, do not guess it is
long enough.

## Treating the exposed endpoint as only a debugging aid

An exposed WebDriver endpoint on the challenge is a file-read and
internal-network capability — not just a way to debug. Test the
`file://` and `localhost` reads before assuming it is inert.

## Using the payload's context for the error hook

Injecting `window.onerror` on the top frame when the payload runs in
an iframe — the hook and the payload are in different documents and
the error never reaches your listener. Inject into the same frame.
