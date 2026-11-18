# Multi-tenant IDOR — the boundary between organizations

A tenant is an ownership boundary above the user. Tenant IDOR is the
commonest real-world shape: the check enforces `user.id == session.user`
or `object.user_id == session.user_id`, but the object actually belongs
to `object.tenant_id == session.tenant_id` — and the tenant check is
missing, partial, or applied to a different field than the request
carries.

---

## 1. The three tenant models

| Model | Object belongs to | The classic gap |
|---|---|---|
| user-scoped | `object.user_id` | user check present, but `?tenant_id=` switches which tenant's users are visible |
| tenant-scoped | `object.tenant_id` | tenant check on reads, missing on writes — or the reverse |
| org-tree | `object.org_id` rolled up into a hierarchy | check tests `org_id == mine`, child orgs' objects readable |

Name the model first — it decides which field to attack.

## 2. The signals that say "tenant-scoped"

In requests:

```
X-Tenant-Id: 7            tenant: 7            ?tenant_id=7
org: acme                 team: 3              workspace: ws_123
{"tenant":"acme"}         {"tenant_id":7}      {"organization_id": 7}
sub claim = "t7:u42"      aud claim = "tenant:7"
Host: acme.app.example    # tenant resolved from subdomain
Host: app.example with X-Tenant-Slug: acme
```

In responses:

```json
{"id": 1001, "tenant_id": 7, "owner": {"org": 7}}
{"_links": {"tenant": "/tenants/7"}}
{"meta": {"org": "acme", "workspace": 3}}
```

Any of these in a response means the object carries a tenant key the
check may or may not compare against the caller's tenant.

## 3. The bypass shapes

**Subdomain vs id mismatch.** `acme.app.example` resolves tenant `acme`
from the Host; the API also accepts `?tenant_id=7`. If the two disagree
— Host says `acme`, param says `7` — and the handler trusts the param,
tenant 7's objects are readable through `acme`'s hostname.

```bash
curl -b acme.cookies "https://acme.app.example/api/items?tenant_id=7"
```

Falsifier: the handler resolves the tenant from one authoritative
source (usually the Host-derived context) and ignores the param.

**Cross-tenant id in a composite path.** `/tenants/7/users/42` — the
check may verify `user 42` exists but not that `user 42 ∈ tenant 7`.
Swapping the path tenant while keeping the leaf id reads the same
object under a different tenant context:

```
GET /tenants/7/users/42    → 403 (not my tenant, denied correctly?)
GET /tenants/1/users/42    → 200 (my tenant id + foreign user id)
```

If `/tenants/1/users/42` returns user 42's data — user 42 belonging to
tenant 7 — the leaf check is missing. If it returns "user 42 not in
tenant 1", the composite check exists and the vector is closed.

**Slug-vs-id confusion.** The API accepts `/orgs/acme` and `/orgs/7`
for the same tenant. The ACL map may be keyed on one form only:
`/orgs/acme/members` denies, `/orgs/7/members` allows.

**Invitation / membership pivot.** `POST /orgs/7/invite` with a victim
email, or `POST /orgs/7/members {"user_id": <my-id>}` — a membership
write missing the tenant-admin check turns into full tenant read
access once joined.

**Default-tenant fallback.** `?tenant_id=0`, `tenant_id=null`,
`tenant_id=` absent — some handlers fall back to "no filter" rather
than "deny", returning every tenant's rows. See
`collection-filters.md`.

## 4. The read/write asymmetry

The most common partial check: tenant scoping on `SELECT` but not on
`UPDATE`/`DELETE`, or the reverse. Map all four verbs per object:

```
GET    /tenants/7/invoices/1001   → ?
POST   /tenants/7/invoices        → ?
PATCH  /tenants/7/invoices/1001   → ?
DELETE /tenants/7/invoices/1001   → ?
```

A check written as middleware on `GET` routes frequently misses
`PATCH`/`DELETE` registered under a different router or with
method-conditional middleware (`if method == "GET": require_tenant()`).

## 5. Nested-tenant objects

Objects that reference two tenants (a shared document, a cross-org
project) are where checks rot:

```json
{"doc": 42, "owner_tenant": 7, "shared_with": [1, 3]}
```

Reading `/docs/42` as tenant 1 member is legitimate. Updating it may
need `owner_tenant` — or the check may compare against `shared_with`
and let a viewer write. Probe the write verbs on shared objects.

## 6. Evidence

A cross-tenant read is proven only when the response contains a field
that could not be public: another org's internal note, a private
invoice total, a member list including emails. Record:

- the request (tenant A session, tenant B object id),
- the verbatim excerpt carrying the foreign tenant's marker
  (`"tenant_id": 7` while session tenant is 1),
- the negative control: same request without the foreign id, or with
  a tenant id that does not exist, to rule out a "everything public"
  baseline.

## 7. Budget rule

Tenant probes multiply fast: tenants × verbs × carriers. Bound it —
one foreign tenant (yours, if the app lets you create a second org),
three verbs (GET, PATCH, DELETE), two carriers (path, body). If all
six deny consistently, the tenant check is real; record it and switch
layer (second-order, mass-assignment, or a different object type).
