# SQL dump extraction

A .sql/.sql.gz/.dump file is the whole database as text — creds, hashes, and often the flag itself.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| /db.sql /dump.sql /backup.sql 200 | DB dump | grep for creds/flag |
| INSERT INTO users | user table | admin creds/hashes |
| flag-shaped strings | the flag | read directly |

## Steps

1. Probe: /db.sql /dump.sql /backup.sql /database.sql /<site>.sql /mysql.sql.
2. Download; grep for flag{, password, INSERT INTO, CREATE TABLE.
3. Password hashes in dumps are crackable (hashcat) — a chain step.
4. Check dump headers for the DBMS and version.

## Falsifier

Falsifier — no dump file served: channel closed unless a hint names a custom dump name.

## Traps

- Dumps can be huge — grep/stream, never open in an editor.
- Compressed dumps (.sql.gz) need gunzip before grep.
- Partial dumps still carry the most valuable tables (users).

## Commands

```bash
for p in /db.sql /dump.sql /backup.sql /database.sql; do curl -s -o /tmp/r -w "$p %{http_code} %{size_download}\n" "$BASE$p"; done
```

## Cross-references

`backup-archives.md` · `env-config-leaks.md`
