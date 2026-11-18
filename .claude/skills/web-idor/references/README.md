# IDOR reference map

Open one named file after the two-identity ownership probe. Do not load
the whole directory — pick the row matching what you observed.

## By observed identifier shape

| Observed | Reference |
|---|---|
| Sequential numeric ids | `sequential-enumeration.md` |
| Opaque or time-ordered ids | `uuid-analysis.md` |
| Predictable id construction | `predictable-ids.md` |
| Signed, encoded or encrypted ids | `signed-ids.md` |
| A bounded collection sweep is justified | `enumeration.md` |

## By where the check is missing

| Observed | Reference |
|---|---|
| API object endpoint | `api-idor.md` |
| GraphQL objects/resolvers | `graphql-idor.md` |
| File/download object | `file-idor.md` |
| Collection list/filter endpoints | `collection-filters.md` |
| Function/verb-level authorization | `function-level.md` |
| Mass assignment / owner-field binding | `mass-assignment.md` |
| Second-order (server reads it for you) | `second-order-idor.md` |
| Tenant/org boundary | `multi-tenant.md` |
| Object lifecycle states (draft/deleted/shared) | `lifecycle-idor.md` |
| Association/join/embed leaks | `object-relationships.md` |
| Blind IDOR — no data in the response | `blind-idor.md` |
| Where the app leaks foreign ids | `id-supply.md` |

## By carrier and request shape

| Observed | Reference |
|---|---|
| Where the id can appear (path/query/body/header/WS) | `carriers-deep.md` |
| Parameter locations and naming | `parameter-locations.md` |
| Identifier formats and coercion | `identifier-formats.md` |
| Method/content-type/route/version bypasses | `bypass-shapes.md` |
| Protocol variants (WS, RPC, multipart) | `protocol-variants.md` |

## By stack

| Observed | Reference |
|---|---|
| Rails/Django/Laravel/Express/Spring/Flask/FastAPI/.NET | `framework-notes.md` |
| White-box source hunt | `whitebox-hunt.md` |

## Analysis and workflow

| Need | Reference |
|---|---|
| Ownership models to name the check | `ownership-models.md` |
| First-contact detection | `detection.md` |
| Theory — what IDOR actually is | `theory.md` |
| Where the boundary is drawn | `the-boundary.md` |
| Where proof appears in responses | `verification-surfaces.md` |
| What each denial pattern means | `failed-attempts.md` |
| Error-message analysis | `error-analysis.md` |
| Denied conditions that are not IDOR | `denied-conditions.md` |
| Bounded workflow | `workflow.md` |
| Attack trees | `attack-trees.md` |
| Field manual | `field-manual.md` |
| Cheatsheet | `cheatsheet.md` |
| Payload dictionary | `payload-dictionary.md` |
| Extended payload corpus | `extended-corpus.md` |
| Real-world case patterns | `real-world-cases.md` |
| CTF-specific shapes | `ctf-shapes.md` |
| Worked challenge traces | `ctf-walkthroughs.md` |
| Mining notes — where ids leak | `mining-notes.md` |
| Evidence rules | `evidence-rules.md` |
| Common mistakes | `common-mistakes.md` |
| Tooling | `tooling.md` |

The two-identity probe in `../SKILL.md` remains the proof boundary.
Enumeration material does not turn a guessed identifier or a public
object into IDOR.
