# Backup and archive exposure — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /backup.zip|app.zip|www.zip|site.tar.gz 200 | archive exposed | download + extract |
| <name>.sql or dump.sql 200 | DB dump | read for creds/flag |
| file~, file.bak, file.swp, file.old 200 | editor backup | read source |
| /phpinfo.php or test.zip | leftover dev artifact | read |

## Falsifier

Falsifier — the bounded archive list returns catch-all/404 throughout and no hint names a custom archive name: nothing conventional is exposed. Don't fuzz for archive names — out of scope.
