# Framework notes — where each stack puts the check (and where it forgets)

Per-framework: the idiomatic place authorization lives, the idiomatic
place it goes missing, and the probes that fit the stack.

---

## Rails

**Where the check lives.** `before_action :set_item` +
`current_user.items.find(params[:id])`, or CanCanCan `load_and_
authorize_resource`, or Pundit `authorize @item`.

**Where it's missing.** Actions added without `before_action` —
custom member/collection routes (`get :export, on: :member`) are
declared in `routes.rb` and frequently skip the filter chain that
`:show` carries.

**Probes.**

```
GET /items/1/export     /items/1/duplicate    /items/1/share
GET /items/1.json       (format suffix → different render path)
PATCH /items/1 {"item":{"user_id":1}}   — strong-params vs mass-assign
?with_deleted=true      — paranoia/discard soft-delete scope
_items?_=  ..._method=delete_   — method override param
```

Strong-params bypass: `item[user_id]` nested under the permitted key
vs flat `user_id` — Rails permits the nested form when `params.require
(:item).permit(...)` whitelists by shape, and the flat field is
dropped silently. Watch for `permit!` and `to_unsafe_h` in source.

## Django

**Where the check lives.** `LoginRequiredMixin` + `get_queryset()`
scoped to `request.user`, or `@permission_required`, or
`request.user == obj.owner` in the view.

**Where it's missing.** Function views without the decorator (a lone
`def item_export(request, id)`), CBVs that override `get()` but not
`get_queryset()`, DRF views where `permission_classes` is set but
`get_object()` calls the unscoped `Model.objects.get(pk=...)`.

**Probes.**

```
GET /items/1/export/    /items/1/download/    /items/1/raw/
GET /api/items/1/?format=json    — DRF format suffix
PATCH /api/items/1/ {"owner": 1}  — writable FK serializer field
GET /admin/app/item/1/change/     — the auto-admin, if exposed
?__debug_toolbar__=1              — djdt panels leak queries
```

DRF specifically: `serializer.save(owner=request.user)` protects
create; a serializer with `owner = PrimaryKeyRelatedField
(queryset=User.objects.all())` makes the field writable — a
`{"owner": 1}` PATCH reassigns the object.

## Laravel / PHP

**Where the check lives.** Policy methods (`$this->authorize
('view', $item)`), `Gate::allows`, scoped route model binding
(`Route::get('/{user:slug}/...')`), or `Auth::id() ==
$item->user_id`.

**Where it's missing.** Implicit route-model binding
(`Item $item` resolves by id before any policy runs — the 404 vs 403
split is your oracle), controllers where `__construct` calls
`$this->middleware('can:view,item')` only on some actions.

**Probes.**

```
GET /items/1          → 404 vs 403 tells you binding resolved
GET /items/1/edit     → edit form leaks the full object in the HTML
GET /api/items?withTrashed=1     — SoftDeletes trait
POST /items/1 {"_method":"PUT"}  — Laravel method spoofing
POST /items {"user_id":1}        — $fillable vs $guarded=[] gap
```

`$guarded = []` (everything fillable) in source = mass-assignment by
design. The `user()` relationship key names (`user_id`, `owner_id`,
`author_id`, `created_by`) are the assignment corpus.

## Express / Node

**Where the check lives.** Middleware (`app.get('/items/:id',
requireAuth, checkOwner, handler)`) or inline `if (item.userId !==
req.user.id)`.

**Where it's missing.** Routes mounted without the middleware chain
(`router.get` vs `app.get` with different stacks), async handlers
where the check `await`s in the wrong order, `param('id')` coercion
differences (`==` vs `===`).

**Probes.**

```
GET /items/1           /items/1/    /items//1   (router strictness)
GET /items/1.json      (res.format branches)
{"user_id": 1} in body            — merge patterns (lodash merge,
                                    Object.assign(res.body, ...))
__proto__ / constructor keys      — merge → prototype pollution path
?id=1&id=2                        — qs duplicate → array
```

`Object.assign(item, req.body)` is the mass-assignment idiom — any
key in the body lands on the model. Pair with `user_id`, `role`,
`isAdmin`, `__proto__.isAdmin` (see `skills/web-prototype-pollution/`).

## Spring / Java

**Where the check lives.** `@PreAuthorize("hasRole('X')")`,
`@PostFilter`, `SecurityContextHolder`, or `item.getOwner().equals
(currentUser)`.

**Where it's missing.** SpEL expressions evaluated once at method
level while the repo call inside is unscoped
(`itemRepository.findById(id)`), or `@PostFilter` applied to a
collection that already leaked single-object reads.

**Probes.**

```
GET /items/1          /items/1.do   /items/1.action  (servlet suffixes)
GET /items/1;jsessionid=...       (path params pass through)
GET /items/1?trace                — Spring Boot Actuator leaks
GET /actuator/mappings            — the whole route table, if exposed
{"id":1,"owner":{"id":1}}         — nested entity binding
```

Actuator is the recon multiplier — `/actuator/mappings` lists every
route including the unguarded export/admin ones.

## Flask / Python

**Where the check lives.** `@login_required` + `Item.query.filter_by
(id=id, user_id=g.user.id).first_or_404()`.

**Where it's missing.** Blueprints registered without the decorator,
`request.view_args` vs `request.args` confusion (path id checked,
query id used), `get_or_404` without the owner filter.

**Probes.**

```
GET /items/1?user_id=1            — arg used over path
GET /items/<int:id> vs <id>       — int converter 404s non-ints,
                                    string route accepts anything
GET /items/1%20/ /items/%2e/1/    — Werkzeug normalization
{"owner_id":1} in JSON PATCH      — schema-less update
```

`first_or_404` vs `one()`: a `404` on a foreign id can't be told from
a nonexistent object without the own-id control — see
`verification-surfaces.md`.

## FastAPI

**Where the check lives.** `Depends(get_current_user)` +
`item.owner_id == user.id` in the path operation.

**Where it's missing.** Extra routes added to the router after the
dependency-wired ones; `response_model` filtering hides fields but
the DB query already ran unscoped (leak via `?fields=` or error
echo).

## .NET / ASP.NET

**Where it lives.** `[Authorize]` + `User.FindFirst("sub")` compared
to `item.OwnerId`, or resource-based `IAuthorizationService`.

**Where it's missing.** `[AllowAnonymous]` on a sibling action in an
`[Authorize]` controller; minimal-API endpoints where the auth filter
was only added to the route group; `FromBody` binding of an
`OwnerId` property on the DTO.

## The cross-framework constant

Every stack's gap is the same shape: the check exists on the idiomatic
path (show, update) and is absent from the non-idiomatic one the author
added later (export, duplicate, preview, share, transfer, raw, print,
download, admin-compat). Enumerate the non-idiomatic verbs first —
`function-level.md` has the verb corpus.
