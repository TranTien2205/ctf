# Field notes — OAuth / SSO flow

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

## 2026-09-15 · SSOS · proposed

- source note: `solved/ssos.md`
- chain card: `knowledge/chains/htb-ssos-oauth-registration-race-cookie-swap-json-csrf.json`
- verification: verified_live — flag string read from /submission/:id as the owning author on a fresh instance
- classified as: `web-oauth-sso` (score 3.5, 3 signals matched)
- also matched: `web-auth-session` (3.5), `web-csrf` (3.5), `web-xss` (2.5)
- signals that fired: client_secret, oauth, redirect_uri

**Confirming probe that worked**

> hammer POST /api/register for the fixed bot account with your own password and confirm it returns 200 before the bot reaches its registerUser step

Expected: the registration succeeds and your credentials work at /api/login

Falsifier: the account is already registered with an unknown random password (instance already consumed)

**Traps recorded on this solve**

- the registration race alone is dead: if you pre-register the student but never swap the cookie, the bot authorizes as teacher and the flag is written to an unreadable teacher account
- the CSRF must use enctype=text/plain with the JSON-name trick, not url-encoded form data, because the binder requires a raw JSON body
- the internal nginx port the bot resolves to (1337) differs from the external mapped port; the data URL must target the internal host:port
- redirect_uri validation is strict on hostname; Host header must include the external port for the port check to pass
- the authorize code exchange still requires the client_secret, so you cannot exchange a stolen code yourself; the swap works because the bot does the exchange
- an instance that already ran its startup is consumed: student has a random password and the flag is unreachable

**Blast radius**: a fresh instance is required; an already-running instance is permanently consumed because the flag is submitted once at startup into an account with an unknown random password

- status: proposed
