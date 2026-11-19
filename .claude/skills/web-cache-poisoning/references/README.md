# Cache poisoning reference map

This directory belongs to the canonical `web-cache-poisoning` class skill.
Open one named file after the first probe; do not read the whole directory.

## Choose by observed signal

| Signal or task | Open |
|---|---|
| A response the cache keys one way but the app keys another | `cache-key-differentials.md` |
| Stored/uploaded content is served to a context it was not written for | `stored-content-confusion.md` |

## Detection — does a cache exist, and what is its surface

| Task | Open |
|---|---|
| The first probe — does a cache exist | `detection.md` |
| A deep detection sweep | `detection-deep.md` |
| The complete surface map | `detection-surface.md` |
| Every detection signal, indexed | `detection-index.md` |
| The detection sequence, step by step | `detection-workflow.md` |
| The detection checklist | `detection-checklist.md` |
| The signal-to-surface map | `detection-map.md` |
| The source grep paths | `whitebox-hunt.md` |

## The key — what is keyed, what is unkeyed

| Task | Open |
|---|---|
| The cache key's composition | `cache-key-analysis.md` |
| The key's deep analysis | `key-analysis-deep.md` |
| The key's complete map | `keymap.md` |
| The keyed-vs-unkeyed param question | `keyed-param.md` |
| The Vary header and the status signals | `cache-status-deep.md` |
| Which pages are cached | `cacheable.md` |

## The unkeyed input — the poisoning vector

| Task | Open |
|---|---|
| The unkeyed-input surface | `unkeyed-inputs.md` |
| The unkeyed-input mechanics | `unkeyed-deep.md` |
| Every header the cache may ignore | `header-dictionary.md` |
| Every param and path | `param-dictionary.md` |
| Every unkeyed input | `input-dictionary.md` |
| Every probe | `probe-dictionary.md` |
| Every request shape | `request-shapes.md` |
| The path-normalization boundary | `evasion.md` |

## The stored response — the deception

| Task | Open |
|---|---|
| The stored-response confusions | `deception-shapes.md` |
| The deception mechanics, exhaustively | `deception-deep.md` |
| The stored copy's content | `stored-content.md` |
| The injected payload's store | `injection-payloads.md` |
| The stored-content payloads | `payload-variants.md` |
| The payload corpus | `payload-dictionary.md` |
| The delivery — the stored copy's serve | `delivery-shapes.md` |
| The persistence and the blast | `ttl-and-blast.md` |

## The attack — the sequence and the named plays

| Task | Open |
|---|---|
| The exploitation sequence | `exploitation.md` |
| The end-to-end plays | `exploitation-playbook.md` |
| The attack sequence, step by step | `exploitation-workflow.md` |
| The named attacks | `attack-shapes.md` |
| The multi-step chains | `multi-step-chains.md` |
| The mechanism, at the protocol level | `mechanism.md` |
| The theory, deeply | `theory-deep.md` |
| The theory | `theory.md` |

## The confirmation — the evidence standard

| Task | Open |
|---|---|
| The evidence standard | `evidence-rules.md` |
| The evidence, exhaustively | `evidence-deep.md` |
| The readback oracles | `readback-oracles.md` |
| The confirmation map | `confirm-map.md` |
| The negative results | `negative-results.md` |
| The negative map | `negative-map.md` |
| The audit checklist | `audit-checklist.md` |

## The boundary — is this a cache-poisoning

| Task | Open |
|---|---|
| The class boundary | `class-boundary.md` |
| The boundary, exhaustively | `boundary-deep.md` |

## The per-stack surface — which cache layer

| Task | Open |
|---|---|
| The per-vendor cache layer | `cdn-and-proxy.md` |
| The per-framework cache layer | `frameworks-deep.md` |
| The framework matrix | `framework-matrix.md` |

## The viewer — the bot and the privileged context

| Task | Open |
|---|---|
| The bot surface | `browser-and-bot.md` |

## The workflow — the sequence end to end

| Task | Open |
|---|---|
| The complete workflow | `workflow.md` |
| The deep workflow | `workflow-deep.md` |
| The workflow map | `workflow-map.md` |
| The field manual | `field-manual.md` |

## The cases — the named shapes

| Task | Open |
|---|---|
| The case studies | `case-studies.md` |
| The case studies, exhaustively | `case-studies-deep.md` |
| The verified card | `verified-chains.md` |
| The verified card, exhaustively | `chain-cards-deep.md` |
| The real-world shapes | `real-world-cases.md` |
| The CTF shapes | `ctf-shapes.md` |
| The extended corpus | `extended-corpus.md` |

## The troubleshooting — why a probe returned nothing

| Task | Open |
|---|---|
| The failure modes | `troubleshoot.md` |
| The failure modes, deeply | `troubleshoot-deep.md` |
| The common mistakes | `common-mistakes.md` |
| The common questions | `common-questions.md` |
| The common questions, exhaustively | `common-questions-deep.md` |
| The edge cases | `edge-cases.md` |
| The error analysis | `error-analysis.md` |
| The cheatsheet | `cheatsheet.md` |
| The glossary | `glossary.md` |
| The summary | `summary.md` |

## Loading rule

The `../SKILL.md` file is enough for routine recognition and the first probe.
Open a file here only when the poisoning needs a concrete key-mismatch probe
or a confirm wording.

Both techniques were distilled from field notes in `../field-notes.md`.
