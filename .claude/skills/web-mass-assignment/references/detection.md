# Detection — finding the mass-assignment surface before any probe

Detection is two questions: WHERE do bodies bind into models (the
endpoint list), and WHICH fields exist beyond the form (the field
inventory). Both are read-only work — cheap, offline, before a single
write.

## Step 1 — the endpoint inventory

Any endpoint that accepts a body and mutates a model:

```bash
python3 tools/web/bundle_miner.py --url <bundle-url> --out /tmp/bundle
# /tmp/bundle endpoints + reconstructed sources
```

Sort by method:

- `POST /register`, `/signup`, `/users` — create binders;
- `PATCH`/`PUT` on `/users/:id`, `/profile`, `/me`, `/settings` —
  update binders (often a SECOND, wider binder than create);
- `POST` on `/orders`, `/checkout`, `/cart`, `/billing` — domain
  objects with economic fields;
- `/import`, `/seed`, `/bulk`, `/migrate` — bulk binders;
- GraphQL mutations — `createUser`, `updateUser`, `updateProfile` args;
- admin paths — `/admin/users` POST/PUT (needs a privilege edge first).

## Step 2 — the field inventory

The model's real field list, from five sources in order:

1. **Read-back responses** — `GET /api/me`, order detail, profile GET.
   Every returned key is a candidate writable key. `role`, `balance`,
   `verified`, `permissions`, `plan`, `status`, `flags`, `price` are
   the privileged semantics; ANY key not on the form is a probe.
2. **The bundle** — `bundle_miner` output + grep the reconstructed
   sources for `role|admin|is_staff|isAdmin|balance|price|discount|
   approved|verified|status|plan|credits|permissions|group|flags`.
   The JS often builds the full object (`{username, role, plan}`) that
   the rendered form only partially sends.
3. **Error messages** — send a wrong-typed value on a known field;
   validation errors frequently list the whole schema
   (`"role must be one of: user, admin"`, `"unknown property: x,
    expected: username, password, role, ..."`).
4. **Docs/schema** — `/api/docs`, `/openapi.json`, `/swagger.json`,
   GraphQL introspection (`{__schema{types{fields{name}}}}`) — the
   model spelled out officially.
5. **Sibling endpoints** — the admin update form or a staff API renders
   the complete field set the public form hides.

## Step 3 — the binder fingerprint

Which binder family is running decides the probe grammar:

| Signal | Binder family | Grammar |
|---|---|---|
| Express stack, `X-Powered-By` | merge-all or Mongoose strict | flat + nested JSON |
| Rails (`X-Runtime`, `user[...]` params) | strong params | `user[role]=admin` |
| Laravel (`laravel_session`) | `$fillable`/`$guarded` | flat + `role[]=admin` |
| Django (csrftoken, `__admin`) | ModelForm vs `create(**data)` | flat; API vs form path |
| Spring (`JSESSIONID`) | bean binding incl. all setters | flat + nested props |
| ASP.NET | model binding / `[Bind]` | flat + `User.Role` case |
| Go/`interface{}` | unmarshal into declared struct | tagged fields only |

The error shape confirms: `TypeError: unexpected keyword` = kwargs
binder; `"unknown property"` = strict schema; silent `200` + drop =
allowlist.

## Step 4 — the probe order

```
1. control POST (the documented body, verbatim)      → baseline
2. POST + privileged field (role=admin)              → write echo
3. GET the object (read-back, DIFFERENT endpoint)    → store truth
4. exercise the field (the gated route/the total)    → decision change
```

`binding_probe.py` automates steps 2–3:

```bash
python3 tools/web/binding_probe.py \
  --url "$BASE/api/register" --body 'username=p&password=x' \
  --readback "$BASE/api/me" --selftest
```

The tool sends the default field set (`role`, `admin`, `is_admin`,
`isAdmin`, `debug`, `permissions`, `group`, `verified`, `is_staff`) with
a canary value, grades echo vs landed, and reports which fields reached
the store. `--fields` overrides the set; `--method GET` tests query
carriers.

## Detection anti-signals

- `GET /api/me` returns only `username`, `id`, `created` — a narrow
  serializer may hide stored fields; check whether admin/sibling views
  show more before concluding the model is narrow.
- `POST` 400s on the control body → the endpoint itself is broken or
  the body shape is wrong — fix the baseline before probing.
- All read-backs identical → cache: add a cache-buster or read a second
  representation (detail page vs API).
