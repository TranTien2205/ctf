# web-host-header — references

Host / forwarded-header attacks: the app or middleware trusts `Host`,
`X-Forwarded-*`, `Forwarded`, or a `X-*-URL`/`*-Path` rewrite header and turns
it into a decision or a sink.

| If | Open |
|---|---|
| **Routing / recognition** | |
| Need the whole detection surface at a glance | `detection-index.md` |
| Which header, which check, which sink | `header-pairs.md` |
| Core theory | `host-header.md`, `theory.md`, `theory-deep.md` |
| Forwarded headers specifically | `forwarded-headers.md` |
| Rewrite headers specifically | `rewrite-headers.md` |
| **Detection** | |
| Detection method + first probes | `detection.md`, `detection-deep.md` |
| Detection matrix by check/route/framework/proxy | `per-check.md`, `per-route.md`, `per-header.md`, `per-boundary.md`, `per-vector.md`, `per-mechanism.md`, `per-surface.md` |
| Per-proxy and per-CDN behavior | `per-proxy.md`, `per-cdn.md` |
| Per-framework behavior | `per-framework.md` |
| **Payloads** | |
| Payload dictionary + variants | `payload-dictionary.md`, `payload-variants.md`, `extended-corpus.md`, `header-abuse.md` |
| **Exploitation** | |
| Exploit shapes + chains | `exploitation.md`, `exploitation-shapes.md`, `multi-step-chains.md`, `verified-chains.md` |
| Case studies | `case-studies.md`, `case-studies-deep.md` |
| **Workflow** | |
| Black-box and white-box workflow | `workflow.md`, `workflow-deep.md`, `field-manual.md`, `field-manual-deep.md` |
| White-box source hunting | `whitebox-hunt.md` |
| **Discipline** | |
| Evidence rules, falsifiers, negatives | `evidence-rules.md`, `evidence-rules-deep.md`, `per-falsifier.md`, `negative-results.md`, `negative-results-deep.md` |
| Common mistakes + questions | `common-mistakes.md`, `common-mistakes-deep.md`, `common-questions.md` |
| Edge cases | `edge-cases.md` |
| Evasion + troubleshooting | `evasion.md`, `troubleshoot.md`, `troubleshoot-deep.md` |
| Class boundary (vs parser-differential, cache-poisoning) | `class-boundary.md` |
| Reference summary + glossary | `summary.md`, `glossary.md` |

General guidance — no solved chain in this toolkit yet.
