# Protocol version and vhost differentials

HTTP/1.0 and HTTP/1.1 are handled by different code paths in most proxies, and
vhost selection depends on exactly how the `Host` header arrives. Both are
parser differentials: the front end decides one thing, the backend answers
another.

## HTTP/1.0 with an empty Host

`Host` is mandatory in HTTP/1.1 but optional in HTTP/1.0. A 1.0 request with no
Host — or an empty one — falls through name-based vhost matching to the
*default* vhost, which is often an internal site.

**Probe** (Dusty Alleys):

```text
GET /reflect HTTP/1.0
Host:

GET /reflect HTTP/1.1
Host: target.example
```

Expected: a reflecting endpoint echoes an internal domain name as the host, or
serves a vhost that was never reachable by name — the leaked internal hostname
then feeds SSRF targets or a second request that names it explicitly.
Falsifier: the reflected host is unchanged, or the proxy rejects the request
outright.

## Version-dependent behaviour worth diffing

| Dimension | 1.0 | 1.1+ |
|---|---|---|
| Host requirement | optional | mandatory |
| Keep-alive | off unless negotiated | on by default |
| Chunked bodies | unsupported | supported |
| `Transfer-Encoding` | ignored or rejected | parsed |

A proxy that accepts `Transfer-Encoding` on 1.0, or treats it as 1.1 in one
direction and 1.0 in the other, is a smuggling candidate — that branch lives in
`../../web-request-smuggling/SKILL.md`.

## Falsifier

The request is rejected at the proxy, or every version and Host variant returns
the same vhost — the farm has a single default and there is nothing to leak.

## Traps

- Some proxies silently upgrade 1.0 to 1.1 before routing; check whether the
  version on the wire survived by reflecting it.
- A default vhost that answers with the *same* content as the named one is a
  non-signal — compare against a request you control, not just the status.
