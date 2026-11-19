# Evidence rules deep — the proof hierarchy in detail

## The three evidence tiers

| Tier | Kind | Proves |
|---|---|---|
| development | local-bot console/network/DOM | the payload works in *your* reproduction |
| capability | `sessionId`, a live `execute`, a `file://` source | the endpoint exposes the primitive |
| impact | live exfil hit, the flag-bearing `source`/`cookies` | the target gave up the flag |

Only impact evidence carries the flag — development evidence is the
path, capability evidence is the reach.

## The substring rule

`tools/hooks.py post-probe` with `confirms` requires `--evidence` be a
substring of `--response` — the quote is *checked*. For this skill:

- file-read confirm: `--response` = the `GET /source` body, `--evidence`
  = a line from the file inside it (`root:x:0:0`)
- flag confirm: `--response` = the listener's logged request or the
  `source`/`cookies` body carrying the flag, `--evidence` = the flag
  substring
- endpoint confirm: `--response` = the `POST /session` JSON,
  `--evidence` = the `sessionId` field

## The live-response requirement

The proving bytes must be a *live* response or a supplied artifact:

- live exfil listener log -> live
- `GET /source` body -> live
- `GET /cookies` body -> live
- a local-bot console log -> development, NOT a flag proof
- a `TESTFLAG`/`CANARY` -> development, NOT a flag

## The reproduction-honesty requirement

A locally-confirmed payload is evidence *of the reproduction*, not of
the target. Record it as:

```
payload X fires in local bot (reproduction: URL/cookie copied, wait/
flags assumed). Not yet target-proven.
```

The "assumed" list is part of the evidence — a payload on assumed
properties is weaker than on copied ones.

## The candidate chain

```
flag-shaped string in a live response
  -> tools/hooks.py pre-flag --value <s> --source <resp> --evidence <excerpt>
    -> gate passes -> the flag
    -> gate fails -> still a candidate
```

The gate is the boundary — a flag-shaped string is never asserted as
the flag before it.

## What does not count as a confirm

- a `sessionId` -> proves the endpoint, not a read
- a `1+1` return -> proves `execute` works, not the flag
- a screenshot -> an artifact; the flag text it shows still needs the
  gate (the PNG is the carrier, the flag in it is the candidate)
- "the bot visited" -> proves the flow, not the payload or the flag

## The negative evidence

A measured negative is a finding too — record it with the probe:

```
file-read: nav file:///etc/passwd -> Chrome error page. closes: read.
```

A kill-map entry is evidence of the *dead* layer — as useful as a
live primitive for the next run's planning.
