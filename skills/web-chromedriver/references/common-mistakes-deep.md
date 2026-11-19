# Common mistakes deep — the misapplications, in detail

## The blind-fire loop

The pattern: guess a payload, submit to the report bot, wait, see
nothing, guess again. Each iteration is a blind coin flip — the live
bot reports no console, no error, no DOM. The skill exists precisely
to close this channel; a session spent blind-firing is a session that
skipped the reproduction step.

**Why it persists**: building a local bot feels like overhead before
"just trying" the payload. It is the opposite — the local loop is the
fast path; the blind loop is the slow one.

## The "works on my page" fallacy

Testing the payload on a synthetic page or the anonymous view, then
assuming it transfers to the bot's authenticated/flag-bearing page.
The bot's page is a different DOM, different context, different
cookies — a payload confirmed on the wrong page is unconfirmed.

## The DOM-vs-response confusion

Reading the HTTP response body to judge where a payload landed. The
rendered DOM is a different document — sanitisation, JS rewriting,
and template rendering all change it. `page.content()`/`GET /source`
is the truth; the response body is what arrived, not what ran.

## The canary skip

Leading with the full multi-stage exfil instead of a `console.log`.
A dead full payload gives no signal about *which* stage died — the
injection, the read, the encode, or the channel. The canary ladder
isolates one property per rung.

## The assumption presented as fact

A reproduction built on guessed properties (wait, cookie, flags) with
the guesses unrecorded. A "confirmed" payload on unstated assumptions
reads as stronger than it is — the notes must carry which properties
were observed vs assumed.

## The leaked-session leak

Creating WebDriver sessions without `DELETE` — each leaks a browser
process. On a local driver it leaks memory; on a shared endpoint it
can hold the only session slot and break the challenge's own bot.
`driver.quit()`/`DELETE` in a `finally`, always.

## The wrong-frame hook

Injecting `window.onerror` on the top frame when the payload runs in
an iframe — the hook and the payload are in different documents, the
error never reaches your listener. Inject into the frame the payload
lands in, or all frames.

## The version-blind reproduction

Reproducing flags/wait/cookie but not the browser *version* — an old
`--headless`, a different JS engine, a different CSP. When the
reproduction matches on all listed properties but still diverges
from live, the unpinned version is the remaining suspect.

## The "sessionId = read" conflation

Treating a `POST /session` `sessionId` as proof of a file read. The
session proves the endpoint answers; the read is proven by `file://`
`source` returning a file's contents. A session is a capability, not
an exploit.

## The timeout-free hang

Commands without timeouts — a `file://` crawl, a hanging `goto`, an
`execute/async` whose callback never fires — pin the session and the
browser. Set `timeouts` and use `wait_until="domcontentloaded"` so a
hang is bounded, not a stall.
