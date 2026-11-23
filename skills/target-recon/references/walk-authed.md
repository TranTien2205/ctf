# Worked example: authed

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Walked: supplied http://<target>/ + creds user:pass.

1. au-loginflow: POST /login json {user,pass} -> 200 sets
   session cookie shape s%3A<val>.<sig> = express-signed.
2. session_dissect <cookie> -> express-signed structure,
   weakness = secret strength offline.
3. au-surfacemap: /admin answers 403 (exists-gated),
   /api/users/<n> int ids sequential (idshape -> idor prior).
4. au-multiaccount not possible (one cred set) -> note.
5. Observations: session=express-signed, /admin gated,
   sequential ids, export endpoint.
6. classify -> idor+session candidates; cls-idor names what
   the skill still needs.
## Pivot

Signal harvested -> out-*; route named -> that skill.
