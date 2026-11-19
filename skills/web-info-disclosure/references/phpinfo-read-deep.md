# Reading phpinfo() — the structured leak — deep

phpinfo() is the single densest disclosure page in PHP apps: env vars, paths, modules, loaded config, version details.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — no phpinfo page exists: channel closed.

## Highest-cost traps

- DOCUMENT_ROOT + open_basedir = the traversal boundaries for file-read classes.
- disable_functions tells you whether a webshell can exec.
- phpinfo leaks are usually dev leftovers — also check /phpinfo.php under admin dirs.

## Commands

```bash
for p in /phpinfo.php /info.php /test.php; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`status-pages.md` · `framework-debug.md`
