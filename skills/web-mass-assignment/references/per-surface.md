# Per-surface — the writable surface by model type

## The `User`/`Account` model

Fields: `username`, `password`, `email`, `display_name`, `bio`,
`avatar`, `role`, `is_admin`, `is_staff`, `permissions`, `groups`,
`verified`, `is_active`, `balance`, `plan`, `tier`, `tenant_id`,
`org_id`, `team_id`, `debug`, `internal`, `_t`, `__v`, `created_at`,
`updated_at`, `deleted_at`.

The widest surface — every privileged semantic lives here. `PATCH`/
`PUT` on `me`/`id` is the primary endpoint.

## The `Order`/`Purchase`/`Transaction` model

Fields: `item_id`, `product`, `quantity`, `price`, `unit_price`,
`discount`, `coupon`, `total`, `subtotal`, `shipping`, `tax`,
`currency`, `status`, `payment_status`, `order_status`, `fulfillment`,
`paid`, `is_paid`, `invoice_paid`.

The economic surface — bound `price`/`total`/`discount` reaching the
checkout totals.

## The `Profile`/`Settings`/`Preference` model

Fields: `display_name`, `bio`, `avatar`, `theme`, `language`,
`notifications`, `privacy`, `role` (sometimes nested), `admin`,
`flags`, `metadata`, `custom`.

The nested surface — `{"profile":{"role":..}}` reaching the child
model's fields.

## The `Membership`/`Role`/`Group` model

Fields: `user_id`, `role`, `group_id`, `permissions`, `scopes`,
`access_level`, `created_by`, `approved`, `expires`.

The association surface — `{"membership":{"role":..}}` or
`user[role_ids][]=1` reaching the join table.

## The `Subscription`/`Plan`/`Quota` model

Fields: `plan_id`, `tier`, `type`, `seats`, `quota`, `features`,
`entitlements`, `rate_limit`, `expires_at`, `lifetime`.

The entitlement surface — bound `plan`/`tier` opening the premium gate.

## The `Wallet`/`Balance`/`Credit` model

Fields: `balance`, `credits`, `coins`, `points`, `tokens`, `currency`,
`credit_limit`, `debt`, `payout`.

The accounting surface — bound `balance`/`credits` reaching the spend.

## The `Verification`/`Invite`/`Token` model

Fields: `verified`, `email_verified_at`, `activated`, `token`,
`expires`, `used`, `code`, `onboarding_complete`.

The state-transition surface — bound `verified`/`activated` skipping
the workflow edge.

## The `Note`/`Comment`/`Post`/`Review` model

Fields: `content`, `title`, `author_id`, `user_id`, `approved`,
`moderated`, `flagged`, `deleted`, `parent_id`, `project_id`.

The content surface — `author_id` forged = authorship; `approved:true`
= moderation-skip.
