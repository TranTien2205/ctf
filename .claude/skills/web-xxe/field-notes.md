# Field notes — XML external entity

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

## 2026-09-18 · xxe (WAFfles or Ice Cream) · proposed

- source note: `solved/htb-xxe-waffles-simplexml-noent.md`
- chain card: `knowledge/chains/htb-xxe-content-type-branch-simplexml-noent-file-read.json`
- verification: verified_live — the flag was returned inline in the body of POST /api/order, in the same position where the submitted food value is echoed
- classified as: `web-xxe` (score 3.0, 3 signals matched)
- also matched: `file-read-primitives` (3.5), `web-race-condition` (1.5), `web-parser-differential` (1.5)
- signals that fired: application/xml, entity, simplexml_load

**Confirming probe that worked**

> post the same body to the JSON endpoint with an XML content type and an XML document that declares an internal entity in the echoed field

Expected: the response echoes the entity's value rather than the entity reference, proving substitution is on

Falsifier: the endpoint rejects the content type, or the entity reference comes back literally or empty

**Traps recorded on this solve**

- the challenge theme named a filter and made a WAF-bypass chain the top local match, but there was no filter at all and the plainest payload worked; probe the plain payload before the encoded one
- reading PHP source with the plain file scheme breaks the XML parse because the source contains angle brackets, so a base64 stream filter is required and its absence looks like an unreadable file
- the visible HTML form was not the request path; only the front-end JavaScript named the real endpoint and content type

**Blast radius**: read-only. The request is an ordinary order submission and creates no persistent object here. Read files only inside the challenge container, and never point an external entity at a host outside the supplied scope.

- status: proposed
