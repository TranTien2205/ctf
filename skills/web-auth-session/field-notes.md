# Field notes — Authentication and session

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

## 2026-09-18 · broken authentication · proposed

- source note: `solved/broken-authentication.md`
- chain card: `knowledge/chains/htb-broken-authentication-unsigned-base64-json-cookie-forge.json`
- verification: verified_live — the flag was read from the body of GET / on the live target, inside an <h1> element, with the forged cookie attached
- classified as: `web-auth-session` (score 2.5, 2 signals matched)
- also matched: `web-race-condition` (1.5), `web-ssti` (1.5), `web-parser-differential` (1.5)
- signals that fired: eyJ1c2VybmFtZSI6ImN0ZnByb2JlX2ExIn0, phpsessid

**Confirming probe that worked**

> register your own account, log in, then URL-decode and base64-decode the session cookie returned by Set-Cookie

Expected: the decoded bytes are readable structured data containing the username you just chose

Falsifier: the value is opaque, or a signature or MAC segment travels with it and the server rejects an edited value

**Traps recorded on this solve**

- the cookie name lies: PHPSESSID here carried base64 JSON, not a PHP session id, so do not skip decoding because the name looks standard
- curl writes the cookie URL-encoded; %3D must be decoded to = before base64 decoding or the decode looks like it failed
- re-encode with base64 -w0, since a wrapped line breaks the header

**Blast radius**: one self-registered user row on a shared challenge database. The forge itself is a read with a chosen cookie and mutates nothing. Do not spray usernames; register once and reuse that account.

- status: proposed

## 2026-09-18 · broken authentication control (TODO OR NOT TODO) · proposed

- source note: `solved/htb-todo-or-not-todo-list-all-access-control.md`
- chain card: `knowledge/chains/htb-todo-magic-list-all-segment-access-control-bypass.json`
- verification: verified_live — the flag was returned as the name field of one object in the JSON array from the listing endpoint on the live target
- classified as: `web-auth-session` (score 1.5, 1 signals matched)
- also matched: `web-cache-poisoning` (1.0), `web-logic-flaw` (1.0), `web-xxe` (1.0)
- signals that fired: session

**Confirming probe that worked**

> issue the listing request twice with one cookie and one secret, once for your own identity and once with the identity segment replaced by the collective value

Expected: your own listing is empty or short while the collective value returns rows owned by another account

Falsifier: the collective value returns the same rows as your own identity, or is rejected with the same error as an unrelated identity

**Traps recorded on this solve**

- the session cookie, the identity and the per-session secret are issued together on each visit; pairing a stale identity with a fresh cookie returns an authorisation error that looks exactly like the control working, which is a false negative that can kill a correct hypothesis
- capture the cookie, the identity and the secret from one single response before probing
- the session cookie is signed and does not need to be forged; the bug is entirely in the path segment

**Blast radius**: read-only. Use the listing route only; the same API exposes completion and deletion routes that take an id and would mutate another account's objects, so never point those at an id that is not yours.

- status: proposed
