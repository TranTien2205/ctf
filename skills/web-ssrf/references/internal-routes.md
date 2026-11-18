# Internal routes — the loopback-route wordlist

The paths the app's own admin/internal-routes answer on loopback —
the routes you can't reach from outside that the server's own fetch
serves fine.

---

## 1. The flag-routes — the obvious homes

```text
/flag                /FLAG            /flag.txt         /getflag
/admin/flag          /api/flag        /internal/flag    /private/flag
/secret              /secret.txt      /theflag          /readflag
/flag.php            /flag.html       /flag.json        /flag.xml
/flag/               /flags           /flag1 /flag2
/the_flag            /real_flag       /get_flag         /the_flag.txt
/flag_endpoint       /flagged         /flagged-page
```

## 2. The admin-routes — the loopback-check the fetch satisfies

```text
/admin              /admin/          /admin.php        /admin.html
/admin/index        /admin/dashboard /admin/panel      /admin/config
/admin/users        /admin/settings  /admin/system     /admin/flag
/admin/console      /admin/shell     /admin/exec       /admin/cmd
/admin/backup       /admin/db        /admin/database   /admin/export
/admin/import       /admin/logs      /admin/status     /admin/health
/admin/metrics      /admin/info      /admin/debug      /admin/test
/admin/manage       /admin/control   /admin/api        /admin/api/flag
/administration     /administrator   /manage           /management
/console            /panel           /cpanel           /webpanel
/internal           /internal/       /internal/admin   /internal/api
/internal/flag      /internal/config /internal/status  /private
/private/           /private/admin   /private/flag
```

## 3. The actuator-routes — the Spring family

```text
/actuator            /actuator/      /actuator/env     — ALL env —
                                                        FLAG!
/actuator/health     /actuator/info  /actuator/beans
/actuator/configprops /actuator/mappings /actuator/metrics
/actuator/threaddump /actuator/heapdump — the memory-dump — flag
                                        in the heap!
/actuator/loggers    /actuator/logfile /actuator/auditevents
/actuator/httptrace  /actuator/sessions /actuator/shutdown —
                      the SHUTDOWN — the DoS — don't POST it
/actuator/jolokia    /jolokia        /jolokia/list     — JMX!
/actuator/prometheus /actuator/scheduledtasks /actuator/caches
```

## 4. The debug/diagnostic routes

```text
/debug              /debug/         /debug/vars        — go-expvar —
                                                        env+vars!
/debug/pprof        /debug/pprof/   /debug/pprof/heap  — go-pprof —
                                                        the heap —
                                                        profile the
                                                        flag!
/debug/pprof/goroutine /debug/pprof/cmdline /debug/pprof/env?
/debug/requests     /debug/events   /debug/routes      /debug/config
/debug/info         /debug/status   /debug/health      /debug/version
/debug/console      /debug/eval     /debug/shell       /debug/repl
/status             /status/        /status/json       /status?format=json
/health             /health/        /healthz           /healthcheck
/info               /info/          /version           /version.json
/metrics            /metrics/       /metrics/json      /metrics/prometheus
/trace              /tracing        /profiler          /profile
/dump               /dump/heap      /dump/threads      /stackdump
/threaddump         /heapdump       /env               /environment
```

## 5. The console/RCE-flavored routes

```text
/console            /console/       /h2-console        — h2-db-console —
                                                        jdbc-url →
                                                        RCE-via-alias!
/_console           /rails/console  — rails-console — the rails-info
/werkzeug           /console        — werkzeug-debugger — the PIN or
                                     the eval — flask-debug!
/__debugger__       — werkzeug-eval — the debugger-console
/phpinfo            /phpinfo.php    /info.php          /test.php
/eval               /eval.php       /shell             /shell.php
/cmd                /command        /exec              /exec.php
/run                /run.php        /system            /system.php
/task               /tasks          /job               /jobs
/repl               /repl/          /api/repl
/_debug             /_profiler      /_profiler/phpinfo — symfony-profiler
/app_dev.php        /dev.php        /dev/              /development
/test               /test/          /testing           /debug.php
```

## 6. The api/internal-api routes

```text
/api                /api/           /api/v1            /api/v2
/api/internal       /api/admin      /api/config        /api/flag
/api/users          /api/keys       /api/secrets       /api/tokens
/api/health         /api/status     /api/version       /api/info
/api/debug          /api/env        /api/system        /api/dump
/api/export         /api/backup     /api/db            /api/data
/api/execute        /api/run        /api/command       /api/eval
/internal/api       /internal/api/  /internal/api/flag
/api-docs           /swagger        /swagger.json      /openapi.json
/api/swagger        /api/openapi    /v2/api-docs       /v3/api-docs
/graphql            /graphiql       /graphql/console   — the gql-
                                                       introspection —
                                                       the schema the
                                                       routes
```

## 7. The monitoring/observability routes

