# web-user-enum — reference corpus map

User enumeration is a differential measurement: `KNOWN` vs `FAKE` vs
`FAKE2` (the three arms) across four oracle channels on every
account-touching form. The class also owns the auth-throttling finding.
`index.md` is the question-keyed corpus index; this file is the
reading-order map.

## Reading order

1. `onboarding.md` — the class in one page
2. `mechanism.md` — the verify-short-circuit + the four channels
3. `channels.md` — body / status+redirect / timing / side-artifact
4. `detection.md` + `detection-matrix.md` — the signal inventory
5. `workflow.md` — the six ordered passes
6. `login-enum.md` / `register-reset-enum.md` / `api-enum.md` — the forms
7. `throttling.md` / `rate-limit-bypass.md` — the loop-bound
8. `exploitation.md` / `multi-step-chains.md` — the confirmed-name → flag
9. `evidence-rules.md` / `falsifiers.md` / `verification-protocol.md` —
   the three-arm verify and the kill conditions
10. `negative-results.md` / `edge-cases.md` / `common-mistakes.md` /
    `troubleshoot.md` — the dead ends and traps

## The four-channel spine

| Channel | Base | Deep | Per |
|---|---|---|---|
| body/text+residual | `channel-body.md` | `channels-deep.md` | `per-channel-deep.md` |
| status + `Location` | `channel-status.md` | `channels-deep.md` | `per-channel-deep.md` |
| timing (the hash gap) | `timing-oracle.md` | `channels-deep.md` | `per-channel-deep.md` |
| side-artifact (cookie/send/lock) | `channel-side.md` | `channels-deep.md` | `per-channel-deep.md` |

## The direct oracles

`check-username`/`available`/`exists`/`taken`/`user-exists` →
`form-surface.md`/`form-surface-deep.md`; REST `users/{id}` →
`api-enum.md`; GraphQL `userByEmail`/`checkUser`/`userExists`/`login` →
`api-enum-deep.md`; register-taken → `register-reset-enum.md`; reset-send →
`register-reset-enum.md`; SAML/OAuth federated → `sso-and-federated.md`;
the WP `?author=N`/`wp-json` → `framework-matrix.md`.

## The mechanism index

`mechanism-index.md`/`mechanism-index-deep.md`/`mechanism-map.md`/
`mechanism-catalogue.md` — the 18 existence-oracle + 8 throttle
sub-mechanisms, each a named bounded measurement.

## The per-axis maps

`per-form`/`per-surface`/`per-check`/`per-endpoint`/`per-endpoint-catalogue`/
`per-vector`/`per-mechanism`/`per-channel`/`per-target`/`per-falsifier`/
`per-boundary`/`per-mechanism-deep` — each a `name → protocol → verdict`
table, most with a `-deep` variant.

## Evidence and discipline

`evidence-rules`/`evidence-deep`/`evidence-playbook`/`evidence-catalogue`,
`falsifiers`/`falsifiers-deep`/`falsifier-map`/`per-falsifier`,
`verification-protocol` (the three arms), `negative-results`/
`negative-results-deep`/`negative-map`, `lead-grammar`, `field-notes-deep` (the
ledger is `../field-notes.md`), `verified-chains` (catalogue — none
verified here yet).

## Payloads and probes

`payload-variants`/`payload-dictionary`/`extended-corpus` (the tokens),
`probe-catalogue`/`probe-map` (the commands), `decision-table`/
`decision-catalogue` (the branches), `attack-shapes`/`attack-shapes-deep`
(the primitives), `exploitation`/`exploitation-deep`/`multi-step-chains`/
`multi-step-chains-deep` (the routes to the flag).

## Reference

`theory`/`theory-deep`, `glossary`/`glossary-deep`, `summary`/`summary-deep`,
`workflow`/`workflow-deep`/`workflow-map`/`workflow-checklist`/
`workflow-playbook`/`workflow-catalogue`, `recon-order`, `checklist`/
`checklist-deep`, `quick-reference`/`quick-reference-deep`/`quick-map`,
`field-manual`/`field-manual-deep`, `operator-notes`, `closing-notes`,
`first-hour`/`first-hour-deep`, `onboarding`/`onboarding-deep`,
`preconditions`/`preconditions-deep`, `edge-cases`/`edge-cases-deep`/
`edge-cases-map`, `common-mistakes`/`common-mistakes-deep`, `anti-patterns`,
`troubleshoot`/`troubleshoot-deep`, `common-questions`/`common-questions-deep`/
`common-questions-map`, `class-boundary`/`per-boundary`, `evasion`/
`evasion-deep`, `case-studies`/`case-studies-deep`, `real-world-cases`/
`real-world-deep`, `scenarios`, `worked-examples`, `username-sources`/
`username-sources-deep`, `framework-matrix`, `sso-and-federated`,
`differentials`/`differentials-deep`, `detection-*` (13 files),
`mechanism-*`, `per-*`.
