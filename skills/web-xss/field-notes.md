# Field notes — Cross-site scripting

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

## 2026-09-18 · xss (Full Stack Conf) · proposed

- source note: `solved/htb-fullstackconf-stored-xss-innerhtml-socketio-flag.md`
- chain card: `knowledge/chains/htb-fullstackconf-blind-stored-xss-socketio-oracle.json`
- verification: verified_live — the flag arrived inside an event frame pushed by the live target on its own push channel, in response to a stored payload executing in the renderer
- classified as: `web-xss` (score 2.5, 2 signals matched)
- also matched: `web-race-condition` (1.5), `web-ssrf` (1.5), `web-sqli` (1.5)
- signals that fired: innerHTML, xss

**Confirming probe that worked**

> open the push channel, leave it idle briefly to confirm it stays silent, then submit an image element with an error handler as the stored value and keep the channel open for about two minutes

Expected: a frame arrives on the channel carrying the reward payload

Falsifier: the channel delivers unrelated traffic while idle, so silence proves nothing, or repeated submissions across contexts produce no frame at all

**Traps recorded on this solve**

- an element whose handler fires while a plain script element does not is the signature of insertion through an HTML property rather than a parser, so carry the handler-based payload first and do not read a failing script element as the value being escaped
- one silent run is not a negative on a bot-driven target: the first attempt with a payload that was later proven to work saw nothing for ninety seconds, and the difference was never explained, so re-run before discarding a payload
- confirm the channel is one that stays open until the server has data before treating its silence as a result
- a comment declaring the push channel is not part of the challenge is misleading; it is not part of the bug but it is the entire exfiltration path

**Blast radius**: the submission is an ordinary newsletter registration and each payload stores one row that a shared renderer will execute. Keep the payload to a harmless dialog, never a redirect, a request to an outside host, or anything that changes state, because other players' sessions are rendered by the same component. Do not repeat the batch once it has fired.

- status: proposed
