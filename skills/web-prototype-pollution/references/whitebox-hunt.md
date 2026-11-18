# White-box hunt — reading the merge and the sink out of source

When the handout includes source, the merge site and the sink are
already named — the job is to find them, not to guess.

---

## 1. The grep battery

```bash
# merge calls — the write sinks
grep -rnE '\bmerge\s*\(|\.merge\(|_\.merge|_\.defaultsDeep|_\.assign|deepmerge|deep-extend|extend\(\s*true|\$\.extend' \
  --include='*.js' --include='*.ts' . | grep -vE 'node_modules|\.min\.|test'

# the request→merge boundary — who passes req.* to a merge
grep -rnE 'merge\s*\(\s*[^,]*,\s*req\.|merge\s*\([^)]*body|merge\s*\([^)]*query|extend\s*\(\s*true[^)]*req\.' .

# path-setters — the dotted-path primitives
grep -rnE 'set\s*\(\s*[a-zA-Z_]+\s*,\s*[a-zA-Z_]*path|split\s*\(\s*["'"'"']\.|\.split\(["'"'"']\.["'"'"']\)|dset|object-path|set-value' .

# the sinks — what reads the merged object
grep -rnE 'new Function|eval\s*\(|\.compile\s*\(|\.render\s*\(|renderFile|spawn\s*\(|execFile|exec\s*\(|fork\s*\(|require\s*\(|vm\.run|Function\s*\(' .

# the fallback grammar — readable properties
grep -rnE '\|\||\?\?|hasOwnProperty|\bin\s+[a-z_]+|Object\.create\(null' .
```

## 2. The merge-site signature list

```js
// the sink shapes
_.merge(opts, req.body)
_.merge(config, req.query)
merge(opts, req.body)
mergeDeep(a, req.body)
deepmerge(a, req.body)
$.extend(true, {}, req.body)
jQuery.extend(true, {}, req.body)
extend(true, {}, req.body)
Object.assign({}, defaults, req.body)   // SHALLOW — not the sink alone
for (var k in req.body) obj[k] = req.body[k]   // hand-rolled, no guard
for (const k of Object.keys(req.body)) obj[k] = req.body[k]
function merge(d, s) { for (k in s) { if (typeof s[k]==='object' && s[k]!==null)
  { d[k] = d[k]||{}; merge(d[k],s[k]) } else d[k] = s[k] } }   // the recursive
```

The recursive `for..in` with `typeof === 'object'` recursing into it
is THE vulnerable shape — every `s[k]` gets copied to `d[k]`, and when
`k` is `__proto__`, `d.__proto__` hits the setter.

## 3. The `path.split('.')` sinks

```js
// the dotted-path setter
function set(obj, path, val) {
  const keys = path.split('.');
  let cur = obj;
  for (let i = 0; i < keys.length - 1; i++) {
    cur = cur[keys[i]] = cur[keys[i]] || {};
  }
  cur[keys[keys.length-1]] = val;
}
set(obj, "__proto__.m", 1)   // the write
```

`dset`, `object-path.set`, `set-value`, and every hand-rolled
`split('.')` walker is this shape. The `path` is attacker-controlled
when an API takes a field name (`{"field":"__proto__.m"}`).

## 4. The sink map — what reads the merged object

For each merge call, follow the target variable to its reads:

```js
const config = merge({}, defaults, req.body);
app.set('view options', config);          // → render opts sink
spawn(cmd, {env: config.env});            // → spawn sink
ejs.compile(tpl, config);                 // → template sink
if (config.isAdmin) ...                   // → authz sink
require(config.module);                   // → require sink
```

Each read-site is a gadget — `gadget-index.md` maps the property
names to sinks.

## 5. The express-specific spots

```js
app.set('view engine', 'ejs');
app.set('view options', {...});           // the option object
app.locals = {...};                       // merged into every render
res.render('page', mergedData);           // data → template
app.use(bodyParser.json());
app.set('query parser', 'extended');      // qs parser — the carrier switch
```

`app.locals` merged-with-request-data is the highest-value site —
every render's options pick it up.

## 6. The mongoose spots

```js
Model.updateOne(filter, update)
Model.findOneAndUpdate(filter, update)
Model.bulkWrite(ops)
doc.set(req.body)
doc.update(req.body)
Object.assign(doc, req.body)
doc.overwrite(req.body)
Model.aggregate([...])
```

`doc.set` and `updateOne`'s `$set`/`$rename`/`$push` fields are the
path-primitives — the target path string is where `__proto__.` goes.

## 7. The Python spots

```python
setattr(obj, k, v) for k, v in payload.items()
update_config(request.json)
def set_path(obj, path, val): ...
config.update(request.json)
deep_update(settings, request.json)
merge(a, request.json)
settings.__dict__.update(...)
getattr(obj, field) / setattr(obj, field, val)   # field from request
exec(request.json['code']) / eval(...)
importlib.import_module(name)
globals()[name] = val
vars(obj).update(...)
```

`class-pollution-python.md` has the attribute-path details.

## 8. The "check the actual merge implementation" step

When a vendored `merge()`/`extend()` is found, READ it:

```js
// does it check the key?
if (key === '__proto__' || key === 'constructor' || key === 'prototype') continue;
// does it use hasOwnProperty?
if (!src.hasOwnProperty(key)) continue;
// does it check own-only on the TARGET?
if (!Object.prototype.hasOwnProperty.call(dest, key)) dest[key] = {};
```

The three checks map to the three bypasses: name-blacklist →
`constructor`, hasOwnProperty → doesn't help (see common-mistakes),
target-own → only new keys merge (pollute a NEW key the sink reads).

## 9. The version pin file

```bash
cat package.json | grep -E 'lodash|merge|deep-extend|jquery|node-extend|mout|just-extend|dset|object-path|set-value|union-value|assign-deep|dot-object|minimist|yargs-parser|ini|qs|extend|deepmerge'
cat package-lock.json | python3 tools/gadget_lookup.py --lockfile -
```

`gadget_lookup` names the vulnerable merge before you write a
payload — the version decides `__proto__` vs `constructor.prototype`.
