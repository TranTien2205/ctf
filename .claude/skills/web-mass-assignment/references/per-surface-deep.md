# Per-surface deep — each model's writable surface, mapped

## `User`/`Account` — the primary surface

```
username password email display_name bio avatar
role is_admin isAdmin is_staff superuser admin internal
permissions groups roles access_level clearance tier
verified is_active approved activated email_verified_at
balance credits plan subscription quota
tenant_id org_id team_id created_by
debug is_system service_account _t __v
created_at updated_at deleted_at last_login
```

**Probes by priority**: `role`/`is_admin`/`is_staff` (privilege) →
`verified`/`is_active`/`approved` (state) → `balance`/`credits`
(economics) → `plan`/`tier` (entitlement) → `permissions`/`groups`
(scope) → `_t`/`type` (discriminator) → `debug`/`internal` (operator).

## `Order`/`Purchase`/`Transaction` — the economic surface

```
item_id product_id product quantity
price unit_price cost amount
discount discount_percent coupon promo_code
total subtotal shipping tax currency
status state payment_status order_status fulfillment
paid is_paid invoice_paid
customer_id user_id buyer_id
```

**Probes**: `price:0`, `discount:100`, `total:0`, `quantity:-1`,
`currency`, `status:"shipped"`, `paid:true` — the fields the totals
code reads. The exercise is `POST /checkout` — does the bound field
reach the total?

## `Profile`/`Settings`/`Preference` — the nested surface

```
display_name bio avatar theme language
notifications privacy location timezone
role admin is_admin flags
metadata custom extra settings
```

The nested object reachable through `{"profile":{"role":..}}` — the
parent's allowlist covers `profile` as a unit; the merge reaches the
child's fields.

## `Membership`/`Role`/`Group` — the association surface

```
user_id role group_id role_id
permissions scopes access_level
created_by approved expires
```

The join-table model — `{"membership":{"role":..}}` or `user[role_ids]
[]=1` reaching the child's `role` field through the parent's nested-
association accept.

## `Subscription`/`Plan`/`Quota` — the entitlement surface

```
plan_id tier type seats quota
features entitlements rate_limit limits
expires_at lifetime active
```

Bound `plan`/`tier`/`subscription` opening the premium gate.

## `Wallet`/`Balance`/`Credit` — the accounting surface

```
balance credits coins points tokens
currency credit_limit debt payout
available_balance pending_balance
```

Bound `balance`/`credits` reaching the spend — `POST /purchase/flag-
item` with the bound amount.

## `Verification`/`Invite`/`Token` — the state-transition surface

```
verified email_verified_at activated token
expires used code onboarding_complete
activation_token verification_code
```

Bound `verified`/`activated`/`onboarding_complete` skipping the
verification edge.

## `Note`/`Comment`/`Post`/`Review` — the content surface

```
content title body text
author_id user_id created_by
approved moderated flagged
deleted parent_id project_id
```

`author_id` forged = authorship; `approved:true` = moderation-skip;
`parent_id`/`project_id` = scope graft.
