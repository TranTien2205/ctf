---
name: web-chromedriver
description: >
  Drive a headless browser yourself. Use to reproduce a challenge's admin bot
  locally so a client-side payload can be debugged without spending bot cycles,
  and to read what the page actually did. Also covers a WebDriver endpoint
  exposed by the challenge itself.
tags: [web, chromedriver, webdriver, headless, admin-bot, xss, ctf]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
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
- `references/mechanism.md` — the two uses and the WebDriver model
- `references/detection.md` — is an endpoint exposed / is a bot worth it
- `references/library-drivers.md` — Selenium / Playwright / curl
- `references/local-bot.md` — reproduce the challenge's bot
- `references/attack-surface.md` — the endpoint as file-read/loopback target
- `references/observability.md` — console, errors, DOM, network
- `references/payload-development.md` — the debug loop
- `references/payload-variants.md` — the exfil and probe payload library
- `references/capabilities.md` — the session capability reference
- `references/chrome-flags.md` — the flags and their reproduction
- `references/session-management.md` — lifecycle, leaks, shared instances
- `references/cdp.md` — DevTools protocol when WebDriver is not enough
- `references/grid-remote.md` — the Grid/shared variant
- `references/multi-page.md` — frames, pages, contexts
- `references/headless-detection.md` — is the visitor a real browser
- `references/workflow.md` — the ordered run
- `references/evidence-rules.md` — what counts as proof
- `references/falsifiers.md` — what kills the class
- `references/troubleshoot.md` — the failure modes and fixes
- `references/edge-cases.md` — the unusual states
- `references/common-mistakes.md` — the misapplications
- `references/class-boundary.md` — where this skill ends
- `references/negative-results.md` — recording dead ends
- `references/evasion.md` — blocked-channel pivots
- `references/attack-shapes.md` — the named exploit patterns
- `references/case-studies.md` — the solved anchors
- `references/per-mechanism.md`, `references/per-check.md`,
  `references/per-route.md`, `references/per-endpoint.md`,
  `references/per-surface.md`, `references/per-boundary.md`,
  `references/per-vector.md`, `references/per-falsifier.md` — the per-axis maps
- `references/detection-matrix.md`, `references/detection-surface.md`,
  `references/detection-index.md`, `references/detection-checklist.md`
  — the detection maps
- `references/theory.md`, `references/glossary.md`, `references/summary.md`,
  `references/onboarding.md`, `references/first-hour.md`,
  `references/preconditions.md`, `references/common-questions.md`,
  `references/checklist.md`, `references/quick-reference.md`,
  `references/field-manual.md`, `references/verified-chains.md` — the
  reference set
- `references/README.md` — the full index of ~120 reference files,
  including `*-deep` variants of every module

## Routing

Client-side payload work: `../web-xss/`. Bot-delivered state change:
`../web-csrf/`. A `file://` read's targets: `../file-read-primitives/`.
A server-side fetch mistaken for a bot: `../web-ssrf/`.
Budget and escalation: `../LOOP_DISCIPLINE.md`.
