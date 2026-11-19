# Extended corpus — the business-logic probe library, expanded

Every row is one probe. Each needs its baseline pair and its falsifier.
Grouped by mechanism; within each, ordered cheapest-first.

## Mass assignment — the field dictionary

### Role / privilege

```
role=admin               role=administrator        role=root
role=superuser           role=staff                role=moderator
role=owner               role=system               role=service
isAdmin=true             is_admin=true             admin=true
isAdmin=1                isAdmin=yes               superuser=true
staff=true               moderator=true            internal=true
permissions=admin        permissions=["*"]         permissions=["admin","user"]
scope=admin              scope="*"                 groups=["admin"]
group=wheel              roles=["admin"]           userType=admin
accountType=admin        level=99                  accessLevel=9
privilege=admin          flags=admin               flags=0xFFFF
```

### State / verification

```
verified=true            isVerified=true           is_verified=true
emailVerified=true       email_verified=true       active=true
activated=true           approved=true             enabled=true
banned=false             locked=false              deleted=false
confirmed=true           status=active             state=verified
mfa=false                totpEnabled=false         otp_required=false
passwordless=true        requiresApproval=false    pendingReview=false
```

### Balance / economics

```
balance=1000000          credits=999999            wallet=9999999
coins=100000             points=999999             tokens=1000000
score=999999             xp=999999                 karma=10000
freeShipping=true        discount=100              coupon=VIPCARD
lifetimeDiscount=100     priceOverride=0           cost=0
```

### Ownership / identity

```
owner=<uid>              ownerId=1                 userId=1
accountId=0              tenantId=0                orgId=1
company=internal         department=engineering    employeeId=1
createdBy=system         modifiedBy=admin          authorId=1
parentId=0               teamId=1                  workspaceId=0
```

### Plan / entitlement

```
plan=enterprise          plan=pro                  tier=premium
subscription=premium     subscriptionType=lifetime  seat=unlimited
quota=-1                 rateLimit=0               apiLimit=999999
features=["*"]           featureFlags={"all":true} entitlements=admin
```

### Nested / prototype-reaching

```
{"user":{"role":"admin"}}            {"user":{"isAdmin":true}}
{"account":{"role":"admin"}}         {"profile":{"verified":true}}
{"meta":{"role":"admin"}}            {"settings":{"admin":true}}
user.role=admin                      user[role]=admin
account.role=admin                   profile.verified=true
__proto__[role]=admin                __proto__={"role":"admin"}
constructor.prototype.role=admin     constructor[prototype][role]=admin
```

### Duplicate-key / parser-conflict

```
?role=user&role=admin                      (last-wins frameworks)
{"role":"user","role":"admin"}             (duplicate JSON keys)
role=user&Role=admin                       (case collision)
%72ole=admin                               (encoded key reaching a
                                            different parser path)
```

## Numeric boundary — the value alphabet, expanded

### Sign and zero

```
-1     -0     +0     -0.0    0.0     -0e0    "−1" (unicode minus)
```

### Sub-integer

```
0.1    0.0000001     0.5     -0.5    1.0000000000000002
```

### Float specials

```
NaN    nan    NAN    Infinity    inf    INF    -Infinity    -inf
1e309  -1e309  1e308  5e-324   (min subnormal)   1.7976931348623157e308
```

### Integer boundaries

```
2147483647        (INT32_MAX)
2147483648        (INT32_MAX + 1)
-2147483648       (INT32_MIN)
-2147483649       (INT32_MIN - 1)
4294967295        (UINT32_MAX)
4294967296        (UINT32_MAX + 1)
9223372036854775807   (INT64_MAX)
9223372036854775808   (INT64_MAX + 1)
18446744073709551615  (UINT64_MAX)
9007199254740991  (JS MAX_SAFE_INTEGER)
9007199254740992  (MAX_SAFE_INTEGER + 1 — precision loss)
```

### Alternative encodings

```
0x10    0X10    0o10    0b1010    010    08    09
1_000   1,000   1 000   1'000     1.000,00 (locale)    1,000.00
+1      - 1     --1     +-1       " 1"    "1 "    "1\n"
```

### Type confusion

```
"1"       "1.0"     "one"     true      false     null
[]        ["1"]     {}        {"value":1}       [[]]
```

## Workflow skip — the step permutations

For an N-step flow `S1 → S2 → … → SN`:

```
SN alone (no prior steps)                    — the canonical skip
SN-1 alone, then SN                          — partial skip
S1, SN (skip middle)                         — interior skip
S3, S1, SN (out of order)                    — ordering assumption
S1 twice, then SN                            — duplicate-step state
GET SN (method change)                       — read-only transition
SN with step=N-1 claimed in body             — lying state param
SN with another user's flow-id               — cross-flow skip
SN with expired session                      — terminal survives expiry
step=0  step=-1  step=N+1  step=MAX          — step index bounds
```

## State replay — the permutations

```
A,A          serial replay
A,B,A        interleaved identities
A,A'         same key, mutated body
A(delay),A   replay after expiry window
A(user1),A(user2)      cross-user
A(object1),A(object2)  cross-object
A → undo → A           re-entry after compensation
```

## Time — the permutations

```
expiry=<now-1>          expiry=<now>            expiry=<now+1>
expiry=0                expiry=-1               expiry=epoch-max
notBefore=<now+1>       notBefore=<now>         notBefore=<now-1>
createdAt=1970          createdAt=<future>      timestamp=0xFFFFFFFF
date=2038-01-19         date=2038-01-20         date=2106 (uint32 wrap)
```

## Sequence — the permutations

```
nonce=<prev-1>          nonce=<prev>            nonce=<prev+2>
id=0                    id=-1                   id=<MAX>
sequence=<first>        sequence=<overflow>     requestId=<reused>
```

## Trust-in-earlier-step — the carriers

```
hidden-field: price, total, discount, subtotal, tax, shipping
param-carried: state, step, token, csrf (the token itself trusted)
header-carried: Referer, Origin, X-Forwarded-*, X-Real-IP
cookie-carried: step=, state=, verified=, role=, cart=
body-carried: userId, orderId, amount (server minted upstream)
```
