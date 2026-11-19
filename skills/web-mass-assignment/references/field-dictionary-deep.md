# Field dictionary deep — the field-name taxonomy by decision gate

## Privilege gates — the fields authorization reads

```
role  roles  user_role  userRole  role_id  access_role  role_ids
isAdmin  is_admin  admin  isAdminFlag  admin_flag  superuser
isStaff  is_staff  staff  moderator  is_moderator  operator
internal  employee  developer  debug  test  qa  auditor  god  root
permissions  permission  scopes  scope  authorities  capabilities
groups  group  roles[]  teams  team  entitlements  rights
accessLevel  access_level  level  tier  rank  clearance  privilege
privileges  canAdmin  can_admin  is_poweruser  is_sudo  su
type  user_type  _t  __t  account_type  membership_type
```

The gate reads ONE of these — the inventory shows which. `role` on
the model → `role` probe; `isAdmin` on the model → `isAdmin`. The
gate's field, not the dictionary's, is the target.

## Verification gates — the fields state checks read

```
verified  isVerified  is_verified  email_verified  emailVerified
email_verified_at  phone_verified  sms_verified  activated
is_active  isActive  active  enabled  approved  is_approved
isApproved  confirmed  is_confirmed  pending_review  pendingReview
review_required  approved_by  status  state  workflow_state
onboarding_complete  mfa_enabled  mfaEnabled  totp_enabled
otp_required  passwordless  trust_level  trusted  known_device
skip_verification  bypass_2fa  verification_token  activation_token
```

The verify-skip fields — `verified:true` bound at register skips the
email step; `mfa_enabled:false` bound disables a gate.

## Economic gates — the fields totals/balances read

```
balance  credits  wallet  coins  points  tokens  score  xp  karma
price  cost  amount  total  subtotal  unit_price  discount
discount_percent  coupon  free_shipping  freeShipping
price_override  lifetime_discount  salary  rate  commission
payout  credit_limit  debt  invoice_paid  paid  is_paid
payment_verified  currency  tax  shipping  fee  vat
```

The economic surface — bound `price`/`total`/`discount` reaching the
checkout; bound `balance`/`credits` reaching the spend.

## Plan gates — the fields entitlement checks read

```
plan  plan_id  tier  subscription  subscription_type
subscriptionTier  seats  quota  limits  rate_limit  api_limit
bandwidth_limit  storage_quota  feature_flags  features
entitlements  package  level_name  pro  premium  enterprise
trial  lifetime  vip  founder  plan_tier  billing_tier
```

The entitlement surface — bound `plan`/`tier`/`subscription` opening
the premium gate.

## Ownership gates — the fields access checks read

```
owner  owner_id  ownerId  user_id  userId  account_id  accountId
created_by  createdBy  modified_by  modifiedBy  author_id  authorId
tenant  tenant_id  tenantId  org  org_id  orgId  organization
company  company_id  department  team_id  workspace  workspaceId
parent_id  parentId  project_id  projectId  scope_id  group_id
```

The ownership surface — `author_id`/`owner_id`/`tenant_id` grafting to
another principal.

## Workflow gates — the fields state machines read

```
status  state  phase  stage  step  current_step  order_status
payment_status  shipping_status  fulfillment  review_status
moderation_status  flag  flags  marked  archived  deleted
is_deleted  deleted_at  soft_delete  locked  frozen  suspended
banned  muted  restricted  resolved  closed  completed  shipped
```

The workflow surface — bound `status`/`state`/`step` skipping the
workflow edge.

## Internal/system gates

```
debug  verbose  dev  development  test_mode  testMode
maintenance_mode  dry_run  admin_note  internal_note
internal_comment  is_system  isSystem  system  service_account
serviceAccount  bot  automation  scheduled  cron_enabled
password_hash  passwordHash  salt  secret  api_key  apiKey
token  session_id  sessionId  csrf_token  private_key
encryption_key  signing_key  ip_whitelist  whitelist  blacklist
```

The system surface — `debug`/`internal`/`is_system`/`service_account`
fields opening operator paths.
