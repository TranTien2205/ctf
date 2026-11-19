---
name: web-user-enum
description: >
  Action-oriented depth skill for User enumeration / auth throttling. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: web-auth-session, web-logic-flaw.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [web, user-enum, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# User enumeration / auth throttling

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

one known-good username and one obviously-bad username against the same form, then the same bad username twice — compare message, status, and timing across the three

**Falsifier** — the observation that closes this class: identical response text, status, and timing distribution for known-good, known-bad, and repeated-bad attempts, including the timing of the password-verification path
## Recognise

A login, registration, reset or contact form whose response differs by whether
the account exists. Three channels carry the difference: the error text
("unknown user" vs "wrong password"), the status code or redirect target, and
the response time — hashing runs only for users that exist.

## Confirm safely

Probe with accounts you control plus one obviously-bad name. A repeatable
difference across three tries is a lead, not a finding — record the delta in
bytes or milliseconds and quote both responses verbatim before confirming.

Never probe enumeration by spraying a wordlist of real usernames on a shared
target; rate limiting is itself the thing under test.

## What the differential buys

| Channel | Exploit |
|---|---|
| Distinct error text | direct enumeration — script one request per candidate |
| Timing only | the server hashes known users' passwords and short-circuits unknown ones |
| Same text, same time, still leaks | check Set-Cookie, redirect target, or an embedded boolean in the body |

A found account is the opening: weak password policies, reset-flow bugs, or
credential stuffing against it are usually the intended chain.

## Traps

- A generic error that LOOKS uniform may still differ by a whitespace or a
  hidden field — diff the raw bodies, not the rendered page.
- Timing noise swallows sub-10ms deltas on a remote target; measure the same
  pair alternately several times and compare medians.
- Absent rate limiting on the auth path is itself reportable, but only after a
  bounded burst shows no throttle AND the account is not locked — a locked
  account is evidence of the control, not its absence.

## Operational probe

```bash
# known-good vs known-bad, same form fields
curl -i -X POST -d 'user=admin&pass=x' "$BASE/login" > /tmp/good
curl -i -X POST -d 'user=zzz-no-such&pass=x' "$BASE/login" > /tmp/bad
diff /tmp/good /tmp/bad
```

`tools/web/enum_probe.py` does the diff for you: one `--known-user`
against four random usernames, measuring status / body signature+length /
elapsed against the random spread. It reports which channel separates
them (verbatim excerpts attached); a uniform result is a real negative.

## Routing

Shares signals with: `../web-auth-session/`, `../web-logic-flaw/`. Check those before committing to this one.

Depth, one named file at a time — the corpus index is
`skills/web-user-enum/references/index.md`; the map is
`skills/web-user-enum/references/README.md`.

**Start here** — `references/onboarding.md`, `references/first-hour.md`,
`references/preconditions.md`, `references/quick-reference.md`,
`references/quick-map.md`, `references/checklist.md`.

**The mechanism** — `references/mechanism.md` +
`references/mechanism-deep.md`/`mechanism-index.md`/`mechanism-map.md`/
`mechanism-catalogue.md`, `references/theory.md`/`theory-deep.md`,
`references/channels.md`/`channels-deep.md` (the four oracle channels),
`references/form-surface.md`/`form-surface-deep.md` (the endpoint
inventory).

**Detection** — `references/detection.md` + `-deep`/`-index`/`-matrix`/
`-checklist`/`-surface`/`-playbook`/`-catalogue`/`-map`, and the
per-channel protocols `references/channel-body.md`, `channel-status.md`,
`channel-side.md`, `timing-oracle.md`. Per form:
`references/login-enum.md`/`-deep`, `register-reset-enum.md`/`-deep`,
`api-enum.md`/`-deep` (JSON/REST/GraphQL), `sso-and-federated.md`,
`framework-matrix.md` (Django/Flask/Express/Rails/Laravel/Spring/ASP.NET/WP).

**Exploit** — `references/exploitation.md`/`-deep` (confirmed-name →
flag chains), `attack-shapes.md`/`-deep`, `multi-step-chains.md`/`-deep`,
`case-studies.md`/`-deep`, `real-world-cases.md`/`-deep`, `scenarios.md`,
`worked-examples.md`, `username-sources.md`/`-deep`, `payload-variants.md`,
`payload-dictionary.md`, `extended-corpus.md`, `probe-catalogue.md`,
`probe-map.md`.

**The throttle** — `references/throttling.md`/`-deep` (the loop-bound
taxonomy), `rate-limit-bypass.md`/`-deep` (every counter-reset).

**The pass** — `references/workflow.md` + `-deep`/`-map`/`-checklist`/
`-playbook`/`-catalogue`, `recon-order.md`, `field-manual.md`/`-deep`,
`operator-notes.md`, `closing-notes.md`, `decision-table.md`,
`decision-catalogue.md`.

**Per-axis maps** — `references/per-form.md`, `references/per-surface.md`,
`references/per-check.md`, `references/per-endpoint.md`,
`references/per-endpoint-catalogue.md`, `references/per-vector.md`,
`references/per-mechanism.md`, `references/per-channel.md`,
`references/per-target.md`, `references/per-falsifier.md`,
`references/per-boundary.md`, `references/per-mechanism-deep.md` — each
plus its `-deep` variant.

**Evidence** — `references/evidence-rules.md` + `-deep`/`-playbook`/
`-catalogue` variants, `references/falsifiers.md` + `-deep` +
`references/falsifier-map.md`, `references/verification-protocol.md`,
`references/negative-results.md` + `-deep` +
`references/negative-map.md`, `references/lead-grammar.md`,
`references/verified-chains.md` (catalogue-honest: none yet).

**Traps & boundaries** — `references/edge-cases.md` + `-deep` +
`references/edge-cases-map.md`, `references/common-mistakes.md` + `-deep`,
`references/anti-patterns.md`, `references/troubleshoot.md` + `-deep`,
`references/common-questions.md` + `-deep` +
`references/common-questions-map.md`, `references/class-boundary.md` +
`references/per-boundary.md`, `references/evasion.md` + `-deep`.

**Reference** — `references/glossary.md` + `-deep`,
`references/summary.md` + `-deep`, `references/field-notes-deep.md` (the
skill-root ledger is `field-notes.md` in this directory),
`references/differentials.md` + `-deep`, `references/detection-map.md`,
`references/index.md`.

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
