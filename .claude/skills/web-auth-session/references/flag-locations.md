# Flag locations — where the flag lives after the auth boundary breaks

The auth is the gate; the flag is behind it. This file maps the common
locations so the forge leads somewhere.

---

## 1. The `/admin/*` surface

```
/admin              → dashboard
/admin/flag         → the flag
/admin/flag.txt     → file
/admin/panel        → panel
/admin/dashboard    → dashboard
/admin/users        → user list (admin's data has flag)
/admin/users/1      → admin user detail
/admin/settings     → settings
/admin/config       → config (flag in env)
/admin/env          → environment dump
/admin/logs         → log access (flag in log)
/admin/backup       → backup download (flag inside)
/admin/db           → database shell
/admin/sql          → SQL console
/admin/shell        → command shell
/admin/exec         → exec
/admin/cmd          → cmd
/admin/run          → run
/admin/eval         → eval
/admin/debug        → debug
/admin/test         → test
/admin/dev          → dev
/admin/internal     → internal
/admin/secret       → secret
/admin/private      → private
/admin/hidden       → hidden
/admin/protected    → protected
/admin/secure       → secure
/admin/restricted   → restricted
/admin/sensitive    → sensitive
/admin/confidential → confidential
/admin/classified   → classified
/admin/top-secret   → top-secret
/admin/topsecret    → topsecret
/admin/forbidden    → forbidden
/admin/exclusive    → exclusive
/admin/vip          → vip
/admin/premium      → premium
/admin/pro          → pro
/admin/staff        → staff
/admin/mod          → mod
/admin/moderator    → moderator
/admin/support      → support
/admin/operator     → operator
/admin/service      → service
/admin/root         → root
/admin/system       → system
/admin/superuser    → superuser
/admin/super        → super
/admin/sudo         → sudo
/admin/god          → god
/admin/master       → master
/admin/owner        → owner
/admin/founder      → founder
/admin/creator      → creator
/admin/maintainer   → maintainer
/admin/developer    → developer
/admin/devops       → devops
/admin/sre          → sre
/admin/ops          → ops
/admin/it           → it
/admin/security     → security
/admin/audit        → audit
/admin/compliance   → compliance
/admin/legal        → legal
/admin/finance      → finance
/admin/billing      → billing
/admin/accounting   → accounting
/admin/hr           → hr
/admin/management   → management
/admin/executive    → executive
/admin/director     → director
/admin/vp           → vp
/admin/cxo          → cxo
/admin/ceo          → ceo
/admin/cfo          → cfo
/admin/cto          → cto
/admin/ciso         → ciso
/admin/cio          → cio
/admin/president    → president
/admin/chairman     → chairman
/admin/board        → board
/admin/council      → council
/admin/committee    → committee
/admin/panel        → panel
/admin/jury         → jury
/admin/judge        → judge
/admin/reviewer     → reviewer
/admin/approver     → approver
/admin/verifier     → verifier
/admin/validator    → validator
/admin/inspector    → inspector
/admin/auditor      → auditor
/admin/monitor      → monitor
/admin/watcher      → watcher
/admin/observer     → observer
/admin/supervisor   → supervisor
/admin/overseer     → overseer
/admin/controller   → controller
/admin/manager      → manager
/admin/lead         → lead
/admin/head         → head
/admin/chief        → chief
/admin/principal    → principal
/admin/senior       → senior
/admin/junior       → junior
/admin/staff        → staff
/admin/employee     → employee
/admin/worker       → worker
/admin/member       → member
/admin/associate    → associate
/admin/assistant    → assistant
/admin/intern       → intern
/admin/volunteer    → volunteer
/admin/consultant   → consultant
/admin/contractor   → contractor
/admin/vendor       → vendor
/admin/partner      → partner
/admin/client       → client
/admin/customer     → customer
/admin/guest        → guest
/admin/visitor      → visitor
/admin/anonymous    → anonymous
/admin/public       → public (ironic — check it anyway)
```

The `/admin/` prefix is the obvious gate; the *endpoint name* under it
varies. `ffuf`/`gobuster` the subtree once you have admin.

## 2. The API surface

```
/api/admin          → admin API
/api/v1/admin       → versioned
/api/v2/admin       → v2
/api/flag           → flag endpoint
/api/v1/flag        → versioned flag
/api/secret         → secret
/api/v1/secret      → versioned
/api/internal       → internal
/api/v1/internal    → versioned
/api/private        → private
/api/v1/private     → versioned
/api/protected      → protected
/api/secure         → secure
/api/restricted     → restricted
/api/sensitive      → sensitive
/api/confidential   → confidential
/api/users          → all users
/api/users/1        → user 1 (admin)
/api/users/0        → user 0 (root)
/api/user           → current user
/api/me             → current user
/api/profile        → profile
/api/account        → account
/api/session        → session info
/api/token          → token info
/api/auth           → auth info
/api/config         → config
/api/env            → env
/api/settings       → settings
/api/status         → status
/api/health         → health
/api/info           → info
/api/version        → version
/api/debug          → debug
/api/test           → test
/api/dev            → dev
/api/internal/flag  → internal flag
/api/admin/flag     → admin flag
/graphql            → GraphQL — the flag is a field
/graphql?query=...  → query
```

