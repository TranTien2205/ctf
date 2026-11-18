# NoSQL injection reference map

This directory belongs to the canonical `web-nosqli` class. Open one named
reference after the safe object-shaped probe; do not load the whole directory.

## Choose by observed signal

| Signal or task | Open |
|---|---|
| Naming the object-injection | `detection.md` |
| The operator list | `operators.md` |
| `$ne`/`$eq` depth | `operator-ne-deep.md` |
| `$regex` depth | `operator-regex-deep.md` |
| `$where` JS depth | `operator-where-deep.md` |
| The JS predicates | `operators-js.md` |
| The `$expr`/`$function`/`$accumulator` | `operators-aggregation.md` |
| Where the object survives | `injection-points.md` |
| The `qs` grammar | `carrier-qs-deep.md` |
| The JSON body | `carrier-json-deep.md` |
| The header/cookie carriers | `carrier-header-deep.md` |
| The login-bypass | `auth-bypass.md` |
| The auth-bypass corpus | `payload-auth.md` |
| Char-by-char extraction | `extraction.md` |
| Extraction depth | `extraction-deep.md` |
| The blind-walk steps | `blind-extraction-walkthrough.md` |
| The blind corpus | `payload-blind.md` |
| The extraction loops | `extraction-automation.md` |
| The flag-field walk | `flag-extraction.md` |
| The aggregation surface | `aggregation.md` |
| Aggregation depth | `aggregation-deep.md` |
| The sanitize/whitelist evasions | `filter-bypass.md` |
| Filter evasion depth | `filter-evasion-deep.md` |
| The MongoDB driver-details | `mongo-specific.md` |
| The mongoose internals | `mongoose-internals.md` |
| The mongo internals | `mongodb-internals.md` |
| The write-operators | `update-injection.md` |
| The extended corpus | `extended-corpus.md` |
| The CTF shapes | `ctf-shapes.md` |
| The walkthroughs | `ctf-walkthroughs.md` |
| The second-order shapes | `second-order-nosqli.md` |
| The workflow order | `workflow.md` |
| The full workflow | `workflow-deep.md` |
| The field-manual | `field-manual.md` |
| The evidence bar | `evidence-rules.md` |
| The error-reading | `error-analysis.md` |
| The failure modes | `common-mistakes.md` |
| The denied-conditions | `denied-conditions.md` |
| The theory | `theory.md` |
| The tool wrappers | `tooling.md` |
| The real-world cases | `real-world-cases.md` |
| The source-grep | `whitebox-hunt.md` |
| The Node/Express shapes | `node-express-shapes.md` |
| The Python carriers | `python-nosql.md` |
| The PHP carriers | `php-nosql.md` |
| The Java carriers | `java-nosql.md` |
| The other-NoSQL DBs | `other-nosql.md` |
| The GraphQL args | `graphql-nosql.md` |
| The REST-API args | `api-nosql.md` |
| The WAF evasions | `waf-bypass-nosql.md` |
| The per-carrier corpus | `payload-injection-points.md` |
| The payload corpus | `payload-dictionary.md` |
| The exotic payloads | `payload-dictionary-2.md` |
| The `$$`/`$literal` corpus | `payload-dictionary-3.md` |
| The corner-cases | `mining-notes.md` |

## Loading rule

The `../SKILL.md` file is enough for routine recognition and the first probe.
Open a file here only when the injection needs a concrete operator or a
confirmation wording.

Every technique here was distilled from a field note in `../field-notes.md`.

The separate `skills/web-sqli/` class covers SQL string/query injection. Do not
use this reference to route or confirm SQLi.
