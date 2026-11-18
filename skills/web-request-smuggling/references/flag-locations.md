# Flag locations — where the flag sits behind a smuggle

## The internal-route — `/flag` loopback-only

```python
@app.route('/flag')
def flag():
    if request.remote_addr != '127.0.0.1':
        return 403
    return open('/flag.txt').read()
```

The flag is on the back-end's loopback — the smuggle reaches it as the
back-end → the flag in the response — `internal-routes.md`.

## The internal-vhost — `Host: internal`

```nginx
server {
    listen 127.0.0.1:8080;
    server_name internal;
    location /flag { return 200 "flag{...}"; }
}
```

A vhost bound to loopback — `Host: internal` smuggle — the flag route.

## The stored-param — the flag inside a victim's request

```python
@app.route('/store')
def store():
    db.save(request.form['x'])    # stores the smuggle's body
```

The victim's request lands inside `x=` — the stored request carries the
flag-cookie or the flag-path — `session-hijack.md`.

## The admin-bot's flag — the bot's cookie

```python
admin_bot.visit(url)   # the bot carries the flag-cookie
```

The smuggle poisons the bot's request → the bot's flag-cookie lands
inside the smuggle's body → `session-hijack.md`.

## The internal-port — `Host: t:9000`

```text
GET /flag HTTP/1.1
Host: t:9000
```

A flag-listener on an internal port — the smuggle's `Host:` probes it —
`internal-routes.md`.

## The internal-path — `/internal/flag`, `/debug/flag`

```text
GET /internal/flag HTTP/1.1
Host: t
```

The flag on an internal path — filtered on the front, open on the back.

## The `/actuator/env` — the Spring-style env dump

```text
GET /actuator/env HTTP/1.1
```

The env-endpoint leaks the flag-variable — the smuggle reaches it.

## The `/metrics` — the Prometheus flag

```text
GET /metrics HTTP/1.1
```

A flag in a metric label — `/metrics` smuggle.

## The readback — the verbatim excerpt

```bash
python3 tools/hooks.py pre-flag <name> --value "flag{...}" \
  --source "response" --evidence "<the verbatim excerpt>"
```

The flag text inside the smuggle's response — verbatim.
