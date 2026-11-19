# Key and certificate files — deep

.pem, .key, .crt, .p12, id_rsa files: raw key material served over HTTP — the most direct disclosure there is.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — no key files served: channel closed.

## Highest-cost traps

- Private keys are never committed to the repo — extract, use, redact.
- A key may be passphrase-protected — note and try the usual suspects.
- SAN fields on certs leak internal hostnames.

## Commands

```bash
for p in /id_rsa /.ssh/id_rsa /server.key /key.pem; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`env-config-leaks.md` · `chaining.md`
