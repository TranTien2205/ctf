# Framework matrix — where the merge lives per stack

The per-framework default: which carrier the stack uses, which
merge it ships, and which sink its options feed.

---

## 1. Express 4 — the default CTF stack

```js
app.use(express.json())                      // JSON body → plain object
app.use(express.urlencoded({extended:true})) // qs → bracket carrier
app.set('query parser','extended')           // qs on query too
```

The merge sites: `_.merge(cfg, req.body)` patterns, `Object.assign`,
hand-rolled `for..in` recursion in middleware, `app.locals` writes.

The sinks: `res.render(view, opts)` — opts merges with `app.locals`
+ view-engine options → EJS/Pug/Handlebars gadget names.

```js
// the classic express PP shape
app.post('/update', (req,res)=>{
  _.merge(config, req.body);        // the write
  res.json({ok:1})
})
app.get('/render', (req,res)=>{
  res.render('page', opts)          // the read — ejs outputFunctionName
})
```

## 2. Express 5 — stricter but same shape

- `query parser` default is now `simple` unless set — the query
  carrier is weaker; JSON body carrier unchanged.
- qs version is newer — `allowPrototypes` guard behavior same.
- The body-parser/`merge` sinks are unchanged.

## 3. Fastify

```js
fastify.register(require('@fastify/formbody'))   // urlencoded
fastify.post('/x', async (req,rep)=>{ req.body })// JSON → plain obj
```

Fastify validates against a JSON Schema by default when `schema` is
set — a `body` schema with `additionalProperties:false` strips
`__proto__` at validation — but UNVALIDATED routes and
`additionalProperties:true` containers still carry it. The merge
site is usually a hand-rolled `Object.assign`/spread or a
`@fastify/*` plugin's own merge.

## 4. Koa

```js
app.use(require('koa-bodyparser')())         // JSON → plain object
app.use(require('@koa/multer')())            // multipart
ctx.request.body                              // the parsed body
```

Koa's context `ctx` is itself an object — `ctx.request.body` merges
feed the same `_.merge`/`for..in` sites. `ctx.state` is the render-
locals analog.

## 5. NestJS

```ts
@Post() create(@Body() dto: Dto) { ... }
// class-validator + class-transformer — the DTO strips unknown
// fields on transform — BUT @Body() without a ValidationPipe
// passes the raw object through
```

The `ValidationPipe` is the guard: `whitelist:true` strips non-
decorated fields (a `__proto__` property isn't decorated →
stripped). A route WITHOUT the pipe, or a `transform:false`
config, carries the raw body to a merge.

## 6. Hapi / @hapi

```js
server.route({method:'POST',path:'/x',handler:(req,h)=>{
  const body = req.payload;    // hapi parses JSON itself
  merge(cfg, body);
}})
```

Hapi's `payload` parse uses qs for queries and its own JSON parser —
`__proto__` keys survive the parse; the merge is the sink.

## 7. Meteor / Sails / AdonisJS

Meteor's `EJSON`/DDP — a richer JSON (dates, binary) — the merge
surface is the method-call argument handling. Sails uses express+
waterline — the `Model.update`/`create` merge is a mass-assignment
surface that ALSO accepts nested `__proto__` in attrs on some
versions.

## 8. Python Flask

```python
@app.route('/update', methods=['POST'])
def update():
    merge(config, request.json)         # the merge site
    setattr_loop(cfg, request.json)     # the py sink
    cfg.__dict__.update(request.json)
```

The Python-side sinks: `app.config`, `os.environ`, module globals,
`setattr` on class objects. `request.json` is a plain dict — the
`getattr`/`setattr`-loop or `dict.update` carries the write.

## 9. Python Django

```python
def update(request):
    merge(settings_obj, json.loads(request.body))
    settings_obj.__dict__.update(data)
    for k,v in data.items(): setattr(obj,k,v)
```

Django's `request.POST` is a QueryDict — a dict-like — merges work
the same. The `settings` module's attrs and `django.conf.settings`
reads are the high-value sinks.

## 10. Python FastAPI / Starlette

