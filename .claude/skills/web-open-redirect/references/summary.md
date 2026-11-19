# Summary — the open-redirect class in one page

## The class

```text
a request value lands in a Location:/meta/JS redirect; the server emits an
attacker-controlled DESTINATION; the client follows it cross-origin.
```

## The oracle

```text
a verbatim Location: carrying the canary — the evidence:
  Location: https://attacker.invalid   <- the absolute
  Location: //evil.com                 <- the scheme-relative
  Location: https://target.com.evil.com <- the subdomain-gap
```

## The falsifier

```text
the destination is validated against an allowlist or forced to a relative
path — Location: <safe> on EVERY canary + bypass arm
```

## The mechanism

```text
param -> filter -> resolution -> carrier -> navigation -> destination
the filter reads ONE parse; the browser resolves ANOTHER — the bypass is
the parser-differential — the `//`/`\`/`@`/`%5c`/encoded/unicode arms
```

## The corpus

| The question | The file |
|---|---|
| the model | `mechanism.md`, `mechanism-deep.md` |
| the detection | `detection.md`, `detection-deep.md`, `detection-matrix.md` |
| the bypass arms | `filter-bypass-deep.md`, `payload-dictionary.md`, `payload-variants.md`, `per-vector.md`, `per-check.md` |
| the parser-gaps | `parser-differentials.md`, `encoding-attacks.md` |
| the carriers | `client-side.md`, `stored-and-referer.md`, `edge-cases.md` |
| the surfaces | `param-inventory.md`, `per-endpoint.md`, `per-surface.md` |
| the chains | `chain-routes.md`, `per-route.md`, `multi-step-chains.md` |
| the evidence | `evidence-rules.md`, `evidence-rules-deep.md` |
| the falsifiers | `falsifiers.md`, `falsifiers-deep.md`, `per-falsifier.md` |
| the negatives | `negative-results.md`, `negative-results-deep.md`, `negative-map.md` |
| the workflow | `workflow.md`, `workflow-deep.md`, `field-manual.md`, `first-hour.md` |
| the discipline | `checklist.md`, `anti-patterns.md`, `common-mistakes.md` |
| the reference | `theory.md`, `glossary.md`, `class-boundary.md`, `framework-matrix.md` |
| the cases | `case-studies.md`, `real-world-cases.md` |
| the troubleshoot | `troubleshoot.md`, `common-questions.md` |
| the indexes | `detection-index.md`, `detection-map.md`, `detection-catalogue.md`, `detection-signals.md`, `detection-surface.md`, `detection-verdicts.md`, `detection-playbook.md`, `detection-checklist.md`, `detection-workflow.md`, `mechanism-index.md` |
| the honest state | `verified-chains.md`, `field-notes-deep.md` |

## The one-line contract

```text
send one external destination; read the verbatim Location; a canary in
the Location confirms; a safe Location on every arm is the falsifier;
the chain's laundered-trust is the flag-path
```

## The catalogue honesty

```text
CATALOGUE — no local solve. The corpus is published knowledge; a verbatim
Location:-canary on a live target is the local confirm that upgrades it.
```
