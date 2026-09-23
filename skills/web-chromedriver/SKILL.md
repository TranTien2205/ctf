---
name: web-chromedriver
description: >
  Drive a headless browser yourself. Use to reproduce a challenge's admin bot
  locally so a client-side payload can be debugged without spending bot cycles,
  and to read what the page actually did. Also covers a WebDriver endpoint
  exposed by the challenge itself.
tags: [web, chromedriver, webdriver, headless, admin-bot, xss, ctf]
environment: [ctf, lab, authorized-testing]
evidence_level: verified
---

# Headless browser control

**Why this exists.** Challenges with an admin bot give you a small number of
visits and no error output. Debugging a payload against the live bot burns those
visits and tells you nothing when it fails. Reproducing the bot locally turns a
blind channel into a normal debugging loop.

This lesson is recorded in `../../solved/apexsurvive.md`: payload development happened
against a local headless browser, and only confirmed payloads were fired at the
bot.

## Build the local bot first

Read the challenge's own bot source when it is supplied — it is usually a short
script, and it tells you exactly what you are reproducing:

- which URL it visits, and how it is handed to the bot
- what it authenticates as, and where that credential lives
- how long it waits, and whether it runs one page or several
- which flags Chrome is launched with

Then run the same shape locally against your own copy of the app. If the bot
source is not supplied, reproduce what you can observe and say in the notes which
parts are assumptions.

## Two ways to drive it

**Library.** Selenium or Playwright is usually simplest when you already have a
Python environment. Confirm the driver exists with `which chromedriver` before
relying on it.

**Protocol.** WebDriver is plain HTTP and JSON, so `curl` is enough when no
library is installed. The endpoint cheat sheet is in
`references/webdriver-api.md`: create a session, navigate, read the page source,
run a script, delete the session.

Either way, delete the session when finished — a leaked session holds a browser
process open.

## What it buys you

| Question | How the local browser answers it |
|---|---|
| Did my payload execute at all? | console output and thrown errors, which the live bot never shows you |
| Which context did the value land in? | read the rendered DOM rather than guessing from the response body |
| Does the sanitiser run before or after my sink? | observe the order directly with a marker at each stage |
| Does my exfiltration request actually leave? | watch the network from the driver instead of waiting on a listener |
| Is the tunnel reachable by a headless client? | fetch your own URL from the driver before handing it to the bot |

That last row is worth its own note: some tunnelling services insert an
interstitial page that a headless browser cannot get past. Check with a
browser-like request **before** spending a bot visit — `../../solved/tornadoservice.md`
records losing attempts to exactly this.

## When the challenge exposes a WebDriver endpoint

Occasionally the driver itself is the challenge surface. Then it is a capability,
not a debugging aid: a session can navigate to a local file URL and the page
source returns its contents, which is a file read as whatever user launched the
driver. Confirm with a path the target certainly has, and treat it as
`../file-read-primitives/` from there.

## Scope

Only the challenge's own instance and your local copy. A browser you drive is a
client acting as its user, so everything the safety rules say about writes on a
shared instance applies to it too.

## References

- `references/webdriver-api.md` — endpoint cheat sheet for driving the protocol
  directly with `curl`

## Routing

Client-side payload work: `../web-xss/`. Bot-delivered state change:
`../web-csrf/`. Budget and escalation: `../LOOP_DISCIPLINE.md`.
