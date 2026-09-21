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
