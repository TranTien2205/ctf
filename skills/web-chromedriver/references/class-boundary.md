# Class boundary — what web-chromedriver is and is not

## Not XSS

`web-chromedriver` does not construct or classify XSS payloads — it
drives the browser the payload runs in. The context discovery, sink
selection, and sanitiser bypass belong to `../web-xss/`. This skill
answers "how do I *run* a real browser to test/exfil", not "what
payload".

Boundary: if the question is "which context does the value land in" ->
`../web-xss/`. If it is "did my payload fire in a real renderer" ->
here.

## Not SSRF

An exposed WebDriver endpoint that navigates to `file://`/`localhost`
is a file read and internal-network reach — but through a *browser*,
not a server-side fetch. `../web-ssrf/` covers the server fetching a
URL; this skill covers a browser session you drive. The `file://` read
here routes to `../file-read-primitives/` for what to read next.

Boundary: if the request leaves from the app's HTTP client -> SSRF.
If it leaves from a browser you own via WebDriver -> here.

## Not general file-read

The `file://` navigation is one read primitive among many —
`../file-read-primitives/` covers LFI, XXE, archive traversal, path
params. This skill supplies the *WebDriver-specific* read and hands
off the "what to read" question.

## Not client-side template injection as a class

The observability here helps debug a CSTI payload, but the
vulnerability class is `../web-ssti/`/`../web-xss/`. This skill is the
harness, not the bug.

## Not CSRF

A bot-delivered state change is `../web-csrf/` territory when the
payload is a forged request the bot's session performs. This skill
drives the browser for *debugging* or *file-read* — the CSRF class
covers the state-change mechanism itself.

## The two uses are one skill

Both the debugging aid and the attack surface are the same underlying
thing — a WebDriver session you control. The skill is the command set
and the reproduction discipline; whether it is pointed at your local
browser or the challenge's endpoint is a deployment detail, not a
different class.

## When to leave this class

| Observation | Route to |
|---|---|
| the payload won't fire because of the HTML/JS context | `../web-xss/` |
| the "bot" is actually a server-side fetch | `../web-ssrf/` |
| a file read exists and the goal is source/flag path | `../file-read-primitives/` |
| the bot performs a state-changing request | `../web-csrf/` |
| the endpoint is a Grid with auth you must break | `../web-auth-session/` |

The boundary rule: `web-chromedriver` is the *browser control layer*.
Once the question is about a payload class or a different primitive,
route out; while the question is "drive a real browser", stay here.
