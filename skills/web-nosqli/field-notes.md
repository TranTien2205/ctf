# Field notes — NoSQL / operator injection

Written by `tools/classify_solve.py` after a flag is verified, then reviewed by a
human. Nothing here is generated from guesswork: every entry cites the solved note
and the chain card it came from.

| Status | Meaning |
|---|---|
| `proposed` | written automatically after a solve; not yet reviewed |
| `confirmed` | a human checked it against the evidence and kept it |

Promote an entry by changing its status line to `confirmed`. Delete an entry that
did not hold up, and say why in the commit message. `test/regression.py` fails if
an entry has any other status.

---

## 2026-09-23 · UnEarthly Shop · proposed

- source note: `solved/unearthly_shop.md`
- chain card: `knowledge/chains/htb-unearthly-shop-aggregation-pipeline-injection-autoload-primer-monolog-rce.json`
- verification: verified_live — GET /admin/ returned the flag appended to the login page body by the gadget's system() call on the live target
- classified as: `web-nosqli` (score 1.5, 1 signals matched)
- also matched: `web-deserialization` (3.5), `web-parser-differential` (2.5), `web-prototype-pollution` (2.5)
- signals that fired: mongo

**Confirming probe that worked**

> POST the product listing endpoint with [{"$limit":1},{"$unionWith":"users"},{"$match":{"username":{"$exists":true}}}]

Expected: documents from the other collection come back, proving the pipeline rather than a filter is controlled

Falsifier: the body is used as a match document only, so an aggregation stage name is treated as a field and nothing extra is returned

**Traps recorded on this solve**

- prepending anything to a generated gadget invalidates its reference indices and the payload then fails with no error
- protected property names contain NUL bytes, which survive JSON and BSON but are lost when a payload is pasted through a terminal
- overwriting the permission field locks the route that writes it, so plan the restore before the write
- the gadget runs from a destructor, so pick a route that is not permission-checked or the redirect will hide the output
- the primer class stays undefined and becomes an incomplete class, which is expected and not an error

**Blast radius**: step 7 writes to the user document that the permission check itself reads, and a payload that replaces the permission map locks the writing route behind its own access check. Carry the original permission keys inside the payload so the panel keeps working and the write stays reversible; otherwise the only way back is a write stage on the pipeline injection. Restore before anything else, because the instance can disappear first.

- status: proposed
