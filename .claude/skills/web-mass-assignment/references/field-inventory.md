# Field inventory — the complete field catalogue by family

## The privilege family

```
role roles user_role userRole role_id role_ids access_role
is_admin isAdmin admin isAdminFlag admin_flag superuser
is_staff isStaff staff moderator is_moderator operator
internal employee developer debug test qa auditor god root
su sysadmin elevated privileged is_poweruser is_sudo
permissions permission scopes scope authorities capabilities
groups group roles[] teams team entitlements rights
access_level accessLevel level tier rank clearance
privilege privileges canAdmin can_admin can_moderate can_edit
can_delete can_publish can_admin type user_type _t __t
account_type user_level userLevel security_level auth_level
domain_admin site_admin org_admin tenant_admin company_admin
team_admin admin_access staff_access internal_access dev_access
membership_type role_name roleName usergroup user_group
grant capability
```

## The verification/state family

```
verified is_verified isVerified email_verified emailVerified
email_verified_at email_confirmed phone_verified sms_verified
activated is_active isActive active enabled approved
is_approved isApproved confirmed is_confirmed pending_review
pendingReview review_required approved_by status state
workflow_state onboarding_complete setup_complete first_login
needs_setup requires_action action_required mfa_enabled
mfaEnabled totp_enabled otp_required passwordless trust_level
trusted known_device skip_verification bypass_2fa
verification_token activation_token email_checked
phone_checked kyc_verified kyc_complete identity_verified
age_verified tos_accepted terms_accepted consent_given
gdpr_consent opted_in subscribed
```

## The economic family

```
balance credits wallet coins points tokens score xp karma
store_credit gift_card_balance reward_points loyalty_points
cashback bonus grant allowance stipend fund bank_balance
net_worth total_credit available_credit spending_limit
daily_limit transaction_limit withdrawal_limit
price unit_price cost amount total subtotal discount
discount_percent coupon promo_code free_shipping freeShipping
price_override lifetime_discount currency tax shipping fee
vat paid is_paid invoice_paid payment_verified salary rate
commission payout credit_limit debt
```

## The plan/entitlement family

```
plan plan_id tier subscription subscription_type
subscriptionTier subscription_plan subscription_tier sub_level
seats quota limits rate_limit api_limit bandwidth_limit
storage_quota feature_flags features entitlements package
level_name pro premium enterprise trial lifetime vip founder
license license_type license_tier billing_plan billing_tier
payment_plan plan_name plan_level tier_level tier_name
member_level membership_level membership_tier user_tier
user_plan access_tier
```

## The ownership/tenancy family

```
owner owner_id ownerId user_id userId account_id accountId
created_by createdBy modified_by modifiedBy author_id authorId
tenant tenant_id tenantId org org_id orgId organization
company company_id department team_id workspace workspaceId
parent_id parentId project_id projectId scope_id group_id
account_owner account_holder record_owner object_owner
resource_owner data_owner primary_owner secondary_owner
co_owner billing_owner technical_owner admin_owner root_org
parent_org owning_org owning_team owning_user owning_account
```

## The workflow/status family

```
status state phase stage step current_step order_status
order_state order_phase order_step payment_status payment_state
payment_phase shipping_status shipping_state delivery_state
fulfillment fulfillment_state review_status review_state
moderation_status moderation_state approval_state flag flags
marked flagged archived deleted is_deleted deleted_at
soft_delete locked frozen suspended banned muted restricted
resolved closed completed shipped correct workflow_step
process_state task_state job_state request_state ticket_state
issue_state case_state
```

## The internals/system family

```
debug verbose dev development test_mode testMode
maintenance_mode dry_run admin_note internal_note
internal_comment is_system isSystem system service_account
serviceAccount bot automation scheduled cron_enabled
password_hash passwordHash salt secret api_key apiKey
token session_id sessionId csrf_token private_key
encryption_key signing_key ip_whitelist whitelist blacklist
admin_access internal_access beta_access early_access
preview_access feature_beta beta_tester insider flagged_internal
is_internal is_dev is_test test_account demo_account
seed_account fixture_account system_user service_user
machine_user api_user
```

## The coverage rule

The dictionary covers SEMANTIC space — privilege, verification,
economics, plan, ownership, workflow, internals. The model answers
the SEMANTIC (a `role` field exists or not); the spellings are
coverage within it. `binding_probe.py`'s default set is the high-
frequency shortlist; the field inventory from `GET`s is the real
source.
