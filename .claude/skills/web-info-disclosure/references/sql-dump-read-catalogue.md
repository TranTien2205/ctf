# SQL dump extraction — case catalogue

A .sql/.sql.gz/.dump file is the whole database as text — creds, hashes, and often the flag itself.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | /db.sql /dump.sql /backup.sql 200 | DB dump | grep for creds/flag |
| 2 | INSERT INTO users | user table | admin creds/hashes |
| 3 | flag-shaped strings | the flag | read directly |

## Falsifier

Falsifier — no dump file served: channel closed unless a hint names a custom dump name.
