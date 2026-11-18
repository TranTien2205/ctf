# web-sqli reference corpus — navigation

SKILL.md is the contract: routes, probe, falsifiers, budgets, tool
commands. This directory is the depth — open the file matching your
signal, not the whole corpus.

## Detection & routing

| Signal | File |
|---|---|
| how to probe, baseline, fingerprint, decision rules | `detection.md` |
| compact field tables (fingerprint/operator/operator map) | `cheatsheet.md` |
| giant sorted payload catalogue | `payload-dictionary.md` |
| auth/login/register/reset injection | `auth-bypass.md` |
| edge contexts: INSERT/UPDATE/DELETE/ORDER BY/LIMIT/LIKE | `edge-contexts.md` |
| JSON bodies, GraphQL, XML, headers, multipart transports | `json-graphql.md` |
| ORM/query-builder surfaces: Django, Rails, Hibernate, Sequelize, Laravel, Prisma | `orm-frameworks.md` |
| second-order / stored SQLi loop | `second-order.md` |
| WAF/filter bypass transforms | `waf-evasion.md` |

## Extraction channels

| Channel | File |
|---|---|
| UNION — col count, reflected cols, extraction | `union.md` |
| error-based echo — per-DBMS error channels | `error-based.md` |
| boolean blind — matched pairs, charset, binary search | `boolean-blind.md` |
| time blind — delays, heavy-query, delay-length encoding | `time-blind.md` |
| fast paths — error echo, agg, OOB, delay-length | `advanced-extraction.md` |
| OOB — DNS/HTTP/UNC exfil | `oob.md` |
| file read/write per DBMS | `file-operations.md` |
| write/exec → RCE catalogue | `rce-paths.md` |

## Per-DBMS catalogues

| DBMS | File |
|---|---|
| MySQL | `mysql.md` |
| MariaDB (delta vs MySQL) | `mariadb.md` |
| PostgreSQL | `postgresql.md` |
| MSSQL | `mssql.md` |
| Oracle | `oracle.md` |
| SQLite | `sqlite.md` |
| DB2, H2, Informix, Firebird, HANA, ClickHouse, CockroachDB | `multi-dbms.md` |

## Tools

| Tool | File |
|---|---|
| repo tools + sqlmap invocations + selftests | `tooling.md` |

## Legacy

| File | Note |
|---|---|
| `extended-corpus.md` | the original extended catalogue — kept for compatibility; newer material supersedes sections where they overlap |

## Order of work

```text
detection.md         → channel exists?
   ├─ union.md           UNION surface
   ├─ error-based.md     error echo
   ├─ boolean-blind.md   true/false oracle
   ├─ time-blind.md      timing oracle
   └─ oob.md             outbound channel
↓
cheatsheet.md §3      → which catalog
↓
<payload-dictionary.md §5-§8>  → enum dbs/tables/columns/rows
↓
file-operations.md    → read configs/flag files
rce-paths.md          → write/exec when needed
advanced-extraction.md → when the channel is slow and you need speed
```
