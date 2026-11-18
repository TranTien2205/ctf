# Injection Points — where the input actually lands

## The classic spots — `?param=`/body/header/cookie

| Spot | Shape | Probe |
|---|---|---|
| `?host=`/`?ip=`/`?target=`/`?name=` | query param | `x;id` |
| `?host[]=` | array param | `x;id` in element |
| `?cmd=`/`?exec=`/`?run=` | query param | `x;id` or eval payload |
| form field `host=` | POST body | `x;id` |
| JSON `"host":"..."` | body | `"x;id"` |
| multipart `name=host` | body | `x;id` in part |
| `Cookie: host=x` | header | `x;id` in cookie |
| `User-Agent`/`Referer`/`X-*` | header | `;id` in header |
| `X-Forwarded-For` | header | IP-ish injection |
| `Authorization`/bearer | header | rarely |
| path segment `/ping/x` | URL-path | `x;id` in segment |
| filename upload `x.png` | multipart-name | `x.png;id` |
| second-order stored field | DB→later-exec | `second-order.md` |

## The JSON-shape — `"x":"y"` the injection inside a value

```json
{"host":"x;id"}           — the whole value is the arg
{"host":"x;id","op":"ping"}
{"cmd":"ping","args":["x;id"]}   — args-array might reach exec
{"expr":"7*7"}            — evaluator
{"f":"x.png;id"}          — filename injection
{"url":"http://x;id"}     — URL-arg
{"host":"127.0.0.1\nid"}  — \n inside the string
{"host":"127.0.0.1\tid"}  — \t
{"host":"127.0.0.1;id"}
```

The `"x;id"` string is passed verbatim to the command — JSON-decoded
before the shell — the `;` survives.

## The nested/encoded injection — `host=x%3bid` inside JSON/params

`{"host":"x;id"}` the `;` isn't URL-encoded inside JSON — the parser
decodes before the shell. But `{"host":"x%3bid"}` — if the app
double-decodes — `;` arrives.

## The `args[]` array-form — when args are separate

```json
{"cmd":"ping","args":["-c","4","x;id"]}
```

- if `args[]` is passed to `execFile`/`spawn(cmd,args)` — the `;` is
  one arg — SAFE (arg-injection only: `["--upload-pack=id"]`)
- if `args[]` is `.join(' ')`'d then shelled — the `;` splits —
  INJECTION
- if `args[]` is each shelled separately — array-element injection

## The parameter-name injection — `?x=y` where the NAME is tainted

`?ping=1&x=id` — if the app does `system($_GET['cmd'].' '.$_GET['arg'])` —
both name and value can carry the injection. Rare but seen — fuzz the
param NAMES too.

## The path-segment injection — `/ping/{host}`

`/ping/x;id` — if the route does `system('ping '.$host)` — the path
segment is the arg — `;` is a valid path char — `/ping/x;id` works.
`/ping/x%3bid` decodes to `;`.

## The multipart-file injection — filename + content

`Content-Disposition: name="f"; filename="x.png;id"` — the FILENAME is
the injection — `filename-injection.md`. The file CONTENT is a separate
surface (`imagemagick-deep.md`).

## The header/cookie side — when headers reach exec

- `User-Agent`/`Referer`/`X-Forwarded-For`/`X-Real-IP`/`X-Client-IP` —
  logged → `log-poisoning.md`
- `Cookie`/`X-Custom-*` — if logged/exec'd
- `Host`/`X-Forwarded-Host` — rarely exec'd
- `X-Original-URL`/`X-Rewrite-URL` — rewrite-driven

## The multipart/mixed boundary — one body many params

Each `Content-Disposition` part is a param — `name="host"` part-value
is the arg — `--data-urlencode` doesn't apply inside multipart — raw
`x;id` in the part body.

## The `callback`/`jsonp` param — a different tainted surface

`?callback=x;id` — the name is concatenated into output — an
eval-or-xss shape, not cmdi — route to `web-xss` if it lands in JS.

## The second-order — `second-order.md` for the full story

A value stored then exec'd later — registration → admin-tool runs it —
the injection survives storage. The probe writes a marker, waits, reads
the side-channel.

## The "multiple inputs combine" — `system("ping $host -c $count")`

`$host` and `$count` are separate inputs — inject either; `count`
`intval`'d → host is the live one. Check EVERY tainted input.

## Falsifiers

- the input never reaches any exec surface — mapped via white-box or
  exhaustive black-box probing — class dead

## Output to record

- which injection point (param/body/header/cookie/path/filename/array)
  carried the payload
