# Field map — field name → semantic → gate → carrier, the four-column table

## Privilege fields

| Field | Semantic | Gate | Carriers |
|---|---|---|---|
| `role` | privilege | `/admin` | flat, nested, `user[role]`, `roles[]`, `role:1` |
| `is_admin` | privilege | `/admin` | flat, `isAdmin`, `role` variants |
| `is_staff` | privilege | `/staff`, Django admin | flat |
| `permissions` | privilege | scope checks | `["*"]`, `[{"all":true}]` |
| `groups` | privilege | group checks | `["admin"]`, `[{"id":1}]` |
| `access_level` | privilege | numeric gates | `9`, `"admin"` |
| `clearance` | privilege | clearance gates | `"top"`, `9` |
| `_t`/`type`/`user_type` | privilege | sub-schema | `"AdminUser"`, `"admin"` |
| `admin`/`superuser` | privilege | bool checks | `true`, `1` |
| `internal`/`debug` | privilege | operator paths | `true`, `1` |

## Verification fields

| Field | Semantic | Gate | Carriers |
|---|---|---|---|
| `verified` | state | `/flag`, `/verified` | `true`, `1`, `"yes"` |
| `is_active` | state | `/restricted` | `true`, `1` |
| `approved` | state | `/pending` | `true`, `1` |
| `activated` | state | `/onboarding` | `true`, `1` |
| `email_verified_at` | state | `/verified-users` | timestamp |
| `mfa_enabled` | state | MFA gate | `false` |
| `onboarding_complete` | state | onboarding | `true` |
| `status` | state | status checks | `"active"`, `"approved"` |

## Economic fields

| Field | Semantic | Gate | Carriers |
|---|---|---|---|
| `price` | economic | checkout totals | `0`, `0.01`, `-1` |
| `total`/`subtotal` | economic | totals | `0`, `0.01` |
| `discount` | economic | totals | `100`, `99999` |
| `balance`/`credits` | economic | purchase | `99999`, `1e6` |
| `currency` | economic | totals | `"AAA"` |
| `paid`/`is_paid` | economic | paid check | `true` |
| `quantity` | economic | totals | `-1`, `9999` |

## Plan fields

| Field | Semantic | Gate | Carriers |
|---|---|---|---|
| `plan` | entitlement | `/premium` | `"enterprise"`, `5` |
| `tier` | entitlement | `/premium` | `"pro"`, `9` |
| `subscription` | entitlement | `/lifetime` | `{"type":"lifetime"}` |
| `features` | entitlement | feature flags | `["premium"]` |
| `seats`/`quota` | entitlement | limit checks | `999`, `-1` |
| `pro`/`vip`/`lifetime` | entitlement | boolean | `true` |

## Ownership fields

| Field | Semantic | Gate | Carriers |
|---|---|---|---|
| `author_id`/`owner_id` | ownership | authorship | `1`, `<other-id>` |
| `tenant_id`/`org_id` | ownership | scoping | `1` |
| `created_by` | ownership | authorship | `1` |
| `team_id`/`project_id` | ownership | scoping | `1` |

## Workflow fields

| Field | Semantic | Gate | Carriers |
|---|---|---|---|
| `status`/`state` | workflow | state machines | `"shipped"`, `"done"` |
| `current_step` | workflow | step gates | `99` |
| `review_status` | workflow | review | `"approved"` |
| `order_status` | workflow | order state | `"shipped"` |
| `correct` | workflow | submissions | `true` |

## The map's use

Pick the SEMANTIC the challenge gates on (the flag sits behind `/admin`
= privilege, `/verified-only` = verification, `/checkout` = economics),
then pick the FIELD the gate reads (from the model or the gate's
source), then the CARRIER the binder accepts. The four columns are
the exploit's coordinates.
