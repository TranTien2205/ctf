# Source disclosure — served code files

When the server serves source instead of executing it — backup extensions, misconfigured handlers, static mounts of app dirs — you read the application itself.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| file.php~ or file.php.bak returns code | editor backup | read source |
| /app/ or /src/ serves .py/.js/.php as text | source mount | walk the tree |
| composer.json/package.json/requirements.txt 200 | dependency disclosure | gadget_lookup |
| Dockerfile / Makefile / Procfile served | build config | paths and commands |

## Steps

1. Probe code-adjacent names: index.php~, index.php.bak, .index.php.swp, app.py, main.py.
2. Probe manifest files: composer.json, package.json, requirements.txt, Gemfile, go.mod.
3. If a source mount exists, walk it like a repo: entry files, config, routes.
4. Manifests → tools/gadget_lookup.py --lockfile for versioned gadget recall.

## Falsifier

Falsifier — source paths return 404/403 or executed output only: no raw source is served. The handout is closed; work black-box.

## Traps

- A manifest alone gives versions → gadget_lookup turns them into known-gadget recall.
- Static mounts of /src/ may exclude config files that are still reachable by direct name.
- Served .git is the extreme case — see git-exposure.

## Commands

```bash
python3 tools/gadget_lookup.py --lockfile <handout>/package-lock.json
for p in /index.php~ /package.json /composer.json /requirements.txt; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`git-exposure.md` · `backup-archives.md`
