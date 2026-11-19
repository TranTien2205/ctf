# Negative results — recording what did not work, as measurements

## Why negatives matter here

A blind bot visit burns the scarcest resource the challenge gives you.
Every dead end recorded as a measurement prevents re-walking it — and
a clean kill map lets `tools/decide.py` name the next layer instead of
the next guess.

## The kill-map cells

| Cell | Measurement | What it closes |
|---|---|---|
| endpoint-exposed | `POST /session` refused on every port/route | the attack-surface use |
| file-read | `file://` navigate errors or empty source | the file-read primitive |
| js-capability | `execute` returns permission error | the JS-in-browser primitive |
| reproduction | local bot cannot match live on flags/wait/cookie | faithful local development |
| injection-executes | canary never fires in local bot | the payload-context assumption |
| channel | `REQ` to tunnel, no hit | the exfil channel |
| bot-visits | live bot never visits your URL | the bot-flow assumption |

## The measurement format

A negative is a *measured state*, not "didn't work":

```
endpoint-exposed: POST http://t:9515/session -> connection refused.
  closes: attack-surface use at :9515.
file-read: navigate file:///etc/passwd -> source = Chrome error page.
  closes: file-read primitive via navigation.
channel: REQ GET https://tunnel/x logged, listener silent.
  closes: tunnel as exfil channel for headless.
```

Each records the probe and the resulting state — enough for the next
run to skip the cell without re-running the probe.

## The honest "cannot reproduce"

When the bot's source is not supplied and its properties cannot be
observed, "cannot reproduce faithfully" is itself a negative to record
— with which properties are assumptions. It is weaker evidence than a
confirmed reproduction and must be stated as such, not hidden.

## The reproduction-mismatch negative

A payload confirmed locally that fails at the live bot is a negative
*on the reproduction* before it is a negative on the payload. Record
it as "reproduction diverged from live on <axis>" once you find which
axis — and until then as "unexplained local/live divergence", not a
dead payload.

## What is not a negative

- a single payload miss — noise, not a falsifier
- "the bot didn't visit yet" — timing, not a dead flow
- a driver install failure — a tooling problem, not a class negative

## The re-open precondition

Each kill-map cell carries what would re-open it:

- endpoint-exposed: another port/route answers `POST /session`
- file-read: `execute` `fetch("file://")` works where navigate failed
- channel: a different exfil channel (same-origin, redirect, DNS)
- reproduction: the bot's source is found, giving real properties

The kill map is a set of measured states with their re-open
conditions — not a list of "tried, failed".
