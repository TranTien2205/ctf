# Authz boundaries — vertical, horizontal, and the missing check

The auth boundary is the code path that decides "are you allowed." This
file is the systematic map — where boundaries exist, where they're
missing, and the shapes that leak.

---

## 1. Boundary types

| Type | Question | The missing check |
|---|---|---|
| **vertical** | is this role allowed? | no `role` check on a privileged path |
| **horizontal** | is this user allowed? | no `owner_id == user.id` on a data path |
| **object** | is this specific object allowed? | IDOR — the object's owner isn't checked |
| **field** | is this field allowed to change? | mass-assign — the update takes any key |
| **method** | is this HTTP method allowed? | PUT/DELETE/PATCH without authz |
| **path** | is this URL path allowed? | `/admin/anything` — prefix check misses suffix |
| **context** | is this request context allowed? | internal vs external, referer, origin |
| **time** | is this allowed *now*? | a check that runs before but not after |

## 2. The endpoints table — enumerate every boundary

Enumerate every path the app exposes, then ask for each: does a check
exist, and is it the right kind?

```
GET  /me                  → user-only? (auth required, own data)
GET  /me/{id}             → object check? (auth + owner_id)
PUT  /me                  → field check? (role, is_admin not writable)
POST /login               → no auth (public)
POST /register            → no auth + mass-assign? (role in body)
POST /forgot              → no auth + token-bound?
POST /reset               → token-bound + expiry?
POST /mfa/verify          → pre-mfa state + rate-limit?
GET  /admin               → vertical check
GET  /admin/users         → vertical + object list
GET  /admin/users/{id}    → vertical + object check
PUT  /admin/users/{id}    → vertical + object + field
POST /admin/impersonate   → vertical + impersonation target
GET  /api/v1/me           → auth required
GET  /api/v1/users        → vertical?
GET  /api/v1/users/{id}   → object check?
GET  /api/v1/users/{id}/notes → object check?
POST /api/v1/notes        → auth + write
GET  /api/v1/notes/{id}   → object check
GET  /api/v1/admin/flag   → vertical + flag
GET  /internal/status     → internal-only?
GET  /internal/users      → internal-only?
GET  /.well-known/jwks    → public
GET  /jwks.json           → public
POST /api/v1/graphql      → auth + introspection?
```

## 3. The vertical check shapes

```python
# the right way
if user.role != 'admin': return 403

# the bugs
if user.role != 'admin' and request.method == 'GET': return 403   # POST skips
if user.role != 'admin': pass                                     # no-op
if user.role not in ['admin','staff']: return 403                  # partial allowlist
if user.is_admin: pass else: return 403                            # inverted
if 'admin' not in user.role: return 403                           # substring
if user.role.startswith('adm'): return 403                        # substring
if user.role in ['admin']: pass                                    # forgot return
# the check exists but is bypassable
if user.role == 'admin' or request.headers.get('X-Internal'): return 403
```

## 4. The horizontal check shapes

```python
# right
if note.user_id != request.user.id: return 404  # 404 not 403 — don't leak existence
# wrong
if note.user_id == int(request.user.id): return note   # cast mismatch
if note.user_id == str(request.user.id): return note   # type coercion
return Note.get(id)  # no owner check
```

## 5. The object check shapes

```python
# per-object
note = Note.get(id)
if note.user_id != request.user.id: return 404

# the bugs
note = Note.get(id); return note  # no check
if note.user_id == request.user.id or user.is_admin: return note  # admin OR is right
if note.user_id != request.user.id and user.role != 'admin': return 404  # skipped for admin
note = Note.get(id, owner_id=request.user.id)  # query is the check — fine
note = Note.get(id); note.can_view(request.user)  # method on object — check it
```

## 6. The field (mass-assign) check

```python
# right
allowed = {'display_name', 'bio', 'theme'}
user.update({k:v for k,v in body.items() if k in allowed})

# bugs
user.update(body)                                   # everything
user.update(body); user.save()                      # same
for k,v in body.items(): setattr(user, k, v)        # explicit
for k,v in body.items(): user[k] = v                # dict-style
Object.assign(user, body)                           # JS
user._fields.update(body)                           # SQLAlchemy internal
user.__dict__.update(body)                          # bypasses setters
db.execute(f"UPDATE users SET {k}={v}")            # injection
db.users.update(user.id, body)                      # orm raw
```

## 7. The method check

```python
@app.route('/admin', methods=['GET','POST'])
def admin():
    if request.method == 'GET' and not is_admin(): return 403
    # POST not checked!
```

```javascript
app.use('/admin', auth);          // all methods
app.get('/admin', auth, handler); // only GET
app.post('/admin', handler);      // POST skips the middleware!
```

## 8. The path check

```python
if request.path.startswith('/admin'): require_admin()
# /administrator — passes? no, doesn't start with /admin (good)
# /ADMIN — case-insensitive path, check is case-sensitive (bug)
# /admin/../admin — normalizes to /admin (good if normalized before check)
# /admin%2fusers — encoded, check happens pre-decode (bug if proxy decodes)
# //admin/users — double slash — normalization
# /admin;users — path parameter
# /admin.json — extension suffix
# /admin/users.json — same
# /admin/users/ — trailing slash
# /admin/users? — query separator
# /admin/users# — fragment
# /admin\users — backslash (Windows)
# /admin\\users — double backslash
# /admin%5cusers — encoded backslash
# /admin/users?id=1 — the path doesn't include query
# /admin/users%00 — null byte truncation
# /admin/users%20 — trailing space
# /admin/users%09 — tab
# /admin/users%0a — newline
# /admin/users%0d — CR
```

## 9. The context check

- `X-Forwarded-For: 127.0.0.1` — trust the header for an internal route
- `X-Forwarded-Host: internal.tld` — same
- `Referer: https://internal.tld/` — internal-only route
- `Origin: https://internal.tld` — same
- `Host: internal.tld` — internal-only route
- `X-Real-IP`, `X-Client-IP`, `X-Remote-Addr` — IP spoof
- `CF-Connecting-IP`, `True-Client-IP` — CDN-provided IP
- `Forwarded: for=127.0.0.1` — RFC 7239

## 10. The time check — TOCTOU

- Read `user.role` at T, write at T+Δ — the role changed between.
- Check `note.user_id` at T, `note.update` at T+Δ — ownership changed.
- Check `token.exp` at T, accept at T+Δ — the exp passed between.
- Check `code.attempts < 3` at T, `code.attempts++` at T+Δ — race the
  counter.

## 11. The "the boundary doesn't exist" list

The worst bugs are the endpoints that should have a check and don't:

- `/internal/users` — the path implies internal but no check.
- `/api/v2/admin` — v2 forgotten while v1 has auth.
- `/graphql` — auth enforced on REST but not GraphQL.
- `/ws` — auth on HTTP but not WebSocket.
- `/metrics` `/health` `/debug` — operational endpoints public.
- `/.well-known/` paths — `jwks.json` should be public, but
  `/.well-known/openid-configuration` may leak `issuer`/`token_endpoint`.
- `/_debug/` `/__debug__/` `/console` — dev tools left enabled.

## 12. Falsifiers

- `403` with `WWW-Authenticate` — auth required, not a boundary bug.
- `404` on the endpoint — doesn't exist.
- The check runs but returns a different error shape — the check exists.
- `200` with `{"error":"not_admin"}` — the check exists and rejected.
- `200` with only public fields — the check filtered, not bypassed.
