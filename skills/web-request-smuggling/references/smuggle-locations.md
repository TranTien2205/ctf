# Smuggle locations — where the boundary is ambiguous

## The URL-param — `?host={x}` interpolated

```python
requests.get(f"http://{host}/endpoint")
```

The `host` param lands raw inside the outbound request — `%0d%0a` folds —
`crlf-injection.md`.

## The header-value — `X-Custom: {x}`

```python
headers = {"X-Custom": user_input}
requests.get(url, headers=headers)
```

The value lands inside a header — `%0d%0a` folds a new header —
`header-smuggling.md`.

## The request-line — `GET /{x} HTTP/1.1`

```python
requests.get(f"http://t/{path}")
```

The `path` lands in the request-line — `%0d%0a` folds a second request —
`request-line-fold.md`.

## The body — `{x}` inside `Content-Length` bytes

```python
requests.post(url, data={"field": user_input})
```

The `user_input` inside the body — the body's boundary is `Content-Length`
— the body's content can't smuggle — the boundary is fixed.

## The cookie — `Cookie: {x}`

```python
cookies = {"session": user_input}
```

The cookie-value lands inside `Cookie:` — `%0d%0a` folds —
`header-smuggling.md`.

## The Host — `Host: {x}`

```python
requests.get(url, headers={"Host": user_input})
```

The `Host:` value — the vhost-smuggle — `virtual-host.md`.

## The upgrade — `Upgrade: {x}`

```python
headers = {"Upgrade": user_input}
```

The `Upgrade:` value — the tunnel-smuggle — `upgrade-smuggling.md`.

## The proxy-auth — `Proxy-Authorization: {x}`

```python
headers = {"Proxy-Authorization": user_input}
```

The proxy-auth value — the credential-fold — `header-smuggling.md`.

## The websocket-message — `{x}` inside a ws-frame

```python
ws.send(user_input)
```

The ws-message — the tunnel's bytes — `upgrade-smuggling.md`.

## The multipart-part — `{x}` inside a part-body

```python
files = {"file": ("name", user_input)}
```

The multipart-part — the boundary-fold — `content-type-boundary.md`.

## The stored-value — `{x}` stored → interpolated later

```python
db.save(user_input)
# later
requests.get(f"http://{stored}/cb")
```

The stored-value — the deferred-fold — `webhook-deferred.md`.
