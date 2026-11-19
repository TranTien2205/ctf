# Backup and archive exposure — surface variants

Source archives, DB dumps, and site backups are the bulk-download form of disclosure: one fetch returns the whole handout, sometimes with history.

## When the shape changes

| Variant | What changes | Route |
|---|---|---|
| /backup.zip|app.zip|www.zip|site.tar.gz 200 | archive exposed | download + extract |
| <name>.sql or dump.sql 200 | DB dump | read for creds/flag |
| file~, file.bak, file.swp, file.old 200 | editor backup | read source |
| /phpinfo.php or test.zip | leftover dev artifact | read |

## Variant-specific traps

- A huge archive may be a zip bomb or decoy — list before extracting, extract to a bounded dir.
- SQL dumps can be GBs — grep, don't open.
- The archive may 403 while directory listing shows it — combine with directory-listing.
- Timestamps in the dump tell you if creds plausibly rotated.

## Falsifier

Falsifier — the bounded archive list returns catch-all/404 throughout and no hint names a custom archive name: nothing conventional is exposed. Don't fuzz for archive names — out of scope.

## Cross-references

`env-config-leaks.md` · `directory-listing.md` · `source-disclosure.md`
