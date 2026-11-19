# Evasion — reaching the logic layer past the defenses

Logic flaws live below the input-validation layer — but the defenses
that block probes live above it. This module is the path past them.

## Content-type shifting

An endpoint allowlisting fields under `application/json` may parse
`application/x-www-form-urlencoded` through a different binder:

```bash
# JSON path — schema-validated
curl -X POST $BASE/register -H "Content-Type: application/json" \
  -d '{"u":"p","role":"admin"}'          → 400 unknown field

# form path — different binder
curl -X POST $BASE/register -d 'u=p&role=admin'   → ?
```

The field the JSON schema rejects may bind through the form path —
two parsers, two allowlists, same model. Probe every content-type the
endpoint accepts; `multipart/form-data` adds a third binder.

## Encoding the key

```
role       %72ole       r%6fle       role%00
Role       ROLE         role[]       user.role
```

Encoded or decorated keys reach different parser paths — a validator
matching literal `role` misses `%72ole` that the binder decodes. The
`%00` terminator and `role[]` array-form each test whether key matching
happens before or after decoding.

## Duplicate delivery

```
?role=user&role=admin            query order — last/first/array wins
{"role":"user","role":"admin"}   JSON duplicate — last wins typically
role=user\nrole=admin            in a parsed body
```

The validator sees one `role`, the binder takes another — the
parser-differential at the key layer. Probe both orders; if the app
validates `params["role"]` but binds `params.get_all("role")[-1]`, the
second wins.

## Method shifting

- `PATCH`/`PUT` binders differ from `POST` — update endpoints often
  have their own (wider or absent) allowlist.
- `GET` on a transition endpoint — a state change on a read verb skips
  CSRF defenses and prefetch assumptions.
- `POST` with `_method=PUT` — framework method-override routes the
  request through the PUT handler with POST's validation.

## Boundary-carrier shifting

The state the workflow checks may live in:

- **cookie** — `step=3` forgeable if unsigned;
- **param** — `?step=3`, `state=confirmed`;
- **header** — `X-Step: 3`, `X-Forwarded-State`;
- **body field** — `{"step":3}`;
- **session** — server-side; the falsifier's home.

Probe each carrier — the handler may read `step` from the cookie while
the UI carries it in the body.

## Rate-limit evasion (budget discipline)

Logic probes are cheap — but a `429` wall isn't a falsifier. Rotate the
session (new account = new rate bucket in per-user limiters), vary the
`X-Forwarded-For` (per-IP limiters — and note the boundary trust), and
space writes. Do NOT spray — the challenge budget is the real limit.

## WAF / filter pass-through

A WAF matching `admin` in values may miss:

- `admin` in a nested JSON key-path (`{"meta":{"priv":"admin"}}`),
- unicode-fullwidth `ａｄｍｉｎ` (normalized differently),
- `admin` split across duplicate params (`role=ad&role=min` — a parser
  that concatenates vs one that validates each).

The WAF guards the transport; the binder is behind it. The gap between
"what the WAF inspects" and "what the binder receives" is the same
structural validator-gap as Pachinko, one layer up.
