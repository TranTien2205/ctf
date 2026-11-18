# Prototype pollution reference map

This directory belongs to the canonical `web-prototype-pollution` class skill.
Open one named file after the first probe; do not read the whole directory.

## Choose by observed signal

| Signal or task | Open |
|---|---|
| A JSON body is merged into a server-side object (Node/JS) | `server-side-merge.md` |
| The target is Python and merge paths touch `__class__`, `__init__`, `__globals__` | `class-pollution-python.md`, `python-paths.md` |
| Pollution happens in the browser via URL or client-side merge | `client-side-dom.md`, `dom-clobbering-deep.md`, `pollution-to-xss.md` |
| `__proto__` is filtered | `constructor-path.md`, `proto-keys-corpus.md`, `defenses-bypass.md` |
| The merge is a document-store operator (`$rename`/`$set`/path) | `mongoose-operators.md`, `rename-operator.md` |
| The merge library is lodash/extend/deep-extend/dset/object-path | `merge-library-minefield.md` |
| Finding where the write can enter — carriers | `carrier-matrix.md`, `injection-points.md`, `api-shapes.md`, `qs-parser.md` |
| Finding which property the sink reads | `gadget-index.md`, `gadget-index-deep.md`, `fallback-grammar.md`, `property-sources.md` |
| EJS/template option gadgets | `ejs-gadgets.md`, `template-gadgets.md` |
| Spawn/env/require/process sinks | `process-gadgets.md`, `nodejs-internals.md`, `pollution-to-rce.md`, `os-environ.md` |
| Authz/role/ownership fallback names | `authz-gadgets.md`, `gadget-index-deep.md` |
| Proving the write — fresh-object/behavior/OOB oracles | `readback-oracles.md`, `status-codes.md`, `detection.md` |
| No direct readback exists | `blind-pollution.md`, `status-codes.md` |
| The write is stored/relayed/delayed | `second-order.md` |
| gRPC/protobuf structured-data carrier | `grpc-attribute.md` |
| Multiple polluted properties in one write | `multi-field-writes.md` |
| JS engine write mechanics (`__proto__` setter vs literal key) | `v8-semantics.md`, `property-sources.md` |
| Per-framework merge/sink defaults | `framework-matrix.md` |
| Deployment/worker/restart blast radius | `environment-matrix.md` |
| When it's NOT this class — the boundary | `the-boundary.md`, `denied-conditions.md` |
| The engagement order end-to-end | `workflow.md`, `field-manual.md`, `attack-trees.md` |
| The probe matrix, payload corpus | `payload-dictionary.md`, `extended-corpus.md` |
| Recording evidence, falsifiers, ledger lines | `evidence-rules.md`, `workflow.md` |
| Diagnosing a failed write | `error-analysis.md`, `common-mistakes.md`, `denied-conditions.md` |
| Mining a white-box handout for the merge+sink | `mining-notes.md`, `whitebox-hunt.md` |
| Real CVEs and chain-card shapes | `real-world-cases.md`, `ctf-shapes.md`, `ctf-walkthroughs.md` |
| The mechanism — what the class actually is | `theory.md` |
| The one-screen version | `cheatsheet.md` |
| Repository tooling | `tooling.md` |

## Loading rule

The `../SKILL.md` file is enough for routine recognition and the first probe.
Open a file here only when the pollution needs a concrete payload shape or a
confirm wording.

Every technique here was distilled from a field note in `../field-notes.md`;
the payloads below are the ones that actually worked on a live target.
