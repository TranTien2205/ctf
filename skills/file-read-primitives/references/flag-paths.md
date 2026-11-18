# Flag Paths — where the flag actually lives

## The default CTF flag files — the guess-order

```
/flag
/flag.txt
/root/flag
/root/flag.txt
/home/ctf/flag
/home/ctf/flag.txt
/home/user/flag
/app/flag
/app/flag.txt
/var/flag
/var/flag.txt
/tmp/flag
/opt/flag
/run/flag
/srv/flag
/usr/flag
/flag{...}
/flag-{uuid}
/flag.md
/flag.php
/flag.json
/flag.xml
/flag.yml
/flag.ini
/flag.conf
/flag.db
/flag.sqlite
/flag.sqlite3
/flag.backup
/flag.bak
/flag.old
/flag.orig
/flag2.txt
/fl4g
/f1ag
/thisisflag
/readflag
/getflag
/showflag
/flag_here
/flag-here
/the_flag
/theflag
```

## The env-var flags — the process env

```
/proc/self/environ           — FLAG / CTF_FLAG / APP_FLAG
/proc/1/environ              — docker-injected
/proc/*/environ              — any process's env
```

`getenv("FLAG")`/`os.environ["FLAG"]`/`process.env.FLAG`/`System.getenv("FLAG")`
— the env-injected flag — `/proc/*/environ` reads it.

## The source-code flags — `define('FLAG',...)`/`const FLAG`

```php
define('FLAG', 'flag{...}');
const FLAG = 'flag{...}';
$flag = 'flag{...}';
getenv('FLAG');
```

```python
FLAG = 'flag{...}'
os.environ['FLAG']
```

```javascript
const FLAG = 'flag{...}';
process.env.FLAG;
```

```java
String FLAG = "flag{...}";
System.getenv("FLAG");
```

The source contains the flag literal — `file:///` read of the source.

## The config-file flags

```
/app/config.php         — define('FLAG'...)
/app/.env               — FLAG=...
/app/config.yml         — flag: flag{...}
/app/config.json        — {"flag": "..."}
/var/www/html/.env
/var/www/html/config.php
/etc/app/config.ini
/etc/flag.conf
/opt/app/flag.conf
/home/ctf/.env
/home/ctf/config.yml
```

## The db-stored flags — the flag-in-the-db

The flag is in a table — XXE/LFI can't query it — read the DB creds +
connect via SQLi or a `LOAD_FILE`-style chain — the flag-in-db chain.

## The URL-only flags — the flag is served, not stored

A flag the app serves at `/flag`/`/admin/flag`/`/debug`/`/internal` —
`http://127.0.0.1/flag` via SSRF — the flag is a response, not a file.

## The sibling-service flags — the flag-service

`http://flag-svc:8080/` — a flag-service container — the SSRF-read.

## The "the flag is a comment" — `<!-- flag -->`/`# flag`/`// flag`

```
<!-- flag{...} -->
# flag{...}
// flag{...}
/* flag{...} */
;; flag{...}
```

A comment in a source/template/DHTML file — the raw source read carries it.

## The "the flag is in a log" — the logged flag

```
/var/log/apache2/access.log    — a past /flag request
/var/log/auth.log
/var/log/nginx/access.log
/var/log/syslog
/var/log/app.log
/var/log/ctf.log
```

A past request logged the flag — the log-archaeology.

## The "the flag is in history" — the typed flag

```
/root/.bash_history          — cat /flag
/home/*/.bash_history
/root/.mysql_history         — SELECT * FROM flag
/root/.psql_history
/home/*/.python_history
/home/*/.zsh_history
C:\Users\*\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadline\ConsoleHost_history.txt
```

The flag was typed once — the history files.

## The "the flag is in a git-commit" — the git-leak

```
/var/www/.git/config         — remotes
/var/www/.git/HEAD           — current ref
/var/www/.git/refs/heads/*
/var/www/.git/packed-refs
/var/www/.git/objects/xx/yyyy  — zlib-objects — decode with zlib.inflate
```

A flag committed then deleted — the git-object has it.

## The "the flag is a filename" — `file:///flag{...}`

A filename that IS the flag — `file:///` dir-listing (Java) reveals it —
`glob://*` lists it — `ls`/`dir`-equivalent oracles.

## The "the flag is in a metadata field" — the xmp/id3/exif

A flag in a media file's metadata — `exiftool`-read — `exif_read_data`/
`getimagesize` oracle — `osint-media-metadata` territory.

## The "the flag is in a backup" — the backup-corpus

```
/root/backup.tar.gz
/var/backups/*.tar.gz
/var/backups/*.sql
/var/backups/*.zip
/home/*/backup*
/root/*.bak
/root/*.old
```

## The "the flag is in the DB-backup" — the .sql/.dump

```
/var/backups/db.sql
/root/db.dump
/root/dump.sql
/var/lib/mysql/flag.frm
/var/lib/mysql/flag.ibd
/var/lib/postgresql/data/base/*/flag
```

## The "the flag is in a memory-dump" — the coredump

```
C:\memory.dmp
/var/crash/*.crash
/tmp/*.core
/tmp/core.*
/proc/self/mem              — the process memory (careful — huge)
```

A core-dump or memory-dump carries the flag — `strings`-read.

## The "the flag is in a swap/tmp" — the transient

```
/tmp/*
/var/tmp/*
/dev/shm/*
/run/shm/*
```

## The "the flag is the filename-of-a-dir" — `glob`-list

`glob://*`/`scandir`/`ls`-equivalent — the flag is a file/dir NAME —
the listing-oracle.

## The "the flag is in a serialized blob" — the unserialize-trap

A `flag.ser`/`.dat`/`.bin` — a serialized PHP/Python object — the
deserialization-sink — `web-deserialization`.
