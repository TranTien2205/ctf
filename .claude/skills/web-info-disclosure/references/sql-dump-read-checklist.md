# SQL dump extraction — checklist

A .sql/.sql.gz/.dump file is the whole database as text — creds, hashes, and often the flag itself.

## Checklist

- [ ] Probe: /db.sql /dump.sql /backup.sql /database.sql /<site>.sql /mysql.sql.
- [ ] Download; grep for flag{, password, INSERT INTO, CREATE TABLE.
- [ ] Password hashes in dumps are crackable (hashcat) — a chain step.
- [ ] Check dump headers for the DBMS and version.

## Abort conditions

- Dumps can be huge — grep/stream, never open in an editor.
- Compressed dumps (.sql.gz) need gunzip before grep.
- Partial dumps still carry the most valuable tables (users).

## Falsifier

Falsifier — no dump file served: channel closed unless a hint names a custom dump name.
