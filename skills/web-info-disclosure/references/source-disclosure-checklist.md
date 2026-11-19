# Source disclosure — served code files — operational checklist

When the server serves source instead of executing it — backup extensions, misconfigured handlers, static mounts of app dirs — you read the application itself.

## Checklist

- [ ] Probe code-adjacent names: index.php~, index.php.bak, .index.php.swp, app.py, main.py.
- [ ] Probe manifest files: composer.json, package.json, requirements.txt, Gemfile, go.mod.
- [ ] If a source mount exists, walk it like a repo: entry files, config, routes.
- [ ] Manifests → tools/gadget_lookup.py --lockfile for versioned gadget recall.

## Abort conditions

- A manifest alone gives versions → gadget_lookup turns them into known-gadget recall.
- Static mounts of /src/ may exclude config files that are still reachable by direct name.
- Served .git is the extreme case — see git-exposure.

## Falsifier

Falsifier — source paths return 404/403 or executed output only: no raw source is served. The handout is closed; work black-box.

## Cross-references

`git-exposure.md` · `backup-archives.md`
