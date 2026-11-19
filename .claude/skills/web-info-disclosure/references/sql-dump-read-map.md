# SQL dump extraction — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| /db.sql /dump.sql /backup.sql 200 | DB dump | grep for creds/flag |
| INSERT INTO users | user table | admin creds/hashes |
| flag-shaped strings | the flag | read directly |

## Falsifier

Falsifier — no dump file served: channel closed unless a hint names a custom dump name.
