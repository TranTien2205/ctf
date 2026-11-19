# Reading phpinfo() — the structured leak

phpinfo() is the single densest disclosure page in PHP apps: env vars, paths, modules, loaded config, version details.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| phpinfo table rendered | full config | extract everything |
| _ENV/_SERVER rows | env vars | secrets and paths |
| Loaded modules list | module inventory | which attacks exist |
| disable_functions value | hardening level | what you CAN'T do |

## Steps

1. Probe /phpinfo.php /info.php /test.php /i.php /p.php.
2. Extract: DOCUMENT_ROOT, _ENV keys, disable_functions, open_basedir.
3. Module list answers which extensions (and their bugs) exist.
4. env rows carry DB creds, API keys — treat as secrets.

## Falsifier

Falsifier — no phpinfo page exists: channel closed.

## Traps

- DOCUMENT_ROOT + open_basedir = the traversal boundaries for file-read classes.
- disable_functions tells you whether a webshell can exec.
- phpinfo leaks are usually dev leftovers — also check /phpinfo.php under admin dirs.

## Commands

```bash
for p in /phpinfo.php /info.php /test.php; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`status-pages.md` · `framework-debug.md`
