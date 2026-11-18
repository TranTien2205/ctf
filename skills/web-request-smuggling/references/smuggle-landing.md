# Smuggle landing — where the poisoned bytes land

## The back-end's parser — the smuggle's parser

The smuggle's bytes land on the back-end's HTTP parser — the back-end
parses them as a NEW request — `desync-taxonomy.md`.

## The next-request slot — the queue's position

```text
your-req → [smuggle] → next-victim-req
```

The smuggle sits between — the next victim's request follows it —
`response-poisoning.md`.

## The prefix-landing — `GPOST` vs the victim's `POST`

```text
G + POST /home → GPOST /home
```

The `G` prefixes the victim's `POST` — `GPOST` is malformed — `cl-te-desync.md`.

## The full-request landing — `GET /admin` standalone

```text
[your-smuggle: GET /admin] → [victim's: GET /home]
```

The smuggle is a complete request — it runs — the victim's request is
next — `smuggle-shapes.md`.

## The header-injection landing — inside the victim's headers

```text
[smuggle: ...\r\n] + [victim's: GET /home ...]
```

The smuggle's trailing `\r\n` merges with the victim's headers — a
header-merge — `header-smuggling.md`.

## The body-landing — the victim inside your body

```text
[your-smuggle: POST /store CL:400 body=x=] + [victim's full request]
```

The victim's request is inside your `x=` — `session-hijack.md`.

## The socket-close — the smuggle that never lands

`Connection: close` on the smuggle's last request — the socket closes
— the smuggle never lands — `smuggle-stability.md`.

## The pool-slot — the non-deterministic landing

The victim has to hit the same pool slot — `queue-management.md`.

## The upgrade-tunnel — the smuggle inside a frame

```text
[ws-frame: GET /admin]
```

The smuggle inside a ws-frame — `upgrade-smuggling.md`.

## The h2-layer — the smuggle inside a DATA frame

```text
[DATA frame: GET /admin]
```

The smuggle inside an h2 DATA frame — `http2-smuggling.md`.
