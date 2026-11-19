# Preconditions deep — each requirement, justified

## The debugging-aid preconditions

**A bot flow exists.** The whole point is reproducing the bot — without
a report/admin-visit flow, there is no blind channel to open. Verify
by the flow's presence (a form, a "the admin will check"), not by
assuming every web challenge has one.

**The payload is client-side.** The bot is a browser; it only runs
client-side payloads (XSS, DOM, template-in-DOM, CSRF-via-browser). A
server-side bug (SQLi, SSRF, RCE) does not need a browser to test —
reproducing the bot is pointless. The discriminator: does the
payload's effect happen *in a renderer*?

**A driver exists or is installable.** `which chromedriver` — the local
reproduction needs a real browser to drive. A missing driver is a
tooling precondition, fixable by install or by using `curl` against a
remote endpoint if one is exposed.

**The bot's properties are recoverable.** Either the bot's source is
supplied (copy it) or its behaviour is observable (derive it). When
neither holds, the reproduction is part guessing — still usable for
development, but the confirmed payload is weaker evidence.

## The attack-surface preconditions

**An endpoint answers.** `POST /session` (or `GET /json` for CDP) on a
reachable port/route returns a session. The falsifier is a refusal on
every plausible endpoint — without an answering endpoint there is no
surface.

**A primitive is live.** A session that creates but cannot navigate,
execute, or read is a capability with no reach — the read primitives
must actually return. A `sessionId` alone is not a foothold.

**The flag is in reach.** The browser's surface — files, loopback,
cookies, DOM, render — must cover the flag's location. A flag on a
host/service the browser cannot reach is outside this surface.

## The shared preconditions

**In scope.** The driver/bot is part of the supplied challenge — an
exposed endpoint on a neighbouring host is out of scope, not a target.

**The work fits the constraints.** The payload's async work fits the
bot's wait; the session's commands fit the timeouts. A payload that
needs more time than the bot gives is dead regardless of correctness.

## The honest gaps

- **closed remote, no bot source** — reproduction is on assumptions;
  development works, transfer is weaker. Record it.
- **flag needs the live bot's credential** — local development proves
  the payload runs, not the exfil value; the live fire is the test.
- **no local driver AND no exposed endpoint** — the skill has no
  browser to drive; install a driver or pivot.
