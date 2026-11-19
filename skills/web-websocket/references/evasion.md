# Evasion — the checks and how to get past them

## Origin-check bypasses

```bash
for o in 'null' 'file://' 'https://target.evil.com' 'https://eviltarget.com' \
         'https://target.com.evil.com' 'https://sub.target.com' \
         'https://target.com.attacker.com' 'https://targetcom.com' 'null'; do
  python3 tools/web/ws_probe.py "$WS/ws" --origin "$o" --message '{}'
done
```

- a substring/`contains` check — `target.com.evil.com`, `eviltarget.com`
- an `endswith` check — `sub.target.com`/`x-target.com`
- a `null`/`file:` origin — a check that treats null as safe
- a missing `Origin` — a non-browser sends none; a check that requires
  one may pass on its absence

## Auth-binding bypasses

- a stale/forgeable `?token=` — `web-auth-session`'s JWT/token attacks
- a `connection_init`/`40{"token"}` frame that overrides the handshake
  with a controlled token
- a `Sec-WebSocket-Protocol` selecting a weaker-authed protocol
- a `Authorization`/custom-header the check does not validate

## Per-message filter bypasses — the schema-fields

- a `role`/`is_admin`/`debug`/`internal` the frame binds (self-grant)
- a nested `{"user":{"role":"admin"}}` — a deep-merge the validator
  misses (`web-mass-assignment`-shaped)
- an array `{"role":["admin"]}`/`{"perm":["x","admin"]}` — a type-juggle
- a `__proto__`/`constructor`/`prototype` key — `web-prototype-pollution`
- a unicode/case variant of the field name — `User`/`user`/`USER`

## The injection-filter bypasses — the payload's evasion

- SQL: case/`/**`/comment/inline-encoding (`web-sqli`'s evasion)
- SSTI: a `{%`/`${`/`{{`/`#{}`/`<%=` variant (`web-ssti`)
- CMDi: `;`|`|`/`&&`/`$()`/`` ` ``/`%0a` (`web-command-injection`)
- LFI: `..%2f`/`..\\`/`%2e%2e`/`....//`/`/..//` (`file-read-primitives`)
- the frame carries it — the WS transport may bypass an HTTP-layer WAF
  that only inspects `GET`/`POST` bodies

## The transport-switch evasion

An HTTP-layer WAF/filter does not inspect frames — a payload blocked in
an HTTP `POST` body may pass in a WS frame. The WS transport is itself
the evasion — the HTTP-layer rules never see the frame.

## The per-connection vs per-account throttle

- a per-connection limiter → open N sockets, one probe each
- a per-IP limiter → the HTTP `X-Forwarded-For` does not apply to a
  persistent socket; a reconnect resets a per-connection count
- a per-account limiter → the lock only writes to a real account
  (the enum's lock-oracle boundary)

## The sub-protocol/differential evasion

- `Sec-WebSocket-Protocol: graphql-ws` → the graphql parser may not run
  the raw-WS validators (a `web-parser-differential`)
- a `Sec-WebSocket-Extensions`/`permessage-deflate` — a compressed frame
  that bypasses a content-filter inspecting only uncompressed bytes

## The evasion record

`evasion: <the-check>: <the-bypass>` — the verbatim bypass + the reply;
the bypass is a finding (a broken control), not a license for an
unbounded sweep.
