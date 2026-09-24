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

## 2026-09-23 · SOS or SSO · proposed

- source note: `solved/htb-sos-or-sso-vue-vbind-onerror-xss-support-bot-oidc-repoint-role-claim.md`
- chain card: `knowledge/chains/htb-sos-or-sso-vue-vbind-onerror-xss-support-bot-oidc-repoint-role-claim.json`
- verification: verified_live — The login endpoint for faction 1 first returned a bare endpoint string; after the reported note's handler ran, it returned a full authorization URL naming our provider. The first login produced an admin-level session whose user listing disclosed the seeded admin address, a second login as that address produced a session for that account, and GET /api/note/1 decoded to the flag. After cleanup the forged account is gone and the login endpoint returns a bare endpoint again.
- classified as: `web-oauth-sso` (score 2.5, 2 signals matched)
- also matched: `web-ssrf` (2.5), `web-idor` (2.0), `web-race-condition` (1.5)
- signals that fired: /token, oidc

**Confirming probe that worked**

> Call the login-initiation endpoint for a built-in tenant and read the URL it returns.

Expected: A bare endpoint string with no state or client_id, showing the configured provider is unreachable and that the flow only works once the endpoint is repointed.

Falsifier: A full authorization URL with a state parameter, meaning the provider resolves and the configuration does not have to be replaced.

**Traps recorded on this solve**

- Reaching the privileged level is not the same as reaching the privileged identity; a check comparing the owner's id forces a second login as that exact account.
- The library refuses the discovery document unless its issuer string matches the registered endpoint exactly, and refuses the id_token unless aud equals the stored client id.
- A static file host cannot serve the identity provider because the code exchange is a POST.
- The reviewer bot clicks a fixed element when the content contains certain words, which on this target was the delete button, so the payload removes its own note.
- Endpoint validation on write makes the original provider value unrestorable once it no longer resolves; do not claim the configuration was reverted.
- A tunnel service's browser interstitial does not apply here because every consumer of the provider is a server-side HTTP client, so the usual warning against it does not hold.
- CSRF enforced as a fixed header value stops nothing scripted; it only blocks form posts and simple cross-origin requests.

**Blast radius**: Repointing a tenant's identity provider is a standing authentication bypass for every user of that tenant while the attacker's provider is reachable, and a role claim from it can mint accounts at any level the role table defines. An endpoint that is validated before it is stored cannot be set back to an unreachable original, so the change is not fully reversible through the API. The reviewer bot deletes content containing certain words, so a payload carrying them destroys its own note after running.

- status: proposed
