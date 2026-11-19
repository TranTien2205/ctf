# Summary deep — the complete mental model

## The skill in one sentence

Drive a real browser — yours for debugging a client-side payload, the
challenge's for a file-read and loopback foothold — through the same
WebDriver command set.

## The two-use invariant

| | Debugging aid | Attack surface |
|---|---|---|
| whose browser | yours (local) | theirs (exposed endpoint) |
| purpose | observe + iterate a payload | read a file/route/cookie |
| the flag comes via | live exfil on your listener | the `source`/`cookies`/`screenshot` |
| the falsifier | can't reproduce faithfully | `POST /session` refused |
| the budget | bot visits (spend locally) | probes (cheap) |

Same commands, different owner — the skill is the command set plus the
reproduction discipline.

## The command set (the whole API you need)

```
POST   /session                  -> sessionId
POST   /session/{id}/url         -> navigate (file://, localhost, any)
GET    /session/{id}/source      -> rendered DOM / file text
POST   /session/{id}/execute/*   -> JS in the page (origin + cookies)
GET    /session/{id}/cookies     -> the jar (HttpOnly too)
GET    /session/{id}/screenshot  -> PNG
DELETE /session/{id}             -> always
```

## The reproduction invariant

A reproduction transfers iff it matches on the behaviour axes — URL,
cookie, wait, flags, version. Divergence on any axis = a different
bot = local results do not transfer. Copy the bot's spec verbatim;
record assumptions.

## The observability set

```
console -> did it run / what errored
pageerror -> the thrown exception
request/response -> what left, what returned
requestfailed -> what was blocked (CSP/DNS/TLS)
DOM -> where the value landed
```

The four-plus-one channels answer every blind question the live bot
hides.

## The development loop

```
reproduce -> canary (prove exec) -> staged markers -> iterate
-> channel check (from inside) -> confirm -> fire live once -> pre-flag
```

## The reads (attack surface)

```
file read     -> file:// nav (or execute fetch) + source
loopback      -> localhost nav + source
cookie        -> GET /cookies (jar) or execute document.cookie
same-origin   -> execute fetch("/flag")
rendered      -> GET /screenshot
```

## The kill map

8 cells: endpoint-exposure, file-read, js-execution, loopback-reach,
reproduction, exfil-channel, flag-in-reach, bot-flow. Each a probe +
kill state + re-open. The class dies when both uses are dead.

## The traps (all recorded)

- blind-fire at the live bot — develop locally
- wrong reproduction — copy the spec
- tunnel interstitial — check from inside (`tornadoservice`)
- response body vs rendered DOM — read the DOM
- leaked session — always `DELETE`
- `sessionId` != a read — the `file://` `source` is the proof
- `TESTFLAG` != flag — live exfil through `pre-flag`

## The anchors

`apexsurvive` (local-bot debugging works) + `tornadoservice` (the
channel check is the skipped step). The method is verified; the
endpoint-as-capability is standard knowledge, not a local solve.
