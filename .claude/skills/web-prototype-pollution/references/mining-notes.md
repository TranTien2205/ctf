# Mining notes — extracting the write and the read out of a handout

The white-box mining procedure for a PP challenge: find the merge,
find what it merges, find what reads the merged object.

---

## 1. The three artifacts

1. **the merge site** — where `req.*`/parsed input gets assigned
   into a live object
2. **the read site** — where a later lookup reads a fallback for a
   property name
3. **the carrier** — how the attacker-shaped object reaches the
   merge

A challenge is PP when all three exist and line up on the same
property name.

## 2. Mining the merge site

```bash
# grep the write vocabulary
grep -rnoE '\.merge\(|_\.merge|_\.defaultsDeep|merge\s*\(|deepmerge|deep-extend|extend\s*\(\s*true|\$\.extend\s*\(\s*true|jQuery\.extend\s*\(\s*true|Object\.assign|\.assign\s*\(|for\s*\(\s*var|for\s*\(\s*const|for\s*\(\s*let' \
  . --include='*.js' --include='*.ts' \
  | grep -vE 'node_modules|\.min\.|test|spec' \
  | grep -iE 'req\.|body|query|input|data|config|opts|setting' \
  | head -80

# the path-setters
grep -rnoE 'dset|object-path|set-value|set\s*\(\s*[a-z_]+\s*,\s*[a-z_]*path|\.split\(\s*["'"'"']\.["'"'"']\)|lodash\.set|_\.set\s*\(' \
  . --include='*.js' | grep -v node_modules | head -40

# the Python shapes
grep -rnoE 'setattr\s*\(|__dict__\.update|vars\s*\(.+\)\.update|getattr\s*\(.+,\s*[a-z_]+\)|\.update\s*\(\s*request' \
  . --include='*.py' | head -40

# the document-store operators
grep -rnoE '\$rename|\$set|\$unset|\$push|\$addToSet|updateOne|findOneAndUpdate|bulkWrite|doc\.set|\.overwrite' \
  . --include='*.js' | grep -v node_modules | head -40
```

## 3. Mining the read site

```bash
# every fallback read — the names pollution can fill
grep -rnoE '[a-zA-Z_$.]+\.[a-zA-Z_]+\s*(\|\||\?\?|===?\s*undefined)' \
  . --include='*.js' | grep -v node_modules | sort -u | head -120

# the authz names specifically
grep -rnoE '(isAdmin|is_admin|admin|role|level|verified|active|enabled|owner_id|tenant_id|org_id|user_type|kind|type|superuser|staff|banned|approved|confirmed)\s*(\|\||\?\?|==|===|!==|!=|in)' \
  . --include='*.js' | grep -v node_modules | head -60

# the template/spawn/config sinks
grep -rnoE 'outputFunctionName|localsName|destructureLocals|escapeFunction|compileDebug|basedir|allowProto|helpers|partials|autoescape|loader|variable|sourceURL|interpolate|evaluate|imports|filters|globals|execPath|execArgv|workerData|modulePath|shell|env|argv0|cwd|detached|stdio|uid|gid|paths|extensions|specifier|main|dir|url|uri|hostname|baseURL|proxy|agent|headers|rejectUnauthorized|callbackUrl|webhook|notifyUrl|debug|verbose|secret|key|views|view engine|trust proxy' \
  . --include='*.js' | grep -v node_modules | head -80
```

Each `name.prop` read is a candidate pollution property — collect
them into a per-challenge write list.

## 4. The version evidence

```bash
# package.json + lockfile — the version decides the alias
python3 tools/gadget_lookup.py --lockfile <handout>/package-lock.json

# manual:
grep -oE '"(lodash|merge|deep-extend|node-extend|jquery|dset|object-path|set-value|dot-prop|qs|minimist|ini|union-value|assign-deep|mout|just-extend|defaults-deep|mixin-deep|for-in|setobject|taffydb|hoek|flat|fastify|@fastify)"[^,}]*' \
  <handout>/package.json <handout>/package-lock.json 2>/dev/null | head -40
```

Match the version to the CVE table in `real-world-cases.md`.

## 5. The app-code reachability

The merge exists — can the REQUEST reach it?

```bash
# the route that calls the merge
grep -rnE 'app\.(get|post|put|patch|delete|use)|router\.(get|post|put|patch|delete)|fastify\.(get|post|put|patch)|server\.route' \
  . --include='*.js' | grep -v node_modules | head -60

# trace each route's handler for the merge call
# a merge inside a POST /update handler that req.body feeds is live;
# a merge inside a startup config loader that never sees req is dead
```

The reachability question: does the route's handler pass a request-
shaped object to the merge? `merge(cfg, req.body)` — live.
`merge(cfg, defaultSettings)` — dead (default is app-controlled).

## 6. The sink reachability

The read site exists — does it fire AFTER the write?

```js
// order matters: the merge must run before the read
app.post('/update', (req,res)=>{ merge(cfg, req.body); res.json(ok) });
app.get('/render', (req,res)=>{ res.render('p', opts) });  // reads opts
// the write lands on /update; the sink reads on /render — ORDER is
// a sequence across requests, not within one
```

For process-global PP, the write and the read can be different
requests — the pollution persists between them. Map which routes
write and which read; the chain is `POST /update → GET /render`.

## 7. The carrier evidence

```bash
# what body/qs the merge's route accepts
grep -rnE 'bodyParser|express\.json|express\.urlencoded|fastify.*content-type|multipart|formidable|multer|busboy|qs\.parse|querystring' \
  . --include='*.js' | grep -v node_modules | head -40

# the query parser setting
grep -rnE "query parser|app\.set\(" . --include='*.js' | head -20
```

`qs`-extended → bracket carriers work; JSON-body → `{"__proto__":...}`
direct; urlencoded-flat → literal-key dead-end.

## 8. The "is the object a plain object" check

The merge target's prototype decides reachability:

```js
const o = {};                    // Object.prototype — vulnerable
const o = Object.create(null);   // null-proto — IMMUNE
class C { } const o = new C();   // C.prototype — vulnerable to class-attr
const o = new Map();             // Map — immune to prop pollution
Object.freeze(o)                 // frozen OWN writes blocked; proto reads still work
```

If the merge target is `Object.create(null)` or a Map — falsifier.

## 9. The minimal mining output

For each candidate:

```json
{
  "merge_site": "file:line — merge(cfg, req.body)",
  "merge_fn": "_.merge (lodash 4.17.4)",
  "carrier": "POST /update json body",
  "read_site": "file:line — opts.outputFunctionName || def",
  "sink_class": "ejs compile",
  "property": "outputFunctionName",
  "aliases_to_try": ["__proto__", "constructor.prototype"],
  "falsifier": "merge guards __proto__/constructor; or sink reads hasOwnProperty"
}
```

That card drives the probe sequence — each field names one arm.

## 10. The ledger

```bash
python3 tools/state.py <chal> --hypothesis "pp: merge(cfg,req.body) at routes/update.js:23 reads outputFunctionName at views.js:41"
```
