# Decision map — which field gates which decision

## The privilege fields → the privilege gates

| Bound field | The gate | The decision |
|---|---|---|
| `role:"admin"` | `GET /admin`, `POST /admin/*` | role == admin |
| `is_admin:true` | same | is_admin truthy |
| `is_staff:true` | `/staff/*`, Django admin | is_staff |
| `permissions:["*"]` | `POST /admin/users`, scope checks | permission in list |
| `groups:[{"id":1}]` | group-membership checks | group contains |
| `access_level:9` | numeric gates | level >= threshold |
| `_t:"AdminUser"` | the privileged sub-schema | schema variant |

## The verification fields → the state gates

| Bound field | The gate | The decision |
|---|---|---|
| `verified:true` | `/flag`, `/verified-only`, `/vault` | verified |
| `is_active:true` | login, `/restricted` | is_active |
| `approved:true` | `/pending-content` | approved |
| `activated:true` | `/onboarding-complete` | activated |
| `email_verified_at` | `/verified-users` | timestamp set |
| `mfa_enabled:false` | the MFA gate | disabled |
| `onboarding_complete:true` | the onboarding gate | complete |

## The economic fields → the totals gates

| Bound field | The gate | The decision |
|---|---|---|
| `price:0` | `POST /checkout` total | totals() reads price |
| `total:0` | same | totals() reads total |
| `discount:100` | same | totals() reads discount |
| `balance:99999` | `POST /purchase/flag-item` | balance >= price |
| `credits:99999` | same | credits suffice |
| `currency:"AAA"` | totals() currency | the denomination |
| `paid:true` | `GET /orders/:id` paid | paid flag |
| `quantity:-1` | totals() math | negative quantity |

## The plan fields → the entitlement gates

| Bound field | The gate | The decision |
|---|---|---|
| `plan:"enterprise"` | `GET /premium`, `/enterprise` | plan == tier |
| `tier:"pro"` | same | tier check |
| `subscription:{type:"lifetime"}` | `/lifetime-features` | subscription type |
| `features:["premium"]` | feature-flag checks | feature in list |
| `seats:999` | seat-limit checks | seats >= n |
| `pro:true`/`vip:true` | `/vip`, `/pro` | boolean flag |

## The ownership fields → the access gates

| Bound field | The gate | The decision |
|---|---|---|
| `author_id:1` | `GET /notes` authorship | author_id == viewer |
| `owner_id:1` | `GET /items` ownership | owner_id match |
| `tenant_id:1` | `GET /tenant/*` scoping | tenant_id match |
| `org_id:1` | `GET /org/*` scoping | org_id match |
| `created_by:1` | `GET /created` authorship | created_by match |

## The workflow fields → the state gates

| Bound field | The gate | The decision |
|---|---|---|
| `status:"shipped"` | `GET /orders/:id` state | status check |
| `state:"done"` | `GET /tasks/:id` | state check |
| `current_step:99` | the step gate | step >= required |
| `review_status:"approved"` | `/pending-review` | review approved |
| `correct:true` | `/flag-submissions` | the bound answer |

## The internals fields → the operator gates

| Bound field | The gate | The decision |
|---|---|---|
| `debug:true` | `/debug`, verbose errors | debug enabled |
| `is_system:true` | `/system/*` | system account |
| `service_account:true` | `/api/service/*` | service flag |
| `internal:true` | `/internal/*` | internal flag |
| `admin_note:"x"` | the admin view's note | displayed to admins |
