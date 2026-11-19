# Race condition reference map

This is the canonical reference entry for `web-race-condition`. Open it after
the first interleaving probe, then choose one named file. Do not use
deserialization material as the race-condition depth reference.

| Signal or task | Next material |
|---|---|
| Read/write gap and two requests can overlap | `interleaved-writes.md` — the canonical starting reference |
| Token/limit/redeem window | `check-then-act-alphabet.md` — the A-L check index; `per-check-deep.md` — the exhaustive playbooks |
| No attributable before/after state change | stop and record inconclusive; do not flood |

`interleaved-writes.md` was distilled from the confirmed field notes in
`../field-notes.md`.

---

## The mechanism

| File | What it covers |
|---|---|
| `interleaved-writes.md` | the canonical start: read-modify-write, two-request interleave, the crossed state |
| `read-modify-write.md` | the RMW window: read → work → write, why a transaction alone is not a close |
| `check-then-act-alphabet.md` | the A-L index of check-then-act windows |
| `delivery-mechanics.md` | burst vs interleave vs single-packet vs stall; the delivery-picker |
| `theory.md` | why the window exists: isolation, scheduling, the commit order |
| `theory-deep.md` | the exhaustive theory: scheduling models, isolation levels, the anomaly catalogue |
| `window-catalogue.md` | every window shape indexed by what separates the read and the write |
| `interleave-patterns.md` | the delivery patterns: barrier, last-byte stall, `--url-b`, startup hammer |

## The check-then-act alphabet — per-check playbooks

| File | What it covers |
|---|---|
| `check-then-act-alphabet.md` | the A-L index |
| `per-check-balance.md` | B — debit/transfer/convert: the balance floor |
| `per-check-token.md` | C — single-use/verify/reset: the crossed token |
| `per-check-other.md` | the less-common windows: rate limiter, idempotency, lock, version, quota, role |
| `per-check-deep.md` | the exhaustive playbooks — schema, window, probe, crossed state, close, variants |

## Detection and audit

| File | What it covers |
|---|---|
| `detection.md` | the recon grep, the response signals, the window audit |
| `detection-deep.md` | the exhaustive detection: per-framework greps, the response-signal matrix |
| `detection-index.md` | the signal → file index |
| `detection-surface.md` | the endpoint → check → probe map |
| `detection-matrix.md` | the row-per-signal matrix: signal → mechanism → probe |
| `whitebox-hunt.md` | the source greps, the ORM patterns, the framework audits |
| `field-manual.md` | the operational reference: setup → inventory → window → probe → record |
| `field-manual-deep.md` | the exhaustive how-to: every command, every branch, every read |

## Per-* maps

| File | What it covers |
|---|---|
| `per-framework.md` | Django/Flask/Rails/Express/Spring/Laravel/Gin/PHP — the ORM and lock idioms |
| `per-mechanism.md` | the mechanism → window → probe map |
| `per-boundary.md` | the trust-boundary map: where the window lives by tier |
| `per-vector.md` | the input-vector map: header, body, cookie, step, file |
| `per-route.md` | the route → record → check → probe map |
| `per-surface.md` | the surface → check map |
| `per-falsifier.md` | the defence that closes each window — and the grep that confirms it |

## Exploitation and chains

| File | What it covers |
|---|---|
| `exploitation.md` | the primitive → gate → flag decision tree |
| `exploitation-deep.md` | the exhaustive primitive → gate → flag guide |
| `exploitation-playbook.md` | the 14-step decision flow from window to flag |
| `exploitation-shapes.md` | the exploit shapes by primitive |
| `multi-step-chains.md` | the race → sink chains: the primitive buys the foothold |
| `verified-chains.md` | the two verified cards: ApexSurvive + SSOS |
| `case-studies.md` | the canonical cases: the redeem, the transfer, the token |
| `case-studies-deep.md` | the exhaustive cases: the actor race, the flow race, the worker |
| `real-world-cases.md` | the real-world patterns: the bank, the vote, the invite |
| `payload-variants.md` | the request variants by check and delivery |
| `extended-corpus.md` | the deep reference material beyond the playbooks |

## Timing and oracle

| File | What it covers |
|---|---|
| `timing-oracle.md` | the pathological-widen technique; the timing delta as the signal |

## Discipline

