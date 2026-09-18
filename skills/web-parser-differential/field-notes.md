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

## 2026-09-17 · Phonebook · proposed

- source note: `solved/phonebook.md`
- chain card: `knowledge/chains/htb-phonebook-ldap-prefix-oracle.json`
- verification: verified_live — 302 / + Set-Cookie mysession after POST /login with the reconstructed password HTB{d1rectory_h4xx0r_is_k00l}
- classified as: `web-parser-differential` (score 2.5, 2 signals matched)
- also matched: `web-race-condition` (1.5), `web-auth-session` (1.5), `web-nosqli` (1.5)
- signals that fired: X-Forwarded-For, nginx

**Confirming probe that worked**

> POST /login user=* pass=* and read the Location header

Expected: a redirect that is not /login?message=Authentication failed, plus a session cookie

Falsifier: every login attempt lands on the same ?message=Authentication failed URL

**Traps recorded on this solve**

- the (!(&(1=0)(userPassword=...)) shape is a blanket bypass, not a character oracle
- the prefix oracle needs username=admin with password=prefix+char+* — the response Location is one bit
- do not forget the {} chars in the flag charset or you stop one character early
- the search page lives under a hashed asset dir that is otherwise unrelated to auth

**Blast radius**: full directory enumeration and account takeover for any uid managed by the same database

- status: proposed
