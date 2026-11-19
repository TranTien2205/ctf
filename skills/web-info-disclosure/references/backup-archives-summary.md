# Backup and archive exposure — summary

Source archives, DB dumps, and site backups are the bulk-download form of disclosure: one fetch returns the whole handout, sometimes with history.

## Signal → route

- /backup.zip|app.zip|www.zip|site.tar.gz 200 → download + extract
- <name>.sql or dump.sql 200 → read for creds/flag
- file~, file.bak, file.swp, file.old 200 → read source
- /phpinfo.php or test.zip → read

## Falsifier

Falsifier — the bounded archive list returns catch-all/404 throughout and no hint names a custom archive name: nothing conventional is exposed. Don't fuzz for archive names — out of scope.
