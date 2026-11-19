# web-source-map — references index

Front-end bundle and source-map recon — mine the shipped JavaScript for
endpoints, routes, secrets, flags, and (via `.map` `sourcesContent`)
the original source. Catalogue class: no local verified solve yet.

## The core

| Module | Covers |
|---|---|
| `mechanism.md` / `mechanism-deep.md` | what a bundle and a `.map` are; the v3 spec, `sourcesContent`, scheme handling, traversal rejection |
| `detection.md` / `detection-matrix.md` / `detection-index.md` / `detection-checklist.md` / `detection-surface.md` | bundle/map signatures, framework fingerprints, signal→state→action, the per-file surface |
| `extraction.md` / `extraction-deep.md` | `bundle_miner` usage + the grep grammar for endpoints/params/secrets/flags |
| `source-maps.md` | the `.map` recovery mechanism in detail |
| `secrets.md` | secret candidates, the entropy+context filter, the live-verify rule |
| `frameworks.md` | webpack/CRA/Next/Vite/Vue/Angular bundle and map shapes |
| `workflow.md` / `first-hour.md` / `field-manual.md` | the ordered pass: inventory→map→mine→verify→route |

## The leads → classes

| Module | Covers |
|---|---|
| `per-target.md` / `per-check.md` / `per-route.md` / `per-surface.md` / `per-vector.md` | what each mined artifact/route/surface/vector is worth and which class it feeds |
| `attack-shapes.md` | how the map feeds the exploit |
| `multi-step-chains.md` | map→IDOR, map→secret→auth, map→flag-gate, map→SSRF, map→source→sink |
| `extended-corpus.md` | manifest/`__NEXT_DATA__`/env/comment/sink grep corpus |
| `mechanism-index.md` | the recon sub-mechanisms |

## The discipline

| Module | Covers |
|---|---|
| `evidence-rules.md` | leads vs findings; the verbatim-excerpt and pre-flag gates |
| `falsifiers.md` / `per-falsifier.md` | one kill per claim |
| `negative-results.md` | recording the mined-but-empty bundle |
| `edge-cases.md` | inline maps, obfuscation, WASM, no-map, dev bundles |
| `common-mistakes.md` / `anti-patterns.md` | the ways the pass goes wrong / must not be done |
| `troubleshoot.md` | when the map does not cooperate |
| `evasion.md` | the bundle's resistance + adjacent disclosure |
| `case-studies.md` / `real-world-cases.md` / `verified-chains.md` | published shapes + honest evidence status |

## The reference

| Module | Covers |
|---|---|
| `theory.md` | the shipped-source principle, minification fiction, trust-boundary inversion |
| `glossary.md` | the vocabulary |
| `summary.md` / `onboarding.md` / `checklist.md` / `quick-reference.md` | orientation and the operator lists |
| `preconditions.md` / `class-boundary.md` | when the route applies / what it feeds |
| `common-questions.md` | the FAQ |
| `bundle-mining.md` | the original thin reference |

## The rules

1. the map is **recon, not the exploit** — it names targets, the routed
   class closes them
2. **verify every lead live** — a bundle string is a claim, not a fact
3. a **secret is a candidate** — it leaks only if it authenticates
4. the source is **attacker-controlled** — read it, never execute it; a
   `sources` traversal is rejected, not recovered
5. **catalogue** — no local verified solve; standard published knowledge
