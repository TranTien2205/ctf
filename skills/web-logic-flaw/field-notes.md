# Field notes — Business logic / mass assignment

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

## 2026-09-23 · NAND circuit checker on a custom CPU (Pachinko / Pachinko Revisited) · proposed

- source note: `solved/pachinko-revisited.md`
- chain card: `knowledge/chains/pico-pachinko-revisited-node-offset-scale-wrap-instruction-overwrite.json`
- verification: verified_live — both flags were returned in the flag field of the live POST /check JSON response
- classified as: `web-logic-flaw` (score 1.0, 1 signals matched)
- also matched: `web-sqli` (1.5)
- signals that fired: privilege

**Confirming probe that worked**

> submit the minimal correct circuit, then the same circuit with one node id just past the checker's documented limit, and compare the two responses

Expected: the correct circuit returns the success output while the out-of-range id is rejected by a different layer, proving two validators with different limits

Falsifier: both are rejected identically, meaning a single validator governs the id and no scaling gap exists

**Traps recorded on this solve**

- the client references a goal that does not exist; read which one the server actually checks
- the checker evaluates ONE random input vector per request, so a circuit that is only sometimes correct passes intermittently -- always repeat a trial before believing it
- an oracle with a 50% pass rate manufactures false positives in proportion to how many ids you scan; six confirmation trials still leaves ~1 false positive per 64 candidates

**Blast radius**: read-only against a per-user instance; the checker is invoked per request and a few hundred gates is enough, so there is no need to send large circuits.

- status: proposed
