# Field dictionary — the candidate field names, by semantic

The binder binds what the request sends — the question is which field
names the model carries. This dictionary groups candidate names by the
decision they would change. Every name is worth exactly ONE probe; a
model that answers `role` answers its semantics, not its spellings —
but a strict-typed model may expose `isAdmin` while ignoring `role`.

## Privilege / authorization

```
role roles user_role userRole role_id access_role
isAdmin is_admin admin isAdminFlag admin_flag superuser
isStaff is_staff staff moderator is_moderator operator
internal employee developer debug test qa auditor
permissions permission permissions[] scopes scope
groups group groups[] teams team roles[] authorities
accessLevel access_level level tier rank clearance
privilege privileges rights entitlements capabilities
canAdmin can_admin is_poweruser is_sudo su god root
```

## Verification / approval state

```
verified isVerified is_verified email_verified emailVerified
phone_verified activated is_active isActive active enabled
approved is_approved isApproved confirmed is_confirmed
pending_review pendingReview review_required approved_by
status state workflow_state onboarding_complete
mfa_enabled mfaEnabled totp_enabled otp_required
passwordless trust_level trusted known_device
```

## Economic / accounting

```
balance credits wallet coins points tokens score xp karma
price cost amount total subtotal discount coupon
free_shipping freeShipping lifetime_discount price_override
salary rate commission payout credit_limit debt
invoice_paid paid is_paid payment_verified
```

## Plan / entitlement

```
plan plan_id tier subscription subscription_type
subscriptionTier seat seats quota limits rate_limit
api_limit bandwidth_limit storage_quota feature_flags
features entitlements package level_name
pro premium enterprise trial lifetime vip founder
```

## Ownership / tenancy

```
owner owner_id ownerId user_id userId account_id accountId
created_by createdBy modified_by modifiedBy author_id authorId
tenant tenant_id tenantId org org_id orgId organization
company company_id department team_id workspace workspaceId
parent_id parentId project_id projectId scope_id
```

## Workflow / status

```
status state phase stage step current_step
order_status payment_status shipping_status fulfillment
review_status moderation_status flag flags marked
archived deleted is_deleted deleted_at soft_delete
locked frozen suspended banned muted restricted
```

## Security internals

```
password_hash passwordHash salt secret api_key apiKey
token session_id sessionId csrf_token private_key
encryption_key signing_key internal_note admin_note
ip_whitelist whitelist blacklist bypass_2fa skip_verification
```

## System / debug

```
debug verbose dev development test_mode testMode
maintenance_mode dry_run admin_note internal_comment
is_system isSystem system service_account serviceAccount
bot automation scheduled cron_enabled
```

## Spelling conventions to try per family

| Convention | Variants for "admin role" |
|---|---|
| camelCase | `isAdmin`, `userRole`, `accessLevel` |
| snake_case | `is_admin`, `user_role`, `access_level` |
| kebab | `is-admin` (headers/query) |
| prefixed model | `user[role]`, `user.role`, `userRole` |
| case-only | `Role`, `ROLE`, `IsAdmin`, `IS_ADMIN` |
| plural | `roles`, `permissions`, `groups` |

The model answers semantics — a `role` field exists or not. But strict
typed binders bind `isAdmin` where they ignore `role`, so the
dictionary's point is coverage of the SEMANTIC space (privilege,
verification, economics, plan, ownership, workflow, internals) not
spelling exhaustion.
