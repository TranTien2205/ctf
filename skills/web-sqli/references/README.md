# SQL injection reference map

This directory belongs to the canonical `web-sqli` class skill. Open one named
file after the first probe; do not read the whole directory.

## Choose by observed signal

| Signal or task | Open |
|---|---|
| The injection point is not yet stable | `detection.md` |
| True and false responses differ | `boolean-blind.md` |
| Only response timing differs | `time-blind.md` |
| The database leaks an error containing data | `error-based.md` |
| The DBMS is known | `mysql.md`, `postgresql.md`, `mssql.md`, or `oracle.md` |
| A file must be read or written through database privileges | `file-operations.md` |
| A filter blocks syntax | `waf-evasion.md` |
| The body carries an object/operator query | `nosql.md`, then return to `../../web-nosqli/SKILL.md` for class handling |
| A named historical CTF variant is not covered above | `extended-corpus.md` |

## Loading rule

The `../SKILL.md` file is enough for routine recognition and the first probe. The
reference map is the second decision point for a difficult challenge. Open the
smallest matching file, and only open `extended-corpus.md` when the challenge
shape or variant is named. A reference is technique knowledge, not proof of a
finding; evidence still goes through the normal hooks and controller.
