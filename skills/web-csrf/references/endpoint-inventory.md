# Endpoint inventory — finding the state-changing surface

Before measuring gates, enumerate every endpoint that changes state.
The CSRF candidate is any write a browser can reach.

---

## 1. The HTTP-method inventory

```bash
# every state-changing route in source
grep -rnoE '@(app|route)\.(post|put|patch|delete)|app\.(post|put|patch|delete)|router\.(post|put|patch|delete)|@(Post|Put|Patch|Delete)Mapping|Route::(post|put|patch|delete)|methods=\[' \
  <src> | head -60

# the GET-with-side-effect — the Lax-open case
grep -rnoE '@(app|route)\.get|app\.get|router\.get|@GetMapping|Route::get|def get_|function.*\(.*\).*\{[^}]*delete|update|create' \
  <src> | head -40
```

The GET-write is the one SameSite=Lax doesn't protect — a delete-
link, a transfer-GET, an admin-action-by-GET.

## 2. The write-semantics inventory — which endpoints change state

| Verb in the route | The write |
|---|---|
| `change`/`update`/`edit`/`modify` | a field update |
| `transfer`/`send`/`pay`/`withdraw` | an asset move |
| `delete`/`remove`/`destroy` | a deletion |
| `create`/`add`/`new`/`register` | a creation |
| `set`/`config`/`setting` | a config change |
| `role`/`grant`/`admin`/`permission` | a privilege change |
| `login`/`logout`/`password`/`email` | a credential change |
| `approve`/`accept`/`confirm` | a state transition |
| `assign`/`submit`/`flag` | the flag-path write |

## 3. The grep-corpus for the write surface

```bash
# route definitions
grep -rnoE '(route|@app|@route|app\.|router\.|Route::|@.*Mapping|path\(|url\()' <src> \
  --include='*.py' --include='*.js' --include='*.ts' --include='*.rb' \
  --include='*.php' --include='*.java' --include='*.go' | head -80

# the front-end's own calls — what the UI invokes
grep -rnoE "fetch\(['\"][^'\"]+|axios\.(get|post|put|delete)\(['\"][^'\"]+|\.ajax|\.post\(|\.put\(" \
  <src> --include='*.js' | head -40

# form actions in templates
grep -rnoE '<form[^>]*action=[^ >]+|<form[^>]*method=[^ >]+' \
  <src> --include='*.html' --include='*.jinja*' --include='*.ejs' \
  --include='*.erb' --include='*.blade*' | head -40
```

## 4. The hidden/internal endpoint — the bot-reachable surface

```bash
# localhost/internal routes the bot can hit
grep -rnoE '127\.0\.0\.1|localhost|internal|admin|private|0\.0\.0\.0|remote_ip|RemoteAddr|ClientIP' \
  <src> | head -30

# the docker-compose internal names — what the bot resolves
grep -rnoE 'http://[a-z_-]+(:[0-9]+)?|hostname:|container_name:|services:' \
  <src> --include='*.yml' --include='*.yaml' --include='Dockerfile*' | head -30
```

The `127.0.0.1`-gated write is unreachable to you but reachable to
the bot's browser — the TornadoService shape.

## 5. The flag-path endpoint — the write that matters

```bash
# where does the flag live / move?
grep -rnoiE 'flag|secret|admin|prize|reward' <src> | head -30
```

The CSRF candidate is the write that touches the flag's path —
the admin-action, the flag-read, the assignment-submit, the
transfer of the flag-object.

## 6. The endpoint→write matrix

| Endpoint | Write | CSRF surface |
|---|---|---|
| `POST /change-email` | email swap | urlencoded form → account takeover |
| `POST /transfer` | asset move | urlencoded → exfil to your account |
| `GET /delete?id=` | deletion | top-nav GET → Lax-safe |
| `POST /update` (JSON) | config/object | text/plain JSON → foothold |
| `POST /login` | credential | credential-plant → session swap |
| `POST /admin/role` | privilege | needs the bot's/admin's session |
| `POST /upload` (multipart) | file | multipart form → file-write |
| `POST /submit-flag` | flag-submit | the flag-path write |
| `POST /update_tornado` (localhost) | a gated write | the bot-as-localhost shape |

## 7. The "which write is the prize" ranking

```text
rank by proximity to the flag:
1. a write that moves/reads the flag directly
2. a write that grants privilege reaching the flag
3. a write that swaps a credential (login-CSRF)
4. a write that plants a config for the next layer
5. a write that stores an XSS for the next viewer
```

## 8. The auth-required map — which session the write needs

```text
the CSRF uses the VIEWER's session — the write's required privilege
is whoever the delivery targets:
- a write anyone's session can do → the victim is anyone
- a write needing admin → the viewer must be the admin-bot
- a write needing a specific account → the bot's fixed account
```

Map the write's auth requirement to the viewer you can deliver to.

## 9. The inventory → probe ordering

```text
for each state-changing endpoint, in flag-proximity order:
  1. does it need a session? which?
  2. SameSite on that cookie?
  3. token required/verified?
  4. Origin/Referer checked?
  5. content-type a form can send?
  6. the write useful (flag-path)?
the endpoint with all six open is the candidate.
```
