# Field notes — Race condition / TOCTOU

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

## 2026-09-07 · ApexSurvive · proposed

- source note: `solved/apexsurvive.md`
- chain card: `knowledge/chains/htb-apexsurvive-profile-race-template-literal-xss-template-overwrite-rce.json`
- verification: verified_live — flag rendered in the page by the overwritten template
- classified as: `web-race-condition` (score 2.5, 2 signals matched)
- also matched: `web-xss` (4.5), `web-ssti` (3.5), `web-file-upload` (2.5)
- signals that fired: race condition, verification token

**Confirming probe that worked**

> send two interleaved profile updates and observe which address receives which token

Expected: a token belonging to one address arrives at the other

Falsifier: the token is read inside the same transaction as the update

**Traps recorded on this solve**

- a partial configuration overwrite loses the socket and bricks the instance permanently
- a trigger file that gets imported on reload must be valid code; a PDF placed there bricks the worker
- the HTML sanitiser escapes ampersands in stored text, so query strings must be built at runtime
- base64url decoding in the browser fails without manual padding
- the bot re-logs in per visit, so stolen cookies expire quickly; verify immediately

**Blast radius**: overwriting server configuration or an imported module can permanently break the instance

- status: proposed
