# Field notes — Arbitrary file read / source disclosure

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

## 2026-09-06 · nginxatsu · proposed

- source note: `solved/nginxatsu.md`
- chain card: `knowledge/chains/htb-nginxatsu-alias-traversal-appkey-session-forge-blind-sqli.json`
- verification: verified_live — extracted value confirmed by a HEX equality probe against the database row
- classified as: `file-read-primitives` (score 2.5, 2 signals matched)
- also matched: `web-auth-session` (3.5), `web-sqli` (3.5), `web-parser-differential` (1.5)
- signals that fired: alias, traversal

**Confirming probe that worked**

> request the static prefix with a single trailing dot-dot segment and compare the response with the normal static path

Expected: a file outside the static root is returned

Falsifier: the traversal path 404s or is normalised away

**Traps recorded on this solve**

- MySQL case-insensitive collations make 't' equal 'T'; case-exact extraction needs a binary comparison
- a linear charset scan is far too slow; binary search costs about seven probes per character
- a string replace applied after formatting cannot match the placeholder it was meant to replace

**Blast radius**: read-only extraction; the forged session affects only the attacker's own requests

- status: proposed
