# Source disclosure — served code files — case catalogue

When the server serves source instead of executing it — backup extensions, misconfigured handlers, static mounts of app dirs — you read the application itself.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | file.php~ or file.php.bak returns code | editor backup | read source |
| 2 | /app/ or /src/ serves .py/.js/.php as text | source mount | walk the tree |
| 3 | composer.json/package.json/requirements.txt 200 | dependency disclosure | gadget_lookup |
| 4 | Dockerfile / Makefile / Procfile served | build config | paths and commands |

## Falsifier

Falsifier — source paths return 404/403 or executed output only: no raw source is served. The handout is closed; work black-box.

## Coverage notes

- A manifest alone gives versions → gadget_lookup turns them into known-gadget recall.
- Static mounts of /src/ may exclude config files that are still reachable by direct name.
- Served .git is the extreme case — see git-exposure.

## Cross-references

`git-exposure.md` · `backup-archives.md`