| File | What it covers |
|---|---|
| `workflow.md` | the contract → inventory → window → probe → record loop |
| `workflow-deep.md` | the exhaustive workflow with every branch |
| `workflow-checklist.md` | the printable checklist |
| `evidence-rules.md` | the baseline, the split, `max_in_flight`, the state read, the attribution |
| `evidence-rules-deep.md` | the exhaustive evidence standard |
| `falsifiers.md` | the close catalogue and the falsifier verdict |
| `negative-results.md` | the inconclusive/falsifier record and the kill-map write |
| `negative-results-deep.md` | the exhaustive negative-result record |
| `edge-cases.md` | the edge cases: one-shot, dirty state, shared instance, the response cache |
| `edge-cases-deep.md` | the exhaustive edge cases |
| `common-mistakes.md` | the discipline failures: flood, no-baseline, wrong split, no attribution |
| `common-mistakes-deep.md` | the exhaustive mistakes |
| `common-questions.md` | the FAQ |
| `common-questions-deep.md` | the exhaustive FAQ |
| `troubleshoot.md` | the failure modes and the fixes |
| `troubleshoot-deep.md` | the exhaustive troubleshooting |
| `evasion.md` | the WAF/limiter/serialization evasion |
| `class-boundary.md` | race vs logic-flaw, race vs deserialization, the class split |
| `glossary.md` | the vocabulary: window, crossed state, attribution, serial baseline |
| `summary.md` | the one-page recap |
| `race-catalogue.md` | the complete endpoint-indexed reference |
| `checklist.md` | the printable race-condition checklist |
| `per-falsifier.md` | the defence that closes each window — and the grep that confirms it |
| `per-check-deep.md` | the exhaustive per-check playbooks — schema, window, probe, crossed state, close |
| `detection-matrix.md` | the row-per-signal matrix: signal → mechanism → probe |
| `common-questions-deep.md` | the exhaustive FAQ |
| `field-manual-deep.md` | the exhaustive how-to: every command, every branch, every read |
| `exploitation-deep.md` | the exhaustive primitive → gate → flag guide |
| `exploitation-playbook.md` | the 14-step decision flow from window to flag |
| `exploitation-shapes.md` | the exploit shapes by primitive |
| `multi-step-chains.md` | the race → sink chains: the primitive buys the foothold |
| `verified-chains.md` | the two verified cards: ApexSurvive + SSOS |
| `case-studies.md` | the canonical cases: the redeem, the transfer, the token |
| `case-studies-deep.md` | the exhaustive cases: the actor race, the flow race, the worker |
| `real-world-cases.md` | the real-world patterns: the bank, the vote, the invite |
| `payload-variants.md` | the request variants by check and delivery |
| `extended-corpus.md` | the deep reference material beyond the playbooks |
| `workflow.md` | the contract → inventory → window → probe → record loop |
| `workflow-deep.md` | the exhaustive workflow with every branch |
| `workflow-checklist.md` | the printable workflow checklist |
| `evidence-rules.md` | the baseline, the split, `max_in_flight`, the state read, the attribution |
| `evidence-rules-deep.md` | the exhaustive evidence standard |
| `falsifiers.md` | the close catalogue and the falsifier verdict |
| `negative-results.md` | the inconclusive/falsifier record and the kill-map write |
| `negative-results-deep.md` | the exhaustive negative-result record |
| `edge-cases.md` | the edge cases: one-shot, dirty state, shared instance, the response cache |
| `edge-cases-deep.md` | the exhaustive edge cases |
| `common-mistakes.md` | the discipline failures: flood, no-baseline, wrong split, no attribution |
| `common-mistakes-deep.md` | the exhaustive mistakes |
| `common-questions.md` | the FAQ |
| `troubleshoot.md` | the failure modes and the fixes |
| `troubleshoot-deep.md` | the exhaustive troubleshooting |
| `checklist.md` | the printable race-condition checklist |
| `quick-reference.md` | the one-page cheat sheet |

## The two verified anchors

- **`knowledge/chains/htb-apexsurvive-profile-race-template-literal-xss-template-overwrite-rce.json`** —
  the crossed verification-token race (profile-update A + profile-update B →
  token A delivered to B), pivoting to a stored-XSS template-literal → a
  parseable-PDF file-write → a template overwrite → RCE. Do not overwrite server
  configuration or imported modules — the card names the bricking risk.
- **`knowledge/chains/htb-ssos-oauth-registration-race-cookie-swap-json-csrf.json`** —
  the registration race for a fixed bot account at app-startup (the actor fires
  on a schedule), pivoting to a cookie-swap through a text/plain cross-site
  JSON submission → the shared OAuth/session confusion → a flag-submit into an
  account controlled by the tester.
