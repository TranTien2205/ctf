# Field notes — Parser differential / proxy trust

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

## 2026-09-07 · NovaCore · proposed

- source note: `solved/novacore.md`
- chain card: `knowledge/chains/htb-novacore-hopbyhop-cache-overflow-domclobber-polyglot-rce.json`
- verification: verified_live — flag file read by the executed plugin
- classified as: `web-parser-differential` (score 3.5, 3 signals matched)
- also matched: `web-file-upload` (3.5), `web-prototype-pollution` (3.5), `web-xss` (3.5)
- signals that fired: hop-by-hop, traefik, x-real-ip

**Confirming probe that worked**

> send the same authenticated-only request twice, once normally and once with the proxy header named in the Connection header

Expected: the second request is accepted without a token

Falsifier: both requests are rejected, so the trust check does not depend on that header

**Traps recorded on this solve**

- the bot runs on a fixed schedule; place the poisoned state first, then poll
- the polyglot only works when the archive bytes are overlaid at the offset the scanner reads

**Blast radius**: overwriting a neighbouring cache entry corrupts another user's record; plugin execution runs code on the instance

- status: proposed
