# Backup and archive exposure — playbook

Source archives, DB dumps, and site backups are the bulk-download form of disclosure: one fetch returns the whole handout, sometimes with history.

## Ordered playbook

1. Probe: /backup.zip /app.zip /www.zip /<site>.zip /db.sql /dump.sql /backup.tar.gz.
2. For archives: download, list contents first (unzip -l / tar -tzf), then extract to a scratch dir.
3. For .sql dumps: grep for flag{, password, INSERT INTO users.
4. For editor backups of code files (index.php~, .index.php.swp): read for source/secrets.
5. Check archive dates — an old backup may hold creds since rotated, still worth noting.

## Falsifier

Falsifier — the bounded archive list returns catch-all/404 throughout and no hint names a custom archive name: nothing conventional is exposed. Don't fuzz for archive names — out of scope.

## Commands

```bash
for p in /backup.zip /app.zip /db.sql; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```
