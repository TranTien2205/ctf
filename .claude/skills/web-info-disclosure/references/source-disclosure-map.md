# Source disclosure — served code files — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| file.php~ or file.php.bak returns code | editor backup | read source |
| /app/ or /src/ serves .py/.js/.php as text | source mount | walk the tree |
| composer.json/package.json/requirements.txt 200 | dependency disclosure | gadget_lookup |
| Dockerfile / Makefile / Procfile served | build config | paths and commands |

## Falsifier

Falsifier — source paths return 404/403 or executed output only: no raw source is served. The handout is closed; work black-box.
