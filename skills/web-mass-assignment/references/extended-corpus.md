# Extended corpus — additional field-value pairs and carrier shapes

## More privilege fields

```
{"account_type":"admin"}   {"membership":"admin"}   {"user_level":9}
{"userLevel":9}            {"security_level":9}      {"auth_level":9}
{"role_name":"admin"}      {"roleName":"admin"}      {"usergroup":"admin"}
{"user_group":"admin"}     {"access":"admin"}        {"grant":"admin"}
{"capability":"admin"}     {"is_root":true}          {"is_super":true}
{"can_moderate":true}      {"can_edit":true}         {"can_delete":true}
{"can_publish":true}       {"can_admin":true}        {"elevated":true}
{"privileged":true}        {"operator":true}         {"sysadmin":true}
{"domain_admin":true}      {"site_admin":true}       {"org_admin":true}
{"tenant_admin":true}      {"company_admin":true}    {"team_admin":true}
```

## More verification/state fields

```
{"email_confirmed":true}   {"confirmed_at":"2024-01-01"}
{"activation_complete":true} {"setup_complete":true} {"first_login":false}
{"needs_setup":false}      {"requires_action":false} {"action_required":false}
{"email_checked":true}     {"phone_checked":true}    {"kyc_verified":true}
{"kyc_complete":true}      {"identity_verified":true} {"age_verified":true}
{"tos_accepted":true}      {"terms_accepted":true}   {"consent_given":true}
{"gdpr_consent":true}      {"opted_in":true}         {"subscribed":true}
```

## More economic fields

```
{"wallet_balance":99999}   {"account_balance":99999} {"store_credit":99999}
{"gift_card_balance":99999} {"reward_points":99999}  {"loyalty_points":99999}
{"cashback":99999}         {"bonus":99999}           {"grant":99999}
{"allowance":99999}        {"stipend":99999}         {"fund":99999}
{"bank_balance":99999}     {"net_worth":99999}       {"total_credit":99999}
{"available_credit":99999} {"spending_limit":99999}  {"daily_limit":99999}
{"transaction_limit":99999} {"withdrawal_limit":99999}
```

## More plan/entitlement fields

```
{"license":"enterprise"}   {"license_type":"pro"}    {"license_tier":"max"}
{"subscription_plan":"ent"} {"subscription_tier":"pro"} {"sub_level":9}
{"account_tier":"pro"}     {"account_plan":"ent"}    {"billing_plan":"pro"}
{"billing_tier":"ent"}     {"payment_plan":"lifetime"} {"plan_name":"pro"}
{"plan_level":9}           {"tier_level":9}          {"tier_name":"ent"}
{"member_level":9}         {"membership_level":9}    {"membership_tier":"pro"}
{"user_tier":"pro"}        {"user_plan":"ent"}       {"access_tier":"pro"}
```

## More ownership/tenancy fields

```
{"account_owner":1}        {"account_holder":1}      {"record_owner":1}
{"object_owner":1}         {"resource_owner":1}      {"data_owner":1}
{"primary_owner":1}        {"secondary_owner":1}     {"co_owner":1}
{"billing_owner":1}        {"technical_owner":1}     {"admin_owner":1}
{"root_org":1}             {"parent_org":1}          {"owning_org":1}
{"owning_team":1}          {"owning_user":1}         {"owning_account":1}
```

## More workflow/status fields

```
{"order_state":"shipped"}  {"order_phase":"complete"} {"order_step":99}
{"payment_state":"paid"}   {"payment_phase":"settled"} {"payment_step":99}
{"shipping_state":"delivered"} {"delivery_state":"delivered"}
{"fulfillment_state":"done"} {"review_state":"approved"}
{"moderation_state":"ok"}  {"approval_state":"approved"}
{"workflow_state":"done"}  {"workflow_step":99}      {"process_state":"done"}
{"task_state":"complete"}  {"job_state":"done"}      {"request_state":"approved"}
{"ticket_state":"resolved"} {"issue_state":"closed"} {"case_state":"closed"}
```

## More internal/system fields

```
{"admin_access":true}      {"staff_access":true}     {"internal_access":true}
{"dev_access":true}        {"debug_access":true}     {"api_access":true}
{"beta_access":true}       {"early_access":true}     {"preview_access":true}
{"feature_beta":true}      {"beta_tester":true}      {"insider":true}
{"flagged_internal":true}  {"is_internal":true}      {"is_dev":true}
{"is_test":true}           {"test_account":true}     {"demo_account":true}
{"seed_account":true}      {"fixture_account":true}  {"system_user":true}
{"service_user":true}      {"machine_user":true}     {"api_user":true}
```
