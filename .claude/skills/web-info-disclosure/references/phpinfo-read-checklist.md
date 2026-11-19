# Reading phpinfo() — the structured leak — checklist

phpinfo() is the single densest disclosure page in PHP apps: env vars, paths, modules, loaded config, version details.

## Checklist

- [ ] Probe /phpinfo.php /info.php /test.php /i.php /p.php.
- [ ] Extract: DOCUMENT_ROOT, _ENV keys, disable_functions, open_basedir.
- [ ] Module list answers which extensions (and their bugs) exist.
- [ ] env rows carry DB creds, API keys — treat as secrets.

## Abort conditions

- DOCUMENT_ROOT + open_basedir = the traversal boundaries for file-read classes.
- disable_functions tells you whether a webshell can exec.
- phpinfo leaks are usually dev leftovers — also check /phpinfo.php under admin dirs.

## Falsifier

Falsifier — no phpinfo page exists: channel closed.
