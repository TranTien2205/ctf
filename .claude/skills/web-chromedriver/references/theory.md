# Theory — why a driven browser is a foothold and a debug harness

## The capability argument

A WebDriver session is a *capability*, not a bug in itself — it is a
remote handle on a fully-powered browser. The power comes from what a
browser already does: navigate anywhere it can reach, run JS in an
origin, hold cookies, render. Pointed at `file://` or `localhost`, a
capability that is "just a browser" becomes a file read and an
internal-network foothold.

The vulnerability is the *exposure* — a driver port that answers
`POST /session` to an unauthenticated client. The primitive set is the
browser's own; the flaw is that it is reachable.

## The debugging argument

A live admin bot is a *blind channel*: it visits your URL, does
something, and reports nothing back. Debugging a payload against it is
debugging by coin flip. A local headless browser turns the same
payload into a closed debug loop — every signal (console, errors, DOM,
network) is visible, and iterations cost CPU, not bot visits.

The skill exists because the blind channel is the expensive path. The
local reproduction is not a nicety — it is the difference between a
handful of uninspectable guesses and a real debug session.

## The reproduction-fidelity argument

A reproduction only transfers to the live bot when it matches on the
axes that change behaviour: the URL, the credential, the wait, the
flags, the JS context. A reproduction that diverges on any axis is a
test of a *different* bot — its confirmations and denials do not
transfer. This is why the bot's source is read as a spec and copied
verbatim, and why observed-but-unguessed properties are recorded as
assumptions rather than treated as certain.

## The surface argument

The browser's attack surface is *positional*: it sits on the challenge
host, so `localhost` is the app's loopback and `file://` is the
container's filesystem — surfaces an external request cannot reach.
The skill is the bridge to that position: the same commands that
navigate a page navigate to a file; the same `execute` that reads a
DOM reads the cookie jar and a same-origin flag page.

## The falsification argument

The class is honest about its two uses: an exposed endpoint, or a bot
worth reproducing. Each has a measured falsifier — `POST /session`
refused, or no bot flow. The kill map is a set of measured states, not
"didn't work" — each cell records the probe and the state that closed
it, plus the observation that would re-open it.

## The evidence argument

Development evidence (local console, a `TESTFLAG`) proves the payload
works in *your* reproduction; impact evidence (the live exfil, the
`file://` source) proves the target. The flag is the second kind,
gated through `pre-flag` like every class — a local confirmation is
necessary, never sufficient.
