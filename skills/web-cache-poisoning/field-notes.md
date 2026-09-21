# Field notes — Cache poisoning / deception

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

## 2026-09-21 · EncoDecept · confirmed

- source note: `solved/encodecept.md`
- chain card: `knowledge/chains/htb-encodecept-charset-xss-cache-deception-orm-oracle-marshal-rce.json`
- verification: verified_live — the flag was written to the Rails public directory by the Marshal RCE and read back over HTTP 200 on the live target
- classified as: `web-cache-poisoning` (score 2.0, 2 signals matched)
- also matched: `web-race-condition` (2.5), `web-prototype-pollution` (2.5), `web-ssrf` (2.5)
- signals that fired: cache, x-cache

**Confirming probe that worked**

> authenticated GET /settings.html?cb=1 twice, then anonymous GET /settings.html?cb=1

Expected: the anonymous request returns 200 with X-Cache-Status HIT and the body of the authenticated page

Falsifier: the anonymous request is a 302 to /login, so the proxy does not serve an authenticated page anonymously

**Traps recorded on this solve**

- report the internal 127.0.0.1 URL to the bot, not the public address, or the bot session is not used
- .ico is rendered as an image by Chrome, so the cached HTML never executes; use .html
- the Marshal gadget needs the detection step first or it raises Errno::ENOENT on the git cache directory
- the gadget is tied to the exact Ruby and gem build and can fail on a patched image
- the flag file written into the web root may not be removable afterwards; reset the instance

**Blast radius**: cache poisoning affects every player who requests the cached URL until it expires; the XSS and RCE act as the privileged bot and can write files inside the container, so use a disposable cachebuster and remove created templates

- status: confirmed
