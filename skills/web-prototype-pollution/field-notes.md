# Field notes — Prototype / class pollution

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

## 2026-09-10 · Secure Notes · proposed

- source note: `solved/secnotes.md`
- chain card: `knowledge/chains/htb-secnotes-mongoose-rename-prototype-pollution-local-gate.json`
- verification: verified_live — HTTP 200 from the gated flag endpoint
- classified as: `web-prototype-pollution` (score 3.5, 3 signals matched)
- also matched: `web-nosqli` (2.5), `web-race-condition` (1.5), `web-ssrf` (1.5)
- signals that fired: $rename, __proto__, prototype pollution

**Confirming probe that worked**

> send an update containing only your own note's filter and no content fields, and read the response

Expected: the matched documents are returned unchanged, proving the filter is attacker-shaped and the call is read-safe

Falsifier: the filter is coerced to a string, so no object reaches the query

**Traps recorded on this solve**

- a broad filter fired before the update semantics are understood mass-updates the collection and can cost the instance
- test update semantics on your own object with the content fields omitted first

**Blast radius**: a broad filter with content fields overwrites every document in the collection and destroys other players' data; always pin the filter to your own object id

- status: proposed

## 2026-09-06 · TornadoService · proposed

- source note: `solved/tornadoservice.md`
- chain card: `knowledge/chains/htb-tornadoservice-bot-csrf-class-pollution.json`
- verification: verified_live — HTTP 200 from /stats with the forged cookie
- classified as: `web-prototype-pollution` (score 3.5, 3 signals matched)
- also matched: `web-auth-session` (3.5), `web-csrf` (3.5), `web-parser-differential` (3.5)
- signals that fired: __class__, class pollution, merge

**Confirming probe that worked**

> fetch a public read endpoint to obtain a valid object id, then confirm the write endpoint answers 403 for a direct request

Expected: 403 that names a local-only restriction, and a readable object id

Falsifier: the write endpoint accepts a direct request, so no bot relay is needed

**Traps recorded on this solve**

- ngrok inserts an interstitial that headless bots cannot pass; a plain SSH reverse tunnel does not
- firing two payload routes at once makes the success unattributable: fire one, wait, then the other

**Blast radius**: the pollution changes a global application setting; other players on a shared instance lose their sessions

- status: proposed
