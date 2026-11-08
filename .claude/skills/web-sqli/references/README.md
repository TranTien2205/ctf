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
| Column count or sort expression is suspected | `detection.md`, then the named ORDER BY case in `extended-corpus.md` if needed |
| A file must be read or written through database privileges | `file-operations.md` |
| A filter blocks syntax | `waf-evasion.md` |
| The value is stored and consumed later | `extended-corpus.md` — Second-Order SQL Injection |
| A sort key or `ORDER BY` expression is client-controlled | `extended-corpus.md` — ExpressionEngine FileManager ORDER BY Sort-Key SQLi |
| The body carries an object/operator query | `../../web-nosqli/SKILL.md` and `../../web-nosqli/references/operators.md` |
| A named historical CTF variant is not covered above | `extended-corpus.md` |

## Loading rule

The `../SKILL.md` file is enough for routine recognition and the first probe. The
reference map is the second decision point for a difficult challenge. Open the
smallest matching file, and only open `extended-corpus.md` when the challenge
shape or variant is named. A reference is technique knowledge, not proof of a
finding; evidence still goes through the normal hooks and controller.
