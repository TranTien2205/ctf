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

## 2026-09-19 · Dusty Alleys · proposed

- source note: `solved/htb-dusty-alleys-default-vhost-leak-ssrf-key-header.md`
- chain card: `knowledge/chains/htb-dusty-alleys-http10-host-vhost-leak-ssrf-to-header-mirror.json`
- verification: verified_live — the flag was returned inline by the live target as the value of the key field in the JSON the mirroring endpoint produced for the server-side fetch
- classified as: `web-parser-differential` (score 2.5, 2 signals matched)
- also matched: `web-ssrf` (4.5), `web-request-smuggling` (2.5), `web-sqli` (1.5)
- signals that fired: nginx, x-forwarded-for

**Confirming probe that worked**

> request the reflecting endpoint using the older protocol version with an empty host header, and compare the reflected host with the one returned by an ordinary request

Expected: the reflected host is an internal domain name rather than the address that was dialled

Falsifier: the reflected host is unchanged, or the proxy rejects the request outright

**Traps recorded on this solve**

- the loopback target must be addressed by the name the application expects: an address literal made the fetcher fail with an invalid status code error, while the name on the same port succeeded
- the proxy normalises dot-dot segments before choosing a location, so traversal from the proxied prefix falls back to the static root instead of reaching another backend path
- combining a content length with a chunked encoding is rejected by the proxy, so smuggling is not the way into the unproxied backend routes
- the reflecting endpoint looks like a harmless debug route; its real value is that it prints credentials attached by a server-side fetcher

**Blast radius**: read-only. Every step is a GET, and the server-side fetch should be pointed only at the challenge's own loopback services. Do not aim the url parameter at anything outside the supplied instance, and do not use it as a general relay.

- status: proposed
