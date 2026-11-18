# Request smuggling reference map

This directory belongs to the canonical `web-request-smuggling` class skill.
Open one named file after the first probe; do not read the whole directory.

## Choose by observed signal

| Signal or task | Open |
|---|---|
| The desync pair names | `desync-taxonomy.md` |
| Finding the desync | `detection.md` |
| The systematic sweep | `desync-detection.md` |
| The pair-vs-oracle table | `smuggle-detection-matrix.md` |
| The classic CL/TE | `cl-te-desync.md` |
| The CRLF folds | `crlf-injection.md` |
| The request-line fold | `request-line-fold.md` |
| The upgrade tunnels | `upgrade-smuggling.md` |
| The h2 downgrades | `http2-smuggling.md` |
| The TE obfuscations | `obfuscation.md` |
| The chunked grammar | `chunked-encoding.md` |
| The CL tricks | `cl-manipulation.md` |
| The header-boundary | `header-boundary.md` |
| The header-level disagreements | `header-smuggling.md` |
| The advanced headers | `advanced-headers.md` |
| The method-boundary | `method-boundary.md` |
| The protocol-version | `protocol-version.md` |
| The h1.0 desync | `http10-desync.md` |
| The Content-Type boundary | `content-type-boundary.md` |
| The virtual-host | `virtual-host.md` |
| The queue-poison | `response-poisoning.md` |
| The client-side CL.0 | `client-side-desync.md` |
| The cookie-steal | `session-hijack.md` |
| The internal routes | `internal-routes.md` |
| The internal-API | `internal-api.md` |
| The filter bypass | `frontend-bypass.md` |
| The cache chain | `cache-poison-via-smuggle.md` |
| The tunnels | `tunneling.md` |
| The protocol-crossing | `protocol-crossing.md` |
| The pipelining | `http-pipelining.md` |
| The queue-management | `queue-management.md` |
| The flag locations | `flag-locations.md` |
| The desync-flags | `desync-flags.md` |
| The async/deferred | `webhook-deferred.md` |
| The second-order | `second-order.md` |
| The blind-smuggle | `blind-smuggle.md` |
| The blind-desync | `blind-desync.md` |
| The CTF shapes | `ctf-shapes.md` |
| The white-box hunt | `whitebox-hunt.md` |
| The proxy-behavior | `proxy-behavior.md` |
| The parser-quirks | `parser-quirks.md` |
| The container-world | `container-world.md` |
| The theory | `theory.md` |
| The theory-primitives | `theory-primitives.md` |
| The theory-boundary | `theory-boundary.md` |
| The theory-parsers | `theory-parsers.md` |
| The theory-smuggle | `theory-smuggle.md` |
| The theory-downgrade | `theory-downgrade.md` |
| The theory-downgrade-deep | `theory-downgrade-deep.md` |
| The desync-mechanism | `desync-mechanism.md` |
| The smuggle-mechanism | `smuggle-mechanism.md` |
| The desync-shapes | `desync-shapes.md` |
| The smuggle-shapes | `smuggle-shapes.md` |
| The ambiguity-catalog | `ambiguity-catalog.md` |
| The desync-corpus | `desync-corpus.md` |
| The desync-ladder | `desync-ladder.md` |
| The smuggle-landing | `smuggle-landing.md` |
| The smuggle-locations | `smuggle-locations.md` |
| The smuggle-payloads | `smuggle-payloads.md` |
| The smuggle-exploitation | `smuggle-exploitation.md` |
| The smuggle-bypass | `smuggle-bypass.md` |
| The smuggle-stability | `smuggle-stability.md` |
| The smuggle-traps | `smuggle-traps.md` |
| The smuggle-cases | `smuggle-cases.md` |
| The smuggle-env | `smuggle-env.md` |
| The smuggle-lifecycle | `smuggle-lifecycle.md` |
| The smuggle-readback | `smuggle-readback.md` |
| The smuggle-readback-deep | `smuggle-readback-deep.md` |
| The desync-readback | `desync-readback.md` |
| The desync-readback-deep | `desync-readback-deep.md` |
| The smuggle-evidence | `smuggle-evidence.md` |
| The detection-oracle | `detection-oracle.md` |
| The detection-payloads | `detection-payloads.md` |
| The exploit-templates | `exploit-templates.md` |
| The probe-sequences | `probe-sequences.md` |
| The desync-workflow | `desync-workflow.md` |
| The smuggle-workflow | `smuggle-workflow.md` |
| The workflow | `workflow.md` |
| The extended-corpus | `extended-corpus.md` |
| The attack-defense | `attack-defense.md` |
| The evidence bar | `evidence-rules.md` |
| The failure modes | `common-mistakes.md` |
| The denied conditions | `denied-conditions.md` |
| The real-world cases | `real-world-cases.md` |
| The error-analysis | `error-analysis.md` |
| The tool wrappers | `tooling.md` |
| The payload corpus | `payload-dictionary.md` |
| The cheatsheet | `cheatsheet.md` |
| The field-manual | `field-manual.md` |
| The writeup | `smuggle-writeup.md` |
| The theory-index | `theory-index.md` |
| The theory-summary | `theory-summary.md` |
| The theory-full | `theory-full.md` |
| The desync-summary | `desync-summary.md` |
| The desync-checklist | `desync-checklist.md` |

## Loading rule

The `../SKILL.md` file is enough for routine recognition and the first probe.
Open a file here only when the desync needs a concrete byte sequence or a
confirmation wording.

Every technique here was distilled from a field note in `../field-notes.md`;
the request shapes below are the ones that actually worked on a live target.
