# Field notes — Arbitrary file read / source disclosure

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

## 2026-09-06 · nginxatsu · proposed

- source note: `solved/nginxatsu.md`
- chain card: `knowledge/chains/htb-nginxatsu-alias-traversal-appkey-session-forge-blind-sqli.json`
- verification: verified_live — extracted value confirmed by a HEX equality probe against the database row
- classified as: `file-read-primitives` (score 2.5, 2 signals matched)
- also matched: `web-auth-session` (3.5), `web-sqli` (3.5), `web-parser-differential` (1.5)
- signals that fired: alias, traversal

**Confirming probe that worked**

> request the static prefix with a single trailing dot-dot segment and compare the response with the normal static path

Expected: a file outside the static root is returned

Falsifier: the traversal path 404s or is normalised away

**Traps recorded on this solve**

- MySQL case-insensitive collations make 't' equal 'T'; case-exact extraction needs a binary comparison
- a linear charset scan is far too slow; binary search costs about seven probes per character
- a string replace applied after formatting cannot match the placeholder it was meant to replace

**Blast radius**: read-only extraction; the forged session affects only the attacker's own requests

- status: proposed

## 2026-09-18 · nginxatsu (rescue-mission variant) · proposed

- source note: `solved/nginxatsu-v2-storage-autoindex-db-backup.md`
- chain card: `knowledge/chains/htb-nginxatsu-storage-autoindex-db-backup-md5-admin.json`
- verification: verified_live — the flag was read from the body of GET / on the live target, inside a <p> element in the page header, while authenticated as the cracked privileged account
- classified as: `file-read-primitives` (score 4.5, 4 signals matched)
- also matched: `web-auth-session` (3.5), `web-ssrf` (2.5), `web-sqli` (2.5)
- signals that fired: ../../, .env, alias, traversal

**Confirming probe that worked**

> generate one artifact with the default values, follow the link to its raw file, then request that file's parent directory with a trailing slash

Expected: an index listing of the directory, containing at least one file that no user generated

Falsifier: the directory returns 403 or 404, or the listing contains only files matching the generated naming pattern

**Traps recorded on this solve**

- this target shares its fingerprint with the 2021 alias-traversal chain and matches it at full signal coverage, yet the traversal probe falsifies: the location uses root, not alias, so nothing traverses
- an nginx-branded 404 means the location matched and the file is absent; a framework-branded 404 means the prefix is not served by nginx at all, which is what decides the traversal question in one request
- nginx normalises dot-dot segments before matching a location, so a multi-level traversal collapses and reaches the application instead of the static prefix
- the archive was a plain tar with a .tar.gz name; identify it with file before trying to decompress it
- sorting parameters supplied in the query string did not reach the query here, so the boolean oracle from the older chain does not exist on this variant

**Blast radius**: read-only apart from one self-registered account and one generated artifact, both of which are ordinary use of the feature. Do not delete files found in the listing; other players read the same directory. Crack hashes offline, never against the live login form.

- status: proposed

## 2026-09-18 · BonechewerCon · proposed

- source note: `solved/htb-bonechewercon-whoops-env-appkey-disclosure.md`
- chain card: `knowledge/chains/htb-bonechewercon-method-not-allowed-whoops-env-disclosure.json`
- verification: verified_live — the flag was read from the body of the error page returned by the live target, inside the environment variables table as the value of the application key
- classified as: `file-read-primitives` (score 1.5, 1 signals matched)
- also matched: `web-auth-session` (3.5), `web-ssrf` (2.5), `web-parser-differential` (1.5)
- signals that fired: .env

**Confirming probe that worked**

> submit the entry form using the method it declares and compare the response size with the normal page

Expected: a response an order of magnitude larger than the normal page, containing a framework exception name and labelled diagnostic sections

Falsifier: the request is handled normally, or the error page is the framework's generic production page with no detail sections

**Traps recorded on this solve**

- the page's maintenance notice and the maintenance middleware in the stack trace both suggest a maintenance-mode bypass, but the application is not in maintenance mode and returns 200; that is flavour text, not the bug
- the same parameter sent on the supported method is not reflected at all and the response is byte-for-byte identical to the plain page, so there is no injection surface to chase
- a plain fixed-length session id means a server-side session driver, so a leaked application key does not enable a session forge on this target

**Blast radius**: read-only. The request raises an exception and reaches no application logic, so nothing is created or modified. Treat every credential in the disclosed configuration as live and do not connect to the services it names; they are usually bound to the container's own loopback and are out of scope.

- status: proposed
