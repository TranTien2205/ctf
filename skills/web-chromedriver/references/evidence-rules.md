# Evidence rules — what counts as proof here

## The two proofs

`web-chromedriver` produces two distinct kinds of evidence, and they
must not be confused:

**Development evidence** — the local bot's console, network log, DOM,
screenshots. Proves the payload works *in your reproduction*. It is
not a flag and not a finding about the target.

**Impact evidence** — the live bot's exfil hit on your listener, or
the `file://` page source from the exposed endpoint. This is the only
proof that matters for the flag.

## What proves what

| Claim | Proof |
|---|---|
| my payload executes | a console marker / a fetch in the local network log |
| my exfil channel works | a listener hit carrying the value (local test) |
| the flag was exfiltrated | a listener hit carrying the flag-shaped value from the live bot |
| the WebDriver endpoint is exposed | a `sessionId` from `POST /session` |
| a file read exists | the `file://` source returning the file's contents |
| the flag | the flag-shaped string in a live response/artifact, through `pre-flag` |

## The candidate rule

A flag-shaped string on your listener is a *candidate* until it passes
`tools/hooks.py pre-flag` — same as any other class. The gate checks
the evidence is a substring of the proving response. A console marker
or a `TESTFLAG` is never a flag.

## Development evidence is not proof

A payload that fires in the local bot is *locally confirmed*, not
*target-proven*. Record it as "fires in reproduction" — the live bot
hit is what promotes it. A reproduction mismatch (flags, wait, cookie)
can make a locally-confirmed payload dead at the live bot, so the
local confirmation is necessary but not sufficient.

## The reproduction honesty rule

When the bot's source is not supplied, the reproduction is part
guessing. Record which parts are assumptions — the wait you chose, the
cookie name you guessed, the flags you defaulted to. A "confirmed"
payload on an assumed reproduction is weaker than on a matching one,
and the notes must say so.

## The negative-result rule

Record dead ends as measurements, not "didn't work":

- `POST /session` refused -> "endpoint not exposed" (the class dies here)
- `file://` navigation blocked -> "file read blocked by config"
- canary never fired -> "injection does not execute" (the context bug)
- `REQ` logged, no listener hit -> "tunnel unreachable" (the channel bug)

Each is a falsifier or a cell in the kill map — a measured negative,
not a shrug.

## The provenance rule

The proving response for the attack-surface use is the `GET /source`
body from the live endpoint — save it, not just the flag it contained.
For the debugging-aid use, the proving response is your listener's log
of the live bot's request. Both go through the hook with the bytes.

## What does not count

- a screenshot of a flag-shaped string (not a live response you can
  gate — capture the source/text, not the image, unless the image is
  the only carrier; then the PNG is the artifact)
- `TESTFLAG` / `CANARY` hits — development signals, not flags
- a payload that "should work" but was never fired at the live bot
- a `sessionId` as proof of file read — it proves the endpoint, not
  the read; the `file://` source is the read proof
