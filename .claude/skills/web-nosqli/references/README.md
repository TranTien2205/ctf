# NoSQL injection reference map

This directory belongs to the canonical `web-nosqli` class. Open one named
reference after the safe object-shaped probe; do not load the whole directory.

## Choose by observed signal

| Signal or task | Open |
|---|---|
| Naming the object-injection | `detection.md` |
| The operator list | `operators.md` |
| The JS predicates | `operators-js.md` |
| Where the object survives | `injection-points.md` |
| The login-bypass | `auth-bypass.md` |
| Char-by-char extraction | `extraction.md` |
| Extraction depth | `extraction-deep.md` |
| The aggregation surface | `aggregation.md` |
| The denied-conditions | `denied-conditions.md` |
| The full workflow | `workflow-deep.md` |
| The field-manual | `field-manual.md` |
| The flag-field walk | `flag-extraction.md` |
| The quick-reference | `cheatsheet.md` |
| The error-reading | `error-analysis.md` |
| The real-world cases | `real-world-cases.md` |
| The source-grep | `whitebox-hunt.md` |
| The sanitize/whitelist evasions | `filter-bypass.md` |
| The MongoDB driver-details | `mongo-specific.md` |
| The write-operators | `update-injection.md` |
| The extended corpus | `extended-corpus.md` |
| The CTF shapes | `ctf-shapes.md` |
| The workflow order | `workflow.md` |
| The evidence bar | `evidence-rules.md` |
| The failure modes | `common-mistakes.md` |
| The theory | `theory.md` |
| The tool wrappers | `tooling.md` |
| The payload corpus | `payload-dictionary.md` |

## Loading rule

The `../SKILL.md` file is enough for routine recognition and the first probe.
Open a file here only when the injection needs a concrete operator or a
confirmation wording.

Every technique here was distilled from a field note in `../field-notes.md`.

The separate `web-sqli` class covers SQL string/query injection. Do not use this
reference to route or confirm SQLi.
