# Field notes — Unsafe deserialization

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

## 2026-09-18 · insecure deserialization (anti_pickle_serum) · proposed

- source note: `solved/htb-anti-pickle-serum-py2-cookie-unpickle-rce.md`
- chain card: `knowledge/chains/htb-py2-pickle-cookie-reduce-rce-rendered-output.json`
- verification: verified_live — the flag was rendered inline in the page returned by the live target, in the same element that previously printed the deserialized object
- classified as: `web-deserialization` (score 2.0, 2 signals matched)
- also matched: `web-open-redirect` (3.0), `web-ssti` (2.5), `web-race-condition` (1.5)
- signals that fired: pickle, pickle.loads

**Confirming probe that worked**

> replace the deserialized value with a call that returns the output of a harmless marker command, and request the page that renders it

Expected: the marker's exact output appears in the position where the object was previously printed

Falsifier: the response is unchanged, an error page is returned, or the value is rejected because it carries no valid signature

**Traps recorded on this solve**

- generating the payload with a newer interpreter than the target emits string opcodes and module paths the target cannot resolve; write the opcodes by hand in the lowest protocol instead
- the class named in the default cookie is usually decorative and carries no behaviour, so time spent reconstructing it is wasted; the value simply has to be replaced
- the deserialization happens before any route logic when it is wired into a pre-request handler, so every path on the site carries the primitive, not only the one that renders it

**Blast radius**: this is command execution on the challenge container, and here that container runs as root. Keep every command read-only, such as listing a directory or printing a file. Never write, delete or restart anything: a single careless command can brick the instance for every player. Confirm with a marker that only prints, and read the objective with one further command.

- status: proposed

## 2026-09-21 · DLLAMA · confirmed

- source note: `solved/dllama.md`
- chain card: `knowledge/chains/htb-dllama-pickle-cookie-auth-bypass-latex-verbatiminput.json`
- verification: verified_live — the flag was extracted from the text layer of /static/input.pdf on the live target after the ^^xx LaTeX payload read flag.txt
- classified as: `web-deserialization` (score 1.0, 1 signals matched)
- also matched: `web-auth-session` (1.5), `web-ssrf` (1.5), `web-open-redirect` (1.0)
- signals that fired: pickle

**Confirming probe that worked**

> log in with any username and base64-decode the resulting user cookie

Expected: the decoded bytes start with a pickle protocol header and reference an application class with an authentication attribute

Falsifier: the cookie is opaque or signed, so no object attributes are attacker-controlled

**Traps recorded on this solve**

- the __reduce__ pickle RCE may be blocked by an object type check; attribute forgery is the working route
- the naive \input{|cmd} payload is blocked by a literal blacklist; use ^^xx escapes
- the generated PDF persists at a fixed path; overwrite it after reading the flag
- the flag file is relative to the application directory (flag.txt)

**Blast radius**: forging the cookie only changes your own session; the generated PDF is written to a fixed static path and must be overwritten with a benign document afterwards so the flag is not left on the shared instance

- status: confirmed

## 2026-09-24 · Spell Orsterra · proposed

- source note: `solved/spell-orsterra.md`
- chain card: `knowledge/chains/htb-spell-orsterra-nginx-unixsocket-redis-messenger-pop-plte-rce.json`
- verification: verified_live — flag returned by /readflag through the PLTE webshell, printed immediately after the literal PLTE bytes in the response
- classified as: `web-deserialization` (score 2.5, 2 signals matched)
- also matched: `web-ssrf` (2.5), `web-open-redirect` (2.0), `web-ssti` (1.5)
- signals that fired: unserial, unserialize

**Confirming probe that worked**

> inject the POP chain with map/stamp set to the target's OWN static PNG and export_file set to a unique probe name, then GET /static/exports/<probe>.png

Expected: HTTP 200 with PNG magic, which proves SSRF + redis write + unserialize + __destruct + arbitrary-path write in one shot without hosting anything

Falsifier: 404 after two worker cycles (~2 min): either the stream name/serializer shape is wrong or the XADD never landed

**Traps recorded on this solve**

- writeup-assisted, but two published details are stale: writeup_search named the technique; the chain was re-derived from source and improved twice: the external redirect server is unnecessary (nginx percent-decodes the unix: uri), and the published IDAT pixel array no longer survives GD/zlib so the payload moved to the PLTE chunk
- the published writeup wraps the stream field as s:1053:"{...}"; that is wrong - the field is plain json_encode(['body'=>..,'headers'=>..]) and a wrapper makes json_decode fail
- PhpSerializer::encode applies addslashes(), and decode() applies stripslashes(), so the body MUST be pre-slashed; addslashes also removes the raw NULs of private-property mangling, which keeps the body valid UTF-8 and avoids the base64 branch (taken only when the body does not end with '}')
- a trailing slash on the /assets/ URL lands on the numkeys argument (0/) and Redis rejects the EVAL; the location regex ~ /assets/(.+)/ is unanchored and the '/' inside unix:/run/... already satisfies it, so omit it
- the write is blind: Redis kills the connection on the 'Host:' line via freeClientAsync, discarding the already-queued reply, so nginx always answers 502 - judge success only by an out-of-band observable
- the Synacktiv IDAT pixel array from the writeup produces no payload on current GD/zlib; verify any image payload by replaying the target's exact transform chain before trusting it
- getExportedMap()'s base64 read is a dead end: the result goes into a local variable and mail() is handed the undefined $this->body, so it exfiltrates nothing
- keep the map small and the handler coordinates off-canvas: imagecopymerge with a negative dst_x still clips and rewrites columns from dst_y down, which perturbs the palette

**Blast radius**: shared instance: the EVAL adds one entry to the 'messages' stream (worker.sh DELs that key every cycle) and the chain writes one file into the web-served exports directory. Use a unique filename, never touch session keys, and delete both the probe file and the webshell with the shell you gain. CONFIG/FLUSHALL/MODULE/SCRIPT are renamed away server-side, so the classic RDB-write path is closed.

- status: proposed
