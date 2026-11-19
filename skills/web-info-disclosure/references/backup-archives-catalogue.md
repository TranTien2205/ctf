# Backup and archive exposure — case catalogue

Source archives, DB dumps, and site backups are the bulk-download form of disclosure: one fetch returns the whole handout, sometimes with history.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /backup.zip|app.zip|www.zip|site.tar.gz 200 | archive exposed | download + extract |
| 2 | <name>.sql or dump.sql 200 | DB dump | read for creds/flag |
| 3 | file~, file.bak, file.swp, file.old 200 | editor backup | read source |
| 4 | /phpinfo.php or test.zip | leftover dev artifact | read |

## Falsifier

Falsifier — the bounded archive list returns catch-all/404 throughout and no hint names a custom archive name: nothing conventional is exposed. Don't fuzz for archive names — out of scope.

## Coverage notes

- A huge archive may be a zip bomb or decoy — list before extracting, extract to a bounded dir.
- SQL dumps can be GBs — grep, don't open.
- The archive may 403 while directory listing shows it — combine with directory-listing.
- Timestamps in the dump tell you if creds plausibly rotated.

## Cross-references

`env-config-leaks.md` · `directory-listing.md` · `source-disclosure.md`
