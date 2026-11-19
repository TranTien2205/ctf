# Falsifiers — the measured states that kill this class

## The class falsifier

`web-chromedriver` dies when neither of its two uses applies:

- **No bot to reproduce** — the challenge has no admin-bot / report
  flow, so there is no blind channel to open, AND
- **No exposed endpoint** — `POST /session` is refused on every
  plausible port/route, so there is no attack surface either.

Either use surviving keeps the class alive. Both dead kills it.

## Debugging-aid falsifiers (the reproduction is impossible)

The local-bot use dies when you cannot reproduce the bot faithfully:

- no bot source supplied AND no observable reproduction properties —
  you cannot guess URL + credential + wait + flags simultaneously
- the live flow cannot be stood up locally at all (closed-source
  remote app with no local copy) AND the bot's behaviour is opaque
- the payload genuinely requires the live bot's credential (a flag
  cookie only it holds) — then local development proves the payload
  shape but never the exfil; the live fire is the only test

The last one is common, not a falsifier — local development still
proves the payload *runs*; only the exfil value is unverifiable.

## Attack-surface falsifiers (the endpoint is not a foothold)

| Observation | Falsifies |
|---|---|
| `POST /session` refused / 404 | no exposed endpoint |
| session created, `file://` navigate errors | file read blocked by config |
| `file://` loads but `source` returns an error page | read is empty/blocked |
| `execute` returns a permissions error | no JS capability |
| session times out before navigation | endpoint unusable |

A refused `POST /session` is the whole class dead at that endpoint —
not a payload problem.

## The reproduction-mismatch falsifier (the subtle one)

The most dangerous false state: a payload that fires locally and dies
at the live bot, where the *reproduction* is the bug, not the payload.
The falsifier of "my reproduction is faithful" is a divergence on any
axis — different flags, a shorter wait, a missing cookie, a different
injection context. When local works and live fails, the reproduction
is the first suspect — re-derive each property from the bot source or
observation before rewriting the payload.

## The budget falsifier

Under the controller, the class dies at its budget on any mechanism
layer — the controller answers `escalate`, not "try harder". A payload
that will not fire after five genuine iterations on different
mechanism axes (context, channel, timing, reproduction) is a spent
mechanism layer, and `tools/decide.py` names the next rung.

## What a falsifier is not

- "the payload did not fire once" — a single miss is noise, not a
  falsifier
- "the live bot did not visit" — a bot-side delay or a wrong URL, not
  a dead class
- "I could not get the driver working" — a tooling problem, not a
  class falsifier; install the driver or use `curl`

Record each falsifier as a measured state with the observation that
closed it — the kill map needs the measurement, not the conclusion.
