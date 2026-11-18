# Sinks Not Flags — when the gadget's output isn't the flag

## The reframe — "the RCE worked" is a waypoint, not a solve

Most failed deser sessions end at "the gadget ran" — the flag was never
the RCE, it was behind the RCE. The last-mile problem is *where the flag
is*, and it's a different question than "does the deserializer run".

## The flag-location census — where CTFs put it

```
the response itself           → a file-read gadget's output
/flag, /flag.txt, flag.txt    → a filesystem read
./flag, ./flag.txt            → the app's working dir
/app/flag, /var/www/flag      → the webroot
env var FLAG                  → `env`, `printenv`, `/proc/*/environ`
a config file                 → .env, config.php, settings.py, web.config
a DB row                      → SELECT flag FROM flags / config table
a property/file the app reads → the "flag" the app itself displays
a second endpoint              → the flag the gadget's role unlocks
the OOB callback               → your listener's log
```

## The `find` reflex — when the path is unknown

```bash
# the flag is *somewhere* — find it:
find / -name '*flag*' -type f 2>/dev/null
find / -iname 'flag*' -o -iname '*flag*' 2>/dev/null
grep -rl 'flag{' / 2>/dev/null
ls -la / /root /app /var/www /tmp /home/*/

# env vars:
env; printenv | grep -i flag; cat /proc/1/environ | tr '\0' '\n'

# process env (the flag in the process's env):
for p in /proc/*/environ; do tr '\0' '\n' < $p 2>/dev/null | grep -i flag; done

# config files that carry it:
cat .env config.php settings.py web.config wp-config.php secrets.yml 2>/dev/null

# the DB:
mysql -e 'SHOW DATABASES; USE app; SHOW TABLES; SELECT * FROM flags;'
sqlite3 /path/to/db 'SELECT * FROM flags;'
```

## The "read it via the gadget" vs "read it via a different primitive"

Once the RCE works, the flag is a READ problem — the cheapest read:

```
gadget can exec → cat /flag / find / env → the flag in the output
gadget writes a file → write flag-read into the file path → GET it
gadget reads a file → point the file-read gadget at /flag
```

But sometimes a different primitive is cheaper — if the deser confirmed
but its RCE is blocked, and a `file-read-primitives` path exists (LFI,
file-read endpoint, phar://), that path reaches `/flag` without the RCE.

## The flag-in-the-object — when the flag IS the prop

Rare shape: the *deserialized object itself* is the flag — a class whose
prop carries `flag{...}` — the flag was IN the original serialized blob.
Read the stream (`pickle_dis`/`php_ser_parse`/`java_ser`) BEFORE crafting —
the flag may already be inside.

## The flag-in-env shape — the env-var flag

```
env | grep -i flag
printenv FLAG
cat /proc/self/environ | tr '\0' '\n' | grep -i flag
cat /proc/1/environ | tr '\0' '\n' | grep -i flag
```

Common in containerized challenges — `FLAG=flag{...}` is in the process
env. `/proc/*/environ` is the cross-process env reader.

## The "flag is a DB row" shape

```sql
SELECT * FROM flag;
SELECT value FROM config WHERE name='flag';
SELECT flag FROM secrets;
```

The gadget needs `os.system`/`Process.Start`+`mysql`/`sqlite3`/`psql` —
or a query-prop gadget that queries the flag table.

## The "flag is behind another layer" shape

- a `role=admin` prop → GET `/admin` → the flag the admin view renders
- a file-write → a `.php` in webroot → `?c=cat /flag` → the flag
- a key-leak → forge a session → the flag behind the session's page

The RCE is one hop — the flag lives behind the *next* hop. Chain-bridges.md
maps which deser output → which next class.

## The `pre-flag` gate — the only way the flag counts

```bash
python3 tools/hooks.py pre-flag $C \
  --value 'flag{verbatim_bytes_from_response}' \
  --source 'the verbatim response/OOB line carrying it'
```

A flag-shaped string is a candidate. The gate writes it only from a real
response/artifact — your typed `flag{` doesn't count.

## Output to record

- Where the flag actually was (the path/env/row/route)
- The verbatim bytes that carried it
- The `pre-flag` + `post-probe` the ledger holds
