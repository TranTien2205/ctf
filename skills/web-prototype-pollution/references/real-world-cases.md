# Real-world cases — the shapes that actually ship

The production PP CVEs and challenge chain-cards that define the
class's vocabulary. Each is a measured precedent — a shape to
recognize, not to re-derive.

---

## 1. The library-merge CVEs — the write-side canon

| CVE/advisory | Package | The flaw | The lesson |
|---|---|---|---|
| CVE-2018-16487 | lodash `merge`/`defaultsDeep` | recursive merge walks `__proto__` | the canonical PP write |
| CVE-2018-3721 | lodash `defaultsDeep` | same | multiple fns affected |
| CVE-2019-10744 | lodash `defaultsDeep` (<4.6.1) | mass PP via defaultsDeep | version-window |
| CVE-2020-8203 | lodash `zipObjectDeep` | path-setter variant | `set`-style too |
| CVE-2021-23337 | lodash `template` | `options.variable` → code gen | the template gadget |
| CVE-2020-28282 | `deep-extend` | recursive merge | a lodash-merge clone |
| CVE-2021-25950 | `just-extend` | recursive merge | another clone |
| CVE-2021-3918 | `json-schema` `validate`/paths | `$ref`+path write | schema paths |
| CVE-2020-7712 | `ini` parse | `a[__proto__]=x` in INI file | INI carrier |
| CVE-2020-7637 | `set-value` | dotted path setter | path API |
| CVE-2021-23440 | `set-value` | same, unfixed | version-window |
| CVE-2020-7754 | `minimist` | argv-parser builds proto keys | CLI carrier |
| CVE-2021-44906 | `minimist` | same | persisted |
| CVE-2022-24999 | `qs` `allowPrototypes` | parse-side proto keys | the qs guard |
| CVE-2021-23518 | `dset` | dotted-path setter | `dset(o, '__proto__.x', v)` |
| CVE-2022-31116 | `object-path` `set` | path setter | same class |
| CVE-2020-7711 | `dot-prop` `set` | path setter | same |
| CVE-2021-25949 | `union-value` | path write | union into proto |
| CVE-2019-10746 | `mixin-deep` | recursive merge | same |
| CVE-2020-8204 | `lodash.set` | path setter | the setter variant |
| CVE-2022-24785 | `moment` `locale` | locale path | a string-key path |
| CVE-2020-28282 dup | `node-extend` | `extend(true, a, b)` | jQuery-extend shape |

## 2. The in-tree chain cards — the local measured solves

```
htb-secnotes-mongoose-rename-prototype-pollution-local-gate
  $rename path-write → obj.isAdmin-style fallback read
  LESSON: the path-API/$rename carrier; pin the filter to your own
          document; a local-only gate read the polluted property

htb-tornadoservice-bot-csrf-class-pollution
  class pollution through a bot-relayed CSRF — the bot's request
  carried the write; the sink was a Python-side class attr
  LESSON: the relayed carrier — you write once via the bot, the
          class change persists for subsequent requests

htb-novacore-hopbyhop-cache-overflow-domclobber-polyglot-rce
  hop-by-hop + cache + DOM-clobber + polyglot → RCE
  LESSON: PP was one layer of five — it supplied the clobber/
          gadget primitive inside a larger chain; the write is
          rarely the whole solve

cscv2026-chromatic-mergecatalog-constructor-prototype-ejs-outputfunctionname-rce
  merge-catalog endpoint → constructor.prototype → outputFunctionName
  → EJS generated-code → RCE; harmless marker confirmed first
  LESSON: the constructor.prototype alias when __proto__ is absent;
          outputFunctionName as the sink; marker-then-payload
```

## 3. The "shape" each case teaches

### A. lodash-merge shape (the default)

```js
const cfg = _.merge({}, defaults, req.body);   // CVE-2018-16487
{"__proto__":{"x":1}}                          // the write
```

Signal: `_.merge`/`.merge(`/`_\.` on req-derived objects.

### B. hand-rolled recursive merge (the clone)

```js
function merge(d,s){for(k in s){if(typeof s[k]=='object'&&s[k]!==null)
  {d[k]=d[k]||{};merge(d[k],s[k])}else d[k]=s[k]}}
```

Signal: the `for..in`+recursion pattern; no name guard.

### C. path-setter (dset/object-path/set-value)

```js
set(config, req.body.field, req.body.value)
{"field":"__proto__.x","value":1}
```

Signal: a `set(path,val)` API where the path is a request string.

### D. document-store rename (mongoose/mongodb)

```js
Model.updateOne(filter, {$rename:{a: req.body.to}})
{"to":"__proto__.x"}
```

Signal: an update endpoint forwarding operator-documents.

### E. extend(true,...) (jQuery/node-extend/deep-extend)

```js
const o = $.extend(true, {}, req.body);
const o = extend(true, {}, req.body);
```

Signal: `extend(` with a `true` first arg — the deep flag.

### F. Python class pollution

```python
def merge(o, s):
    for k,v in s.items():
        if isinstance(v,dict): merge(getattr(o,k),v)
        else: setattr(o,k,v)
```

Signal: `getattr`/`setattr` in a merge — `__class__` reaches the
class object.

### G. client-side DOM clobber (the twin)

```html
<form name=cfg><input name=api value=https://attacker>
```

Signal: `window.cfg.api`-style reads with injectable name/id HTML.

## 4. The version-pin discipline

Every case is version-bound. Before burning probes:

```bash
python3 tools/gadget_lookup.py --lockfile <handout>/package-lock.json
# or read the lockfile and match against the CVE list above
```

A `lodash@4.17.10` merge is pre-patch; `4.17.21` is mostly fixed for
`__proto__` but `constructor.prototype` and `set`-paths survive on
some versions. The version decides WHICH alias works — not whether
the class exists.

## 5. The pattern-to-attempt mapping

| Observed pattern | First alias to try | If filtered |
|---|---|---|
| `_.merge/defaultsDeep` | `__proto__` | `constructor.prototype` |
| `extend(true,..)` | `__proto__` | `constructor.prototype` |
| `set/dset/object-path` | `__proto__.x` | `constructor.prototype.x` |
| mongoose update | `$rename`→`__proto__` | `$set`→`constructor.prototype` |
| hand-rolled merge | `__proto__` | `constructor.prototype` |
| Python setattr-loop | `__class__.x` | `__init__.__globals__.x` |
| qs/ini/minimist parse | `__proto__[x]` | `constructor[prototype][x]` |
| client merge | `__proto__` in hash/msg | clobber the read name |

## 6. The recurring traps the cases document

- **"the write returned 200 but nothing polluted"** — the merge
  was shallow, or used `defineProperty`, or the input was a string
  not an object. Always readback on a FRESH object.
- **"the marker polluted but no payoff"** — no sink read the name.
  The gadget hunt is a separate step; write-confirmation ≠ impact.
- **"the filter caught `__proto__`"** — `constructor.prototype` is
  the alias; the filter checked the literal string, not the path.
- **"the app crashed on my write"** — you shadowed a built-in
  method (`toString`/`valueOf`) or broke an enumeration — the
  write landed but took the process down. Use a benign name.
- **"it worked locally, not on the instance"** — a different
  dependency version; `gadget_lookup` the lockfile.
- **"other users' sessions broke"** — process-global write; the
  blast_radius was real. Pin writes, use harmless markers, plan
  the restart.
