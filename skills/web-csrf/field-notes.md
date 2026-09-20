# Field notes — Cross-site request forgery

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

## 2026-09-20 · TornadoService · proposed

- source note: `solved/tornadoservice.md`
- chain card: `knowledge/chains/htb-tornadoservice-bot-csrf-class-pollution.json`
- verification: verified_live — HTTP 200 from /stats with the forged cookie. Re-verified live 2026-09-20 on a second instance: after the bot ran, the public read endpoint showed exactly one polluted object carrying the text/plain marker {"machine_id": "host-1051", ..., "ignore": "="}, and the forged cookie returned HTTP 200 with the flag in the body.
- classified as: `web-csrf` (score 3.5, 3 signals matched)
- also matched: `web-cors` (4.0), `web-auth-session` (3.5), `web-parser-differential` (3.5)
- signals that fired: bot visits, csrf, text/plain

**Confirming probe that worked**

> fetch a public read endpoint to obtain a valid object id, then confirm the write endpoint answers 403 for a direct request

Expected: 403 that names a local-only restriction, and a readable object id

Falsifier: the write endpoint accepts a direct request, so no bot relay is needed

**Traps recorded on this solve**

- ngrok inserts an interstitial that headless bots cannot pass; a plain SSH reverse tunnel does not
- firing two payload routes at once makes the success unattributable: fire one, wait, then the other
- RESOLVED 2026-09-20: fetch is the wrong primitive. Private Network Access refuses a preflighted subresource request to a loopback address, and from an INSECURE public origin it refuses even a simple GET, because PNA requires a secure context. Confirmed on the real bot (Chrome 127) and on a replica (Chrome 152). Use a form navigation, which is not a subresource and is never subject to PNA.
- Because PNA kills fetch from a plain-http public page, the bot cannot discover the internal port for you. Fire the form blind across a port list and take the object id from the public read endpoint, which lists the same objects.
- Put a dummy key in the text/plain body to absorb the '=' that the encoding inserts. In a setattr merge that key then shows up in the public read endpoint, so a blind cross-origin write becomes verifiable.
- Header spoofing stays falsified: XFF, X-Real-IP, Forwarded, X-Originating-IP, X-Client-IP, True-Client-IP and Host: localhost all still return the 403 when the server runs without xheaders.

**Blast radius**: the pollution changes a global application setting; other players on a shared instance lose their sessions

- status: proposed
