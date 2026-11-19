# Payload dictionary — field names × value shapes × carriers

## Privilege — the fields authorization reads

```
role         "admin" | "superuser" | "moderator" | "operator" | 1 | true
is_admin     true | "true" | 1 | "yes"
isAdmin      true | "true" | 1
is_staff     true | "true" | 1
superuser    true | 1
admin        true | 1
internal     true | 1
moderator    true | 1
permissions  ["*"] | ["admin"] | ["all"] | {"all":true}
scopes       ["admin"] | ["*"] | ["write"]
groups       ["admin"] | [{"id":1}] | [{"name":"admin"}]
roles        ["admin"] | ["superuser"]
role_ids     [1] | [2]
access_level 9 | "admin" | 99
clearance    "top" | "admin" | 9
tier         "admin" | "pro" | 9
type         "admin" | "staff"
user_type    "admin" | "staff"
_t           "AdminUser" | "Admin"
__t          "Admin" | "AdminUser"
account_type "admin" | "staff"
user_level   9 | 99
auth_level   9
security_level 9
```

## Verification — the fields state checks read

```
verified         true | "true" | 1 | "yes"
is_verified      true | 1
isVerified       true | 1
email_verified   true | 1
emailVerified    true | 1
email_verified_at "2024-01-01" | <timestamp>
is_active        true | 1
isActive         true | 1
active           true | 1
activated        true | 1
approved         true | 1
is_approved      true | 1
isApproved       true | 1
confirmed        true | 1
is_confirmed     true | 1
onboarding_complete true | 1
mfa_enabled      false | 0          ← disables a gate
otp_required     false | 0          ← disables
bypass_2fa       true | 1           ← disables
skip_verification true | 1
status           "active" | "approved" | "verified"
state            "active" | "done"
workflow_state   "complete"
```

## Economics — the fields totals/balances read

```
balance      99999 | 1000000 | 1e6 | "99999"
credits      99999 | 1e6
wallet       99999
coins        99999
points       99999
tokens       99999
score        99999
price        0 | 0.01 | -1
unit_price   0 | 0.01
cost         0
amount       0
total        0 | 0.01 | -1
subtotal     0
discount     100 | "100"
discount_percent 100
coupon       "FREE100" | "ADMIN"
free_shipping true | 1
price_override 0
currency     "AAA" | "XXX" | ""
tax          0
shipping     0
paid         true | 1
is_paid      true | 1
invoice_paid true | 1
payment_verified true | 1
credit_limit 1e9
```

## Plan — the fields entitlement checks read

```
plan             "enterprise" | "pro" | "admin"
plan_id          5 | 9 | 99
tier             "pro" | "enterprise" | 9
subscription     "pro" | {"type":"lifetime"}
subscription_type "lifetime" | "enterprise"
seats            999 | -1
quota            1e9 | -1
limits           {"requests":-1} | {"api":99999}
rate_limit       0 | -1
features         ["premium","admin"] | ["*"]
entitlements     ["*"]
pro              true | 1
premium          true | 1
lifetime         true | 1
vip              true | 1
founder          true | 1
```

## Ownership — the fields access checks read

```
owner_id    1 | <other-user-id>
author_id   1
user_id     1
created_by  1
tenant_id   1
org_id      1
team_id     1
company_id  1
workspace_id 1
project_id  1
parent_id   1
```

## Workflow — the fields state machines read

```
status          "shipped" | "completed" | "approved" | "resolved"
state           "done" | "complete" | "final"
current_step    99 | "complete"
order_status    "shipped" | "delivered"
payment_status  "paid" | "settled"
review_status   "approved"
moderation_status "approved"
correct         true | 1          ← bound answer
flagged         false | 0
approved        true | 1
```

## The value-shape variants

| Field | String | Bool | Int | Array | Object |
|---|---|---|---|---|---|
| role | `"admin"` | — | `1` | `["admin"]` | `{"name":"admin"}` |
| is_admin | `"true"` | `true` | `1` | — | — |
| groups | `"admin"` | — | — | `["admin"]` | `[{"id":1}]` |
| verified | `"yes"`/`"1"` | `true` | `1` | — | — |
| balance | `"9999"` | — | `9999` | — | — |
| plan | `"pro"` | — | `5` | `["pro"]` | `{"type":"pro"}` |
| permissions | — | — | — | `["*"]` | `{"all":true}` |
