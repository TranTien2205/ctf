# Field notes — SQL injection

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

## 2026-09-07 · red-island-2 · proposed

- source note: `solved/red-island-2.md`
- chain card: `knowledge/chains/htb-red-island-2-json-unicode-waf-bypass-time-blind-sqli.json`
- verification: verified_live — extracted value confirmed by a HEX equality probe
- classified as: `web-sqli` (score 5.5, 5 signals matched)
- also matched: `web-race-condition` (1.5), `web-cache-poisoning` (1.0)
- signals that fired: ORDER BY, SELECT note FROM notes WHERE assignee = '%s'`.
2. WAF (on RA, SQL, mysql, time-based

**Confirming probe that worked**

> send one blocked keyword as unicode escapes and compare the response with the same keyword sent literally

Expected: the escaped form is accepted while the literal form is rejected

Falsifier: both forms are rejected, so the filter runs after decoding

**Traps recorded on this solve**

- grouped concatenation needs an explicit ordering or rows arrive in a different order each query
- parallel timing probes contend on the worker pool and corrupt the oracle; extract sequentially
- measure the baseline before choosing a threshold; jitter can cross a threshold set too close
- end of string reads as a space in a numeric binary search; test for a non-zero character code before appending
- compare hex strings as strings, not as a numeric literal, or the comparison silently fails

**Blast radius**: conditional sleeps hold a worker per matching row; keep the row count and the sleep short on a shared instance

- status: proposed
