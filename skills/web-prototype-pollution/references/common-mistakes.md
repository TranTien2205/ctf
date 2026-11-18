# Common mistakes — the ways this class's probes go wrong

---

## 1. Confusing local write with prototype write

The response echoes `{"__proto__":{"m":1}}` — you see the property on
the object and call it a finding. It isn't: the merge assigned
`__proto__` as an own property (the JSON-parse shape) OR wrote it to
the object locally. The proof is the fresh-object readback: create
or fetch an object you did NOT write — no marker there means no
prototype write. This is the single most common false positive.

## 2. Jumping at the payoff property first

`{"__proto__":{"isAdmin":true}}` → 403 persists → "the class is
closed". Not necessarily: the WRITE may never have landed (a local
merge), the sink may not read `isAdmin` (wrong property name), or the
check is `=== true` vs your `"true"`. The marker-first protocol exists
because a failed payoff-write tells you nothing — isolate the write
from the sink.

## 3. Treating `Object.assign` as a sink

`Object.assign({}, req.body)` is SHALLOW — `__proto__` lands as a
literal own property (the response echoes it), never touching
`Object.prototype`. The response echo makes it LOOK like pollution.
Only recursive merges write the proto. `_.merge`, `deep-extend`,
`merge-deep`, `$.extend(true,...)` are sinks; `Object.assign`,
`_.assign`, `{...}` spreads are not.

## 4. Testing the wrong carrier

`__proto__` through `?x=` when the app's query parser is `simple`
(flat keys) — the key arrives as literal text `__proto__[x]` and the
merge sees a weird field name, not a proto path. Match the carrier to
the parser: JSON for body merges, qs-brackets for extended parsing,
dotted-path for path-APIs.

## 5. Forgetting the materialization step

The stored doc holds `"__proto__.m":1` as a STRING FIELD (BSON literal
path); only when the doc is loaded into a JS object does the path
resolve. The readback that doesn't re-materialize (a raw DB dump, a
cached response) shows nothing. Fetch through the app's normal read
path — `toObject()`/`lean()`/`toJSON()` are where the proto goes live.

## 6. Type mismatches on the payoff property

- `{"isAdmin":"true"}` vs `if(user.isAdmin === true)` — string fails.
- `{"role":["admin"]}` vs `if(user.role === 'admin')` — array fails.
- `{"perms":"admin"}` vs `perms.includes('admin')` — string has
  `includes` but checks substring not element — `"adminx"` contains it.

Match the type the CHECK expects, not the type you sent.

## 7. Claiming the sink before the sink ran

`outputFunctionName` polluted, but the template was compiled at boot —
no render runs the new options. The write is real; the SINK is the
missing half. Trigger the compile (`/render`, `/preview`, a fresh
page) before claiming impact.

## 8. The "pollution stays forever" surprise

`Object.prototype` pollution is process-global until restart. On a
shared instance your `isAdmin` persists for every other player — the
app is broken for them too. This is simultaneously the finding AND
the cleanup problem; on a CTF it usually wins you the flag instantly,
but on a real engagement it's a DoS-sized blast radius.

## 9. Missing the second-hop carrier

You can't reach the merge directly — but the app merges an IMPORTED
object (a webhook payload, a fetched JSON, a queued job arg). The
pollution goes into whatever the second hop imports. SSRF → JSON →
merge is the two-hop carrier most people don't try.

## 10. Reading the wrong response field

The marker lands on a DIFFERENT field than where you read:
`{"config":{"__proto__":{"m":1}}}` may materialize as `config.m` (the
nested path) not `m` — the marker is under the WRAPPER's proto, not
the object's. Read the whole response and search for the marker
string, don't check one field.

## 11. Assuming `hasOwnProperty` saves it

`for (k in src) if (src.hasOwnProperty(k)) dest[k]=src[k]` — the
`hasOwnProperty` check on the SOURCE passes for `__proto__` because
`JSON.parse` made it an own property. The guard that actually works is
a blacklist on the DESTINATION path, not a source-side check. A merge
"protected" by `hasOwnProperty` is often still vulnerable.

## 12. The unicode-escape miss

The filter checks the bytes `__proto__` — but `{"__prot\u006f__":{}}`
parses to the same key and slips a byte-level check. Always try the
escaped form once.

## 13. Recording a `404` as `refutes`

A `404` on the write endpoint means the route didn't match — the
merge never ran. It's `inconclusive`, not `refutes`. Check the
endpoint exists at all before counting the write as denied.