```python
@app.post('/update')
async def update(body: dict):     # untyped dict — raw JSON in
    merge(cfg, body)

@app.post('/update2')
async def update2(dto: Dto):       # a Pydantic model — validated!
    merge(cfg, dto.dict())          # dto.dict() is a plain dict —
                                    # unknown fields stripped by
                                    # pydantic — __proto__ gone
```

`dict` body = raw carrier; `Dto` body = pydantic-stripped unless
`extra='allow'`. `dto.dict()` re-plainifies but with only declared
fields.

## 11. Next.js / Nuxt — the SSR surface

```js
// pages/api/*.ts / app/api/*/route.ts
export async function POST(req) {
  const body = await req.json()
  _.merge(cfg, body)
}
// getServerSideProps merging req.query into props → client-side
// hydration — a server-side merge feeding a client-side render
```

The `getServerSideProps`/`getStaticProps`/`app` dir loaders pass
server-merged props to the client — a server write that lands in
the client-side React state.

## 12. Golang — the `map[string]interface{}` variant

```go
var m map[string]interface{}
json.Unmarshal(body, &m)          // arbitrary JSON → map
mergo.Merge(&cfg, m)              // mergo map-merge
// or a hand-rolled:
for k,v := range m { cfg[k]=v }   // a map-merge — 'k' is a string
```

Go maps have no prototype — BUT the `mergo`/`mapstructure` merges
of `map[string]interface{}` can carry `__proto__`-shaped KEYS as
literal strings — the write lands on the MAP, not a proto. The PP-
class is JS/Python; in Go the equivalent is a map-key confusion or
a `reflect`-based field-set — a different class.

## 13. Ruby / Rails

```ruby
params.permit(...)                 # strong params — whitelists
params.require(:user).permit(:name)
# unpermitted: params[:settings] is a Hash — deep_merge_into
config.deep_merge(params[:settings])
```

`deep_merge`/`deep_merge!` on a raw `params` Hash — the Rails
analog of `_.merge`. Symbol-vs-string keys matter: `__proto__` as a
string key survives; as a symbol `:"__proto__"` it's still a key —
the write lands on the target Hash (not a proto). Ruby's "PP" is
mass-assignment via `update_attributes`/`assign_attributes` — a
different class boundary.

## 14. Java / Spring

```java
// @RequestBody Map<String,Object> — the map-merge
Map<String,Object> body = ...;
config.putAll(body);               // shallow — no proto
deepMerge(config, body);           // a recursive map-merge —
                                   // 'k' is a literal string
```

Java maps have no proto — but a recursive-map-merge can carry
`__proto__`/`constructor` KEYS into a nested map that later code
reads — a data-confusion more than a proto-write. The Jackson
`ObjectMapper.readValue(x, Map.class)` + `BeanUtils.copyProperties`
surfaces are the class-boundary cases (closer to mass-assignment).

## 15. The matrix summary

| Stack | Carrier | Merge | High-value sink |
|---|---|---|---|
| express | JSON body, qs | _.merge/extend/for..in | ejs/pug opts, spawn env, app.locals |
| fastify | JSON body | hand-rolled/plugin | render opts, spawn |
| koa | JSON body | _.merge/for..in | ctx.state reads |
| nestjs | @Body (unvalidated) | class-transformer/spread | config/service opts |
| hapi | payload | hand-rolled | view opts |
| meteor | EJSON/DDP | method-args | publish/method opts |
| flask | request.json | setattr/update/merge | app.config, os.environ, globals |
| django | request.POST/body | setattr/update | settings attrs, os.environ |
| fastapi | dict body | merge/update | app.state, os.environ, config |
| next.js | api body | _.merge/spread | render props (server→client) |
| grpc | Struct/map/Any | toObject→merge | converted-dict merge |
| graphql | input object | resolver merge | context/opts reads |
| ruby | params.deep_merge | deep_merge! | hash-key confusion (boundary) |
| go | map[string]interface{} | mergo/reflect | map-key confusion (boundary) |
| java | Map<String,Object> | recursive-merge | map-key confusion (boundary) |
