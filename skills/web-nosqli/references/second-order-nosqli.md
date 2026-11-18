# Second-order NoSQLi — the stored-filter

## The shape — the operator stored, the filter later

```javascript
// POST /profile — store the operator
app.post('/profile', async (req, res) => {
  await User.updateOne({user: req.user.name}, {$set: {bio: req.body.bio}})
})

// GET /search — the stored bio reaches the filter
app.get('/search', async (req, res) => {
  const users = await User.find({bio: {$regex: req.user.bio}})
})
```

The stored-field's content reaches a LATER query's filter —
`injection-points.md`-adjacent — the injection is stored, not direct.

## The `username`-as-filter — the self-referential

```javascript
// POST /register — the user names themselves
app.post('/register', async (req, res) => {
  await User.create({user: req.body.user, pass: req.body.pass})
})

// GET /me — the user's name reaches the filter
app.get('/me', async (req, res) => {
  const me = await User.findOne({user: req.user.name})
})
```

`user: "{$ne: null}"` — the stored-username reaches `findOne` — the
self-referential injection — `injection-points.md`.

## The `bio`/`notes`/`meta` — the free-text

```javascript
app.post('/profile', async (req, res) => {
  await User.updateOne({user: req.user.name}, {$set: {bio: req.body.bio}})
})
```

The `bio`/`notes`/`description`/`comment`/`meta`/`settings` — the
free-text field — the stored-injection's home — `injection-points.md`.

## The `filter`-as-data — the stored-query

```javascript
// POST /saved-search — the user saves a filter
app.post('/saved-search', async (req, res) => {
  await SavedSearch.create({name: req.body.name, filter: req.body.filter})
})

// POST /run — the saved filter runs
app.post('/run', async (req, res) => {
  const s = await SavedSearch.findOne({name: req.body.name})
  const users = await User.find(s.filter)
})
```

The saved-filter — `{"filter": {"$ne": null}}` stored then run —
`injection-points.md`.

## The `template`-injection — the stored-render

```javascript
app.post('/page', async (req, res) => {
  const page = await Page.findOne({slug: req.body.slug})
  res.send(render(page.template, {data: page}))
})
```

The stored-template — the render-side — `skills/web-ssti/` — different
class.

## The `log`-injection — the stored-filter

```javascript
app.post('/log', async (req, res) => {
  await Log.create({msg: req.body.msg, user: req.user.name})
})
app.get('/logs', async (req, res) => {
  const logs = await Log.find({user: req.query.user})
})
```

The stored-log — `injection-points.md`.

## The `session`-injection — the stored-cookie

```javascript
app.post('/login', async (req, res) => {
  const user = await User.findOne({user: req.body.user})
  if (user) req.session.user = user.user
})
```

The session-carrier — `skills/web-auth-session/` — different class.

## The `cache`-injection — the stored-cache

```javascript
const cached = await Cache.findOne({key: req.body.key})
if (!cached) await Cache.create({key: req.body.key, val: req.body.val})
```

The cache-store — `injection-points.md`.

## The `queue`-injection — the stored-job

```javascript
await Queue.create({job: "send", data: req.body.data})
```

The queue-store — `injection-points.md`.

## The `webhook`-injection — the deferred

```javascript
await Webhook.create({url: req.body.url, filter: req.body.filter})
```

The webhook — `skills/web-ssrf/` — different class.

## The `profile`-injection — the self-doc

```javascript
app.post('/profile', async (req, res) => {
  await User.updateOne({user: req.user.name}, {$set: req.body})
})
```

`$set: req.body` — the whole body into the update — `update-injection.md`
— the mass-assignment-adjacent — `skills/web-mass-assignment/`.

## The `import`-injection — the bulk-load

```javascript
app.post('/import', async (req, res) => {
  await User.insertMany(req.body.users)
})
```

`insertMany` — `update-injection.md`.

## The `export`-injection — the read-side

```javascript
app.get('/export', async (req, res) => {
  const users = await User.find({})
})
```

The export — `injection-points.md`.
