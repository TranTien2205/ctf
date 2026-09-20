# Field notes — Server-side request forgery

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

## 2026-09-07 · Red Island · proposed

- source note: `solved/red-island.md`
- chain card: `knowledge/chains/htb-red-island-ssrf-gopher-redis-lua-rce.json`
- verification: verified_live — flag returned by the helper binary through the Lua channel
- classified as: `web-ssrf` (score 2.5, 2 signals matched)
- also matched: `web-request-smuggling` (2.5), `web-race-condition` (1.5), `web-auth-session` (1.5)
- signals that fired: 127.0.0.1, ssrf

**Confirming probe that worked**

> submit a loopback URL in the fetch field and read the full response body, including error text

Expected: content or an error that proves the server performed the fetch

Falsifier: the field is validated to an allowlist and never reaches a client

**Traps recorded on this solve**

- the gopher payload length prefix must equal the exact byte length of the Lua string
- always read error bodies: this app leaked the fetched file inside a non-200 message

**Blast radius**: eval on the shared Redis instance affects every player's session; prefer read-only Lua first

- status: proposed
