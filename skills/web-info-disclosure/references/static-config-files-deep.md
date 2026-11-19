# Static config file exposure — deep

web.config, .htaccess, nginx.conf served inside the app, robots-style configs: the server's own ruleset as readable text.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — no server config file is served: channel closed.

## Highest-cost traps

- .htpasswd hashes crack with hashcat -m 1600 (apr1) etc.
- web.config may have protected-paths lists = the hidden route inventory.
- A served .htaccess sometimes exposes the auth realm name.

## Commands

```bash
for p in /web.config /.htaccess /.htpasswd /nginx.conf; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`source-disclosure.md` · `env-config-leaks.md`
