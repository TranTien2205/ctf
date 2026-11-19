# Detection surface — where the writable surface hides

## The model-as-surface

Every model attribute the binder CAN reach is part of the writable
surface — the form's declared fields are a SUBSET. The gap between
"the model has" and "the form sends" is the attack surface.

## The discovery channels

| Channel | Yields | Command |
|---|---|---|
| read-back `GET` | returned keys = candidate fields | `curl $BASE/api/me \| jq 'keys'` |
| bundle | the JS's constructed objects | `bundle_miner --url ... --out ...` |
| errors | the schema's field names | wrong-typed probe → validation error |
| docs | the official model dump | `/openapi.json`, GraphQL `__schema` |
| sibling views | the admin's full field set | `GET /admin/users`, staff API |
| timestamps | `createdAt`, `updatedAt`, `__v` | implicit in every response |

## The hidden-field families

Fields the form never renders but the model carries:

- **privileged**: `role`, `is_admin`, `is_staff`, `permissions`,
  `groups`, `access_level`, `clearance`;
- **state**: `verified`, `is_active`, `approved`, `activated`,
  `onboarding_complete`, `email_verified_at`;
- **economic**: `balance`, `credits`, `price`, `discount`, `total`,
  `currency`, `credit_limit`;
- **plan**: `plan`, `tier`, `subscription`, `quota`, `features`;
- **ownership**: `owner_id`, `author_id`, `created_by`, `tenant_id`,
  `org_id`, `team_id`;
- **workflow**: `status`, `state`, `current_step`, `review_status`,
  `order_status`;
- **internal**: `debug`, `internal_note`, `is_system`, `service_account`,
  `_t`, `__v`, `deleted_at`.

## The nested surface

`profile`, `settings`, `preferences`, `billing`, `address`, `metadata`,
`extra`, `custom` — nested objects whose sub-fields the flat allowlist
can't see. `{"profile":{"role":..}}` reaches `profile.role` the flat
allowlist can't drop (it only covers `profile` as a unit).

## The association surface

`memberships`, `roles`, `groups`, `subscriptions` — CHILD models
reachable through nested-association accepts. `{"membership":{"role":..}}`
or `user[role_ids][]=1` binds the child's fields through the parent's
accepted key.

## The write-only surface

Fields that bind but never serialize: `password_hash`, `internal_note`,
`deleted_at`, `__v`. Invisible in read-backs; provable only by
exercising the decision or by a second representation (admin view).

## The discriminator surface

`_t`, `__t`, `type`, `user_type` — the field selecting WHICH schema
binds. `_t:"AdminUser"` switches to the privileged sub-schema — a
different surface entirely.
