# lab/vulnapp.py — the offline evaluation target

Deliberately vulnerable single-file app, **stdlib only** (no pip needed,
Windows-friendly). One planted bug per Argus probe family — the exact set
used by `selftest.py`, `pytest` and `argus demo` for reproducible results.

| Route | Planted issue |
|---|---|
| `/search?q=` | reflected XSS (unescaped reflection) |
| `/item?id=` | SQLi — error-based + boolean-blind (sqlite) |
| `/product?id=` | SQLi — numeric context (unquoted pair only) |
| `/stock?sku=` | SQLi only via OR true/false pair |
| `/reset` | host-header poisoning: form action built from XFH |
| `/settings/update-email` | GET state-change form (CSRF lead) |
| `POST /login` | SQLi auth bypass + user-enum error differential |
| `POST /login2` | user-enum via **timing** (uniform error text) |
| `POST /login3` | rate-limited login: 429 after 5 fails/user |
| `POST /api/register` | mass-assignment: stores every sent field |
| `/ping?host=` | OS command injection — real argv execution from a seven-command allowlist (`id`, `whoami`, `uname`, `hostname`, `pwd`, `echo`, `cat`), never a shell, plus the sleep separators for the blind case |
| `/hello?name=` | SSTI (`{{7*7}}` → 49) |
| `/download?file=` | path traversal (`../`, fakefs) |
| `/redirect?next=` | open redirect incl. `javascript:` scheme |
| `/safedirect?next=` | filtered redirect (`//host` bypass) |
| `/jsredirect` | client-side DOM redirect |
| `/api/user/<id>`, `POST /api/order` | IDOR (path + JSON body) |
| `/fetch?url=` | SSRF (real fetch, `file://` readable) |
| `POST /xml` | XXE (external entity resolution) |
| `POST /api/login` | NoSQLi (`$ne`/`$gt` operator bypass) |
| `POST /upload`, `GET /uploads/<f>` | upload served back, active content-type |
| `/redeem` | race condition (unlocked check-then-act) |
| `/import?data=` | deserialization (magic bytes → parser error) |
| `/cached` | cache poisoning (unkeyed X-Forwarded-Host) |
| `/profile[/x.css]` | cache deception (path confusion) |
| `/api/config`, `POST /api/config2` | prototype pollution (`__proto__` + `constructor.prototype`) |
| `/api/data` | CORS: reflects Origin + credentials (simple + preflight) |
| `/token`, `/api/me` | JWT HS256, weak secret `secret123` — crack → forge admin |
| `POST /desync*` | request smuggling CL.TE / TE.CL / obfuscated-TE + agreed-framing control |
| `/admin`, `/internal`, `/debug` | host-header bypass via X-Original-URL |
| `/.git/HEAD`, `/.env`, `/debug`, `robots.txt` | info disclosure |
| `/graphql` | introspection (POST + GET `?query=`) |
| `/ws` | WebSocket upgrade (101) |
| `/static/*.map` | sourcemap → JS recon |

Plus recon surface: forms, cookies with hygiene flags to notice,
Server/framework headers for fingerprinting.

```bash
python lab/vulnapp.py 8777
python -m argus run http://127.0.0.1:8777
```

Do NOT expose this app beyond localhost — it is vulnerable on purpose.

## Why /ping really executes

The lab's whole job is to let the agent reach the evidence a finding needs,
and `argus proof rce` asks for the output of `id; echo <nonce>`. A simulated
`sh: syntax error` gave the probe nothing to read, so the class was
unprovable anywhere in the project.

So it executes, under two bounds. The server binds `127.0.0.1` only, and
commands run as an argv list through the allowlist above — never through a
shell — so a destructive or networked payload is inert and comes back
`command not found`, which is also what a hardened target looks like. `cat`
is confined to the lab's fake filesystem: a lab must not read the operator's
real files to make a point. The injection is real; the blast radius is not.

Do not expose this on a network interface. That was true before and it is
more true now.
