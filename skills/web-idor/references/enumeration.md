# IDOR - General Enumeration Techniques

## Autorize/Burp Extension Approach
```
1. Login as User A (low priv), capture all requests in Burp
2. Login as User B (victim/higher priv) in a second session
3. Use Autorize extension: replay User A's requests with User B's session token missing/swapped
4. Flag responses that return 200 + same data as authenticated response (bypass detected)
```

## Manual Two-Account Testing Methodology
```
Setup: Create 2 accounts (User A, User B) at same privilege level, or 1 low + 1 admin

For each authenticated endpoint:
1. As User A, note the object ID(s) returned (own profile ID, order ID, etc.)
2. As User B, try accessing User A's object IDs using User B's session/token
3. Compare: does User B get User A's data? (Horizontal IDOR)
4. As User A (low-priv), try accessing admin-only endpoints (Vertical IDOR/privilege escalation)
```

## Parameter Fuzzing for Hidden ID Fields
```bash
# Try common ID parameter names even if not visible in normal flow
?id=1 ?user_id=1 ?uid=1 ?account_id=1 ?profile_id=1 ?ref=1 ?doc_id=1
```

## Burp Intruder for Bulk Testing
```
1. Capture request with object ID as insertion point
2. Set payload type to Numbers (sequential range) or list of known IDs
3. Compare response length/status across all payloads
4. Filter results showing 200 OK with substantive different content (not error page)
```

## Response Comparison Techniques
```python
import requests

def test_idor(base_url, session_a_cookie, object_ids):
    baseline_len = None
    for obj_id in object_ids:
        r = requests.get(f"{base_url}/api/object/{obj_id}",
                         cookies={"session": session_a_cookie})
        print(f"ID {obj_id}: status={r.status_code} len={len(r.text)}")
```

## Blind IDOR Indicators (no direct data returned but action succeeds)
```
- Response time difference (object exists vs doesn't)
- Different error messages ("not found" vs "forbidden" vs generic 500)
- Side effects observable elsewhere (e.g., DELETE succeeds silently, verify by re-fetching)
```

## Encoded/Obfuscated ID Enumeration
```python
import base64
# If ID appears base64 encoded
for i in range(1, 100):
    encoded = base64.b64encode(str(i).encode()).decode()
    print(f"{i} -> {encoded}")

# If ID is hashed (MD5 of sequential number - check via known samples)
import hashlib
for i in range(1, 100):
    h = hashlib.md5(str(i).encode()).hexdigest()
    print(f"{i} -> {h}")
```

## Checklist for Full Coverage
```
1. Test all CRUD operations (Create/Read/Update/Delete) for each object type
2. Test both path-based (/users/123) and parameter-based (?id=123) references
3. Test nested/related object access (user's orders, orders' line items)
4. Test with completely unauthenticated request (no session at all)
5. Test with expired/invalidated session token
6. Test API and web UI separately - protections may differ
7. Document exact request/response pairs as evidence for report
```