```text
/metrics            /metrics/prometheus     /prometheus
/-/healthy          /-/ready                /-/reload     — prometheus-
                                                          control
/api/v1/status/config /api/v1/targets       /api/v1/alerts
/node_exporter      /node-metrics
/stats              /statsd                 /stats.json
/nginx_status       /stub_status            /server-status
/server-info        /server-status?auto
/fpm-status         /fpm-ping               /fpm-pong
/solr/admin/info/system /solr/admin/cores?action=STATUS
/jmx                /jmx-console            — jboss-jmx — deploy!
/jbossws/services   /web-console            — jboss
/manager/html       /manager/status         — tomcat-manager —
                                              deploy-a-war!
/host-manager/html  /tomcat/manager
/wildfly            /wildfly/management
/jolokia            /jolokia/list
/hawtio             /hawtio/jolokia          — java-mgmt
/druid/index.html   /druid/datasource.html   — druid-monitor —
                                               datasource-creds!
```

## 8. The data/admin routes

```text
/phpmyadmin         /pma            /phpMyAdmin        — db-admin
/adminer            /adminer.php    — the mini-admin
/mysql              /mysql-admin
/redis              /redis-admin
/mongo              /mongo-express
/es                 /elasticsearch  /kibana
/_cat/indices       /_all/_search?pretty  — es-routes — the dump
/_cluster/health    /_cluster/state?pretty
/couchdb            /_utils         — couchdb-admin — /_all_dbs
/influxdb           /query?q=show+databases
/minio              /minio/health   /minio/prometheus/v2/metrics
/consul             /v1/agent/services /v1/kv/?recurse
/etcd               /v2/keys/?recursive=true
/zk                 /zookeeper
/nacos              /nacos/v1/console — alibaba-nacos — config-svc
/eureka             /eureka/apps    — spring-eureka — the svc-registry —
                                      WHICH SERVICES + WHERE — the map
/sentinel           /sentinel-dashboard
/xxl-job            /xxl-job-admin  — the scheduler — job-trigger
/apollo             /apollo
/seata              /seata
/rocketmq           /rocketmq-console
/dubbo              /dubbo-admin
```

## 9. The ci/cd and dev-tool routes

```text
/jenkins            /jenkins/script — the script-console — RCE!
/script             /scriptConsole  — jenkins-script — groovy —
                                      RCE — default-auth absent on
                                      internal often
/gitlab             /gitlab/admin   — gitlab-admin
/nexus              /nexus/service/rest — nexus-repo
/sonarqube          /sonar/api      — sonar
/gitea              /gitea/api      — gitea
/drone              /drone/api
/argocd             /argocd/api
/rancher            /rancher/api
/harbor             /harbor/api     — harbor-registry
/portainer          /portainer/api  — portainer — docker-mgmt!
/rancher            /rancher
```

## 10. The flag-route-discovery — when the path is unknown

```text
the path isn't guessable → the discovery-paths:
  - /proc/self/maps via file:// → the loaded-files → the route-
    handler paths — the route-map in the binary
  - /proc/self/cwd/ + the source-files → the route-defs in source
  - the nginx/apache-conf via file:// → the location-blocks →
    the internal-routes declared — the conf names them!
  - /actuator/mappings /debug/routes /openapi.json — the route-
    inventory-endpoints — the app tells you its routes
  - the front-end js — the route-calls — bundle_miner
  - the sitemap/robots — robots.txt names the hidden-routes —
    the classic recon-file
```

## 11. The method-variants — the route's verb

```text
GET /admin/flag    — the read-verb — most fetchers GET
POST /admin/flag   — some routes need POST — the fetch's method is
                     fixed-usually-GET — the route may reject-GET —
                     the method-control needs gopher-http or a
                     crlf-injected second-request — the GET-fetches
                     can't POST without composition
PUT /x             — write-verb — the state-changes
DELETE /x          — destructive
the fetch-method is the constraint — the route's verb-expectation —
a POST-only route is unreachable via plain-http-fetch — the
header/method-control paths from gopher-deep.md
```

## 12. The vhost-routes — the name-bound

```text
the app may vhost — the route answers only for the right Host:
  http://internal-vhost:80/admin — the vhost-name — the host-header
                                  selects the vhost — the internal-
                                  vhost-name — /etc/hosts, nginx-conf,
                                  the resolv.conf's domain
  http://admin.localhost/         — the admin-subdomain — the vhost-
                                    by-name
  http://internal.localhost/
  the loopback-route the fetcher's HOST-header selects — gopher-for-
    http with Host: internal-vhost — the header-control
```

## 13. The route-budget — the bounded-inventory

```text
don't spray 500 routes — the inventory is bounded:
  - the actuator/debug/flag/admin families — ~30 high-value routes
  - /proc/self/maps + the conf-files via file:// — the REAL routes
    over the wordlist — read the route-map don't guess it
  - the route-list-endpoints — /actuator/mappings /debug/routes
    /openapi.json — the app tells you
the route-sweep is a probe-class — 5 probes or the inventory —
whichever comes first
```
