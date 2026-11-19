# Detection surface deep — the full writable-surface enumeration

## The model-as-surface

Every model attribute the binder CAN reach is the writable surface —
the form's declared fields are the SUBSET the developer intended. The
gap `model fields - form fields` is the probe set.

## The surface by discovery channel

| Channel | Yields | The command |
|---|---|---|
| read-back `GET` | returned keys | `curl $BASE/api/me \| jq 'keys'` |
| sibling `GET` | another object's fields | `curl $BASE/api/users/<id> \| jq 'keys'` |
| bundle | JS-constructed objects | `bundle_miner --url ... --out ...` |
| errors | schema field names | wrong-typed probe → error |
| docs | the model dump | `/openapi.json`, `/swagger.json` |
| GraphQL | the args/input types | `{__schema{mutationType{fields{name args{name}}}}}` |
| admin views | the full record | `GET /admin/users`, staff API |
| timestamps | `createdAt`, `__v`, `deleted_at` | implicit in every record |
| associations | child model fields | `{"membership":{...}}` nested probes |

## The hidden-field families

**Privileged** (the escalation targets):
```
role is_admin isAdmin is_staff superuser admin internal
permissions groups roles access_level clearance tier
moderator operator developer debug is_sudo god root sysadmin
type user_type _t __t account_type user_level auth_level
```

**State** (the workflow-skip):
```
verified is_active isActive activated approved is_approved
confirmed email_verified_at onboarding_complete status state
mfa_enabled otp_required bypass_2fa skip_verification
```

**Economic** (the totals):
```
balance credits wallet coins points tokens score
price unit_price cost amount total subtotal discount
coupon currency tax shipping paid is_paid invoice_paid
credit_limit debt payout transaction_limit
```

**Entitlement** (the plan):
```
plan plan_id tier subscription subscription_type seats quota
limits features entitlements rate_limit pro premium vip
lifetime founder license billing_plan membership_tier
```

**Ownership** (the scope):
```
owner_id author_id user_id created_by modified_by
tenant_id org_id team_id company_id workspace_id
project_id parent_id account_id
```

**Workflow** (the state machine):
```
status state phase stage step current_step
order_status payment_status shipping_status fulfillment
review_status moderation_status correct flagged
archived deleted is_deleted deleted_at locked suspended
```

**Internal** (the operator):
```
debug verbose dev test_mode maintenance_mode internal_note
admin_note is_system service_account bot automation
password_hash salt secret api_key token private_key
__v ip_whitelist whitelist
```

## The nested surface

`profile`, `settings`, `preferences`, `billing`, `address`, `metadata`,
`custom`, `extra`, `config`, `options`, `details`, `info`, `data` —
nested objects whose sub-fields the flat allowlist can't see. The
parent's allowlist covers the object AS A UNIT; the merge reaches the
nested fields.

## The association surface

`memberships`, `roles`, `groups`, `subscriptions`, `wallets`,
`permissions`, `verifications` — CHILD models reachable through
`accepts_nested_attributes_for` or `{"membership":{"role":..}}` —
the child's fields bind through the parent's accepted key.

## The write-only surface

`password_hash`, `internal_note`, `admin_note`, `deleted_at`, `__v`,
`salt`, `secret`, `token` — fields that bind but never serialize.
Invisible in read-backs; provable only by exercising the decision or
a second representation (admin view, detail page).

## The discriminator surface

`_t`, `__t`, `type`, `user_type`, `account_type`, `membership_type` —
fields selecting WHICH schema binds. `_t:"AdminUser"` switches to the
privileged sub-schema — a bound field that changes the writable
surface itself.
