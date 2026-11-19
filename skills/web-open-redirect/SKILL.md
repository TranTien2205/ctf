---
name: web-open-redirect
description: >
  Action-oriented depth skill for Open redirect. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: web-ssrf, web-oauth-sso.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [web, open-redirect, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Open redirect

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

one external destination in the redirect parameter, following the response Location header exactly

**Falsifier** — the observation that closes this class: the destination is validated against an allowlist or forced to a relative path
## Recognise

A parameter that names where to go next: a post-login destination, a callback, a
continue URL. The response is a redirect and the parameter is inside its
`Location` header.

## Confirm

Send one external destination and inspect the exact `Location` header without
following it. Repeat once with an encoded or parser-boundary form only if the
first result is inconclusive. Confirmation requires the server to emit a
redirect to the attacker-controlled destination.

## Why it matters in a chain

Alone it is low value. It becomes the chain when it feeds something that trusts
the destination: an OAuth redirect target, a server-side fetch, or a bot that
will visit whatever it is handed. See `../web-oauth-sso/` and `../web-ssrf/`.

## Traps

- A validator that only checks a prefix is satisfied by a hostname that starts
  with the allowed value. One that only blocks `//` is satisfied by backslashes
  or encoded forms, depending on which parser resolves the URL.
- A redirect that is immediately followed by a safe allowlist or a fixed
  relative path is not open; record the exact header before escalating.

## Routing

Shares signals with: `../web-ssrf/`, `../web-oauth-sso/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/ctf-web/auth-and-access.md`

| Signal or task | Open |
|---|---|
| Any redirect-parameter question | `references/filter-bypasses.md` |
| the mechanism model | `references/mechanism.md` `references/mechanism-deep.md` `references/theory.md` |
| the detection signals | `references/detection.md` `references/detection-deep.md` `references/detection-matrix.md` `references/detection-signals.md` `references/detection-catalogue.md` |
| the param vocabulary | `references/param-inventory.md` `references/per-param.md` `references/per-endpoint.md` `references/per-surface.md` `references/detection-surface.md` |
| the bypass arms | `references/filter-bypass-deep.md` `references/per-check.md` `references/per-vector.md` `references/per-boundary.md` `references/per-target.md` `references/payload-dictionary.md` `references/payload-variants.md` `references/payload-map.md` `references/boundary-map.md` `references/encoding-attacks.md` `references/evasion.md` `references/extended-corpus.md` |
| the parser gaps | `references/parser-differentials.md` `references/framework-matrix.md` |
| the carriers | `references/client-side.md` `references/stored-and-referer.md` `references/per-channel.md` `references/per-mechanism.md` `references/edge-cases.md` |
| the chain routes | `references/chain-routes.md` `references/per-route.md` `references/multi-step-chains.md` `references/attack-shapes.md` `references/exploitation.md` `references/second-order.md` |
| the evidence rules | `references/evidence-rules.md` `references/evidence-rules-deep.md` `references/detection-verdicts.md` |
| the falsifiers | `references/falsifiers.md` `references/falsifiers-deep.md` `references/per-falsifier.md` `references/detection-verdicts.md` |
| the negatives | `references/negative-results.md` `references/negative-results-deep.md` `references/negative-map.md` |
| the workflow | `references/workflow.md` `references/workflow-deep.md` `references/field-manual.md` `references/first-hour.md` `references/recon-order.md` `references/detection-workflow.md` `references/detection-playbook.md` |
| the checklists | `references/checklist.md` `references/checklist-deep.md` `references/detection-checklist.md` |
| the quick-ref | `references/quick-reference.md` `references/quick-reference-deep.md` `references/decision-table.md` `references/decision-catalogue.md` |
| the onboarding | `references/onboarding.md` `references/onboarding-deep.md` `references/operator-notes.md` `references/lead-grammar.md` |
| the edge/trap | `references/edge-cases.md` `references/common-mistakes.md` `references/common-mistakes-deep.md` `references/anti-patterns.md` `references/troubleshoot.md` `references/troubleshoot-deep.md` `references/common-questions.md` `references/common-questions-deep.md` |
| the cases | `references/case-studies.md` `references/real-world-cases.md` |
| the preconditions | `references/preconditions.md` `references/preconditions-deep.md` `references/class-boundary.md` |
| the probes | `references/probe-catalogue.md` `references/probe-map.md` `references/detection-playbook.md` |
| the indexes | `references/README.md` `references/detection-index.md` `references/detection-index-deep.md` `references/detection-map.md` `references/mechanism-index.md` `references/mechanism-map.md` `references/per-surface-map.md` `references/negative-map.md` |
| the honest state | `references/verified-chains.md` `references/field-notes-deep.md` `references/summary.md` `references/glossary.md` |

## stop_conditions

- `stop when` every canary + bypass arm on a surface returns a verbatim
  `Location:` to a safe/allowlisted/forced-relative destination — the
  class falsifier
- `budget`: five probes per mechanism (the canary + the arm family on one
  surface), twenty-five per challenge — `../LOOP_DISCIPLINE.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Operational probe

Do not follow the redirect. Send one external destination and inspect only the
response headers:

```bash
curl -i --max-time 10 \
  "$BASE/login?next=https%3A%2F%2Fattacker.invalid%2Flanding"
```

`tools/web/redirect_probe.py` sweeps the usual parameter names (or one
`--param`) and the boundary forms — `//host`, `%5c`, userinfo,
subdomain — with `follow=False`, reporting any case whose `Location`
resolves to the canary host as a candidate with the verbatim header.

Record the exact `Location` value and status. Then test one parser-boundary
variant only if the first destination is rejected: a leading `//`, encoded
slash, backslash, userinfo form, or a scheme-relative URL must be chosen from
the URL parser behavior observed in the application. Confirmation requires the
server to emit an attacker-controlled absolute destination; a client-side
navigation or a safe relative path is not proof.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