## 3. The data field

The flag is often a *field* on a privileged object, not an endpoint:

- `user.flag` — the admin user's `flag`/`note`/`bio`/`secret` field.
- `user.secret` — same.
- `user.note` — a private note.
- `user.bio` — bio field.
- `post.flag` — a private post.
- `message.flag` — a DM.
- `file.flag` — an uploaded file.
- `document.flag` — a stored doc.
- `config.flag` — an env/config value.
- `session.flag` — the session store entry.
- `token.flag` — a token claim.
- `jwt.flag` — inside the JWT itself (the flag is a claim).

The forge gives you admin; the flag is a *read* on the admin's row.

## 4. The env/config surface

```
GET /admin/env        → environment
GET /admin/config     → config
GET /api/config       → same
GET /config.json      → static
GET /.env             → the env file
GET /proc/self/environ → via file-read
GET /debug/vars       → Go expvar
GET /actuator/env     → Spring
GET /actuator/configprops → Spring
GET /server-status    → Apache
GET /nginx_status     → nginx
GET /phpinfo.php      → PHP
GET /info.php         → PHP
GET /elmah.axd        → .NET
GET /trace.axd        → .NET
GET /__debug__/       → Flask/Werkzeug
GET /console          → Werkzeug debugger (RCE)
GET /_profiler/       → Symfony
GET /telescope/       → Laravel
GET /horizon/         → Laravel
GET /debugbar/        → Laravel
GET /adminer.php      → Adminer
GET /phpmyadmin/      → PMA
GET /pma/             → PMA
GET /db/              → db admin
GET /database/        → db admin
```

The flag is `FLAG`/`flag`/`SECRET`/`FLAG_VALUE`/`CTF_FLAG` in env —
the config surface dumps it.

## 5. The internal/loopback surface

The flag is on a loopback-only route that only the server can reach —
the auth boundary gives you the *session* that reaches an SSRF, and the
SSRF reaches the internal flag. See `web-ssrf`.

```
http://127.0.0.1:8080/flag
http://localhost:3000/admin
http://[::1]:8000/internal
http://0.0.0.0:9000/secret
http://127.1/flag              → short form
http://2130706433/flag         → decimal
http://0x7f000001/flag         → hex
http://0177.0.0.1/flag         → octal
http://127.0.0.1.xip.io/flag   → DNS
http://localtest.me/flag       → resolves to 127.0.0.1
http://localhost.localdomain/flag
http://lvh.me/flag
http://nip.io/flag
http://sslip.io/flag
http://vcap.me/flag
http://lacolhost.com/flag
http://127.0.0.1.nip.io/flag
http://127-0-0-1.org.uk/flag
http://spoofed.burpcollaborator.net/flag
```

## 6. The GraphQL field

```graphql
query { flag }
query { admin { flag } }
query { user(id:1) { flag secret note } }
query { users { flag } }
query { config { flag secret } }
query { internal { flag } }
query { node(id:"<admin-gid>") { ... on User { flag } } }
mutation { readFlag }
```

See `web-graphql` — auth gets you the session, the query gets the field.

## 7. The second-order flag

The flag is in the *bot's* session or a job's output — the admin bot
logs in (you triggered it), reads `/flag`, stores it somewhere you can
read. Or the job's output file carries it. The chain is:

```
your-session → trigger admin-bot → bot reads /flag → bot stores it
             → your-session reads the stored copy
```

## 8. The source-tree flag

`flag.txt` / `flag` / `.flag` / `flag.py` / `flag.js` / `flag.php` /
`flag.json` / `flag.yml` / `flag.env` / `FLAG` — read it via the
file-read primitive the admin session unlocks (LFI, path traversal,
`read_loop`).

## 9. The "the flag IS the session" edge

Sometimes the flag is the admin's *session id itself* — you don't need
to reach an endpoint, the stolen/forged session value is the answer.
Or the flag is a JWT claim — `session_dissect --token` reveals it.

## 10. The reach-map

After the forge, the order:

1. `/api/me` — what does the forged session see? (`role`, `flag` field?)
2. `/admin`, `/admin/*` — the admin subtree (enumerate if needed).
3. `/api/admin`, `/api/flag`, `/api/v1/flag` — the API flag.
4. The admin user's data — `/api/users/1`, `/users/1`.
5. The config/env surface — `/admin/env`, `/api/config`.
6. The internal surface — SSRF via the admin session.
7. The GraphQL field — `query { flag }`.
8. The second-order — bot/job.
9. The source tree — `flag.txt`.

`http_probe --evidence-regex 'flag\{|CTF\{|FLAG\{' --evidence-kind
impact` on each — the first `confirms` is the flag.
