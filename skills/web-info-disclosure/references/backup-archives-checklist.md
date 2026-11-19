# Backup and archive exposure — operational checklist

Source archives, DB dumps, and site backups are the bulk-download form of disclosure: one fetch returns the whole handout, sometimes with history.

## Checklist

- [ ] Probe: /backup.zip /app.zip /www.zip /<site>.zip /db.sql /dump.sql /backup.tar.gz.
- [ ] For archives: download, list contents first (unzip -l / tar -tzf), then extract to a scratch dir.
- [ ] For .sql dumps: grep for flag{, password, INSERT INTO users.
- [ ] For editor backups of code files (index.php~, .index.php.swp): read for source/secrets.
- [ ] Check archive dates — an old backup may hold creds since rotated, still worth noting.

## Abort conditions

- A huge archive may be a zip bomb or decoy — list before extracting, extract to a bounded dir.
- SQL dumps can be GBs — grep, don't open.
- The archive may 403 while directory listing shows it — combine with directory-listing.

## Falsifier

Falsifier — the bounded archive list returns catch-all/404 throughout and no hint names a custom archive name: nothing conventional is exposed. Don't fuzz for archive names — out of scope.

## Cross-references

`env-config-leaks.md` · `directory-listing.md` · `source-disclosure.md`
