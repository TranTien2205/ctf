# Field notes — Unrestricted file upload

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

## 2026-09-15 · Amidst Us · proposed

- source note: `solved/amidst-us.md`
- chain card: `knowledge/chains/htb-amidst-us-imagemath-eval-static-folder-exfil.json`
- verification: verified_live — flag string read from /static/f.txt on the rebuilt deployment
- classified as: `web-file-upload` (score 2.5, 2 signals matched)
- also matched: `web-sqli` (2.5), `web-race-condition` (1.5), `web-auth-session` (1.5)
- signals that fired: import, upload

**Confirming probe that worked**

> background[0] = eval("__import__('time').sleep(6)") compared with a ~1s baseline request

Expected: response time near 7s instead of ~1s

Falsifier: the response stays at the baseline duration (eval not executed), or every string in background is rejected before the pipeline

**Traps recorded on this solve**

- raw arithmetic strings in the injection slot are rejected before execution; the working payload needs the eval("...") wrapper
- a fast 400 can hide a command that already executed as a side effect; verify the write result downstream
- quoted shells inside the f-string need exactly one escaping level per layer or the whole expression never parses
- the static_folder is guessable but not required: flask.current_app hands out the real path from inside the request
- class budget accounting counts the exploratory probes; keep falsifiers separate so the confirmed mechanism keeps a probe slot for the exfil round

**Blast radius**: arbitrary python runs inside the challenge container; a cp or rm with a wrong path can disturb app state, and an eval(exit()) kills the single-process dev server permanently

- status: proposed
