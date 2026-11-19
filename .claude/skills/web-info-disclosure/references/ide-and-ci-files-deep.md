# IDE and CI config exposure — deep

.idea/, .vscode/, .gitlab-ci.yml, .travis.yml, .github/workflows/, docker-compose.yml: build-time secrets and internal layout.

## Boundary conditions

- Every positive read diffs against the catch-all baseline; status alone proves nothing.
- A 403 on a real path is a candidate bypass (verbs/Host/path) — try before recording dead.
- Content found is evidence; its use is the owning class's job.
- Artifacts containing secrets are handled, not committed.

## Falsifier

Falsifier — none of the build-time files are served: the channel is closed.

## Highest-cost traps

- CI files often list secret NAMES not values — still an inventory of what to hunt.
- docker-compose usually reveals internal hostnames the app depends on.
- .idea can contain run configurations with credentials.

## Commands

```bash
for p in /.gitlab-ci.yml /docker-compose.yml /Dockerfile /.idea/workspace.xml; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`env-config-leaks.md` · `source-disclosure.md`
