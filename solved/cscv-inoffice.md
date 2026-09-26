# in-office (CSCV 2026) — web

Flag read from a live response. Value not recorded here.

## Stack
HAProxy 2.9.7-alpine in front of gunicorn 25.3.0 / Flask 3.1.3 on an internal
docker network. `/office-process` unpickles an uploaded file through a
`RestrictedUnpickler` that allows `module == "builtins"` minus
`exec`/`eval`/`__import__`. `/healthcheck` is an SSRF taking `method`, `url` and
a JSON `headers` dict.

## The two gates

    acl is_office_path path,url_dec -i -m sub office
    acl is_multipart  req.hdr(Content-Type) -i -m beg multipart/form-data
    http-request deny if is_office_path !network_office
    http-request deny if is_multipart   !network_office
    use_backend back1 if is_office_web        # hdr(host) -i mmoffice.x.corp

`network_office` is `src 192.168.17.0/24 10.0.17.0/24` and is not reachable.

## Chain

**Multipart ACL** — prefix the header value with `0x0b`:
`Content-Type: \x0bmultipart/form-data; boundary=x`. HAProxy strips only SP and
HTAB, so `-m beg` misses; Werkzeug's `parse_options_header` uses Python
`str.strip()`, which also strips `\x0b`, and still parses the boundary.

**Path ACL** — an authority-form request-target:

    POST office-process?,mmoffice.x.corp HTTP/1.1
    Host: office-process?,mmoffice.x.corp

Three parsers disagree at the same time:

- HAProxy's `http_get_path()` returns not-found when the target neither starts
  with `/` nor has a scheme followed by `//`, so the `path` sample is unset and
  `is_office_path` cannot match (HAProxy issue #2565, same 2.9.7 build).
- HAProxy accepts authority-form only when the authority is byte-equal to
  `Host`, but `hdr(host)` splits on commas and tests every occurrence, so the
  `mmoffice.x.corp` element still satisfies `use_backend`.
- Python's `urlsplit` puts everything after `?` in the query, and Werkzeug
  matches on `"/" + path.lstrip("/")`, so the bare token becomes
  `/office-process`.

**Restricted pickle** — `is_safe` gates the *module*, not the name, so
`builtins.getattr`, `builtins.dict` and `builtins.globals` are all reachable.
`globals()` invoked from a REDUCE resolves to the nearest Python frame —
`restricted_loads` in `utils.py` — handing over that module's namespace.
From there: `pickle` → `pickle.sys` → `sys.modules` → `app` → the Flask app →
`view_functions`. Then `open('/flag.txt').read()` and bind the flag string's own
`.strip` bound method into `view_functions['index']`; `GET /` returns the flag.
A second pickle rebinds `index` to `sys.modules['app'].index` to restore it.

## Traps
- A port in the authority breaks the backend side:
  `urlsplit('office-process:80')` parses `office-process` as a *scheme* and
  leaves path `'80'`.
- No request-target whose `path` sample is *set* can work. In every form HAProxy
  accepts, its authority scan and Python's `netloc` end at the same `/`, and
  `url_dec` decodes exactly like Python's `unquote` — so making `url_dec` fail
  leaves a literal `%` that Werkzeug cannot route. 40+ URI forms measured.
- The `/healthcheck` SSRF cannot deliver the pickle. With only method/url/headers,
  `urlopen` can never emit a body: http.client's `_is_illegal_header_value`
  (`\n(?![ \t])|\r(?![ \t\n])`) permits only obs-fold, which never terminates the
  header block, and POST without data always sends `Content-Length: 0`.
- gunicorn honours a `SCRIPT_NAME` request header (prefix-strip, which would turn
  `*/office-process` into `/office-process`) only from a peer inside
  `forwarded_allow_ips` (`127.0.0.1,::1`). It works when testing the backend
  directly and silently fails through HAProxy, where `header_map=drop` removes it.
  HAProxy itself forwards underscore headers untouched — the drop is gunicorn's.
- `/healthcheck` returns `error` for any 4xx/5xx because `urlopen` raises
  `HTTPError`, so a 2xx status is its only positive oracle.
