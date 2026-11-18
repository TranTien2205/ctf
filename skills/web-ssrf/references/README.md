# SSRF references — navigation

The corpus files, ordered by when you'd open them. The canonical
contract lives in `../SKILL.md`.

## Detection & confirmation
- `detection.md` — the paired first-probe, the read-channel ladder,
  the class vs impact evidence split
- `error-analysis.md` — what each error-string means, the failure-
  stage ladder, the refused-vs-timeout diagnostic
- `blind-ssrf.md` — timing/status/OOB oracles, the callback-shape,
  the shared-store write-read channel
- `fetcher-matrix.md` — per-library scheme-list + redirect + header-
  forward + crlf-inject — read the callback's UA first

## Bypass — the filter families
- `url-parsing.md` — IP-encodings, @/#/?-confusion, scheme-flex,
  parser-differential table
- `bypass.md` — the check-type → bypass-family mapping
- `dns-rebind.md` — the resolve-twice gap — TTL=0, A/AAAA splits,
  own-DNS-server
- `redirect-chains.md` — the validate-then-follow escape — 301-308,
  open-redirect-on-allowed-domain, scheme-change-redirects
- `crlf-injection.md` — the SSRF→request-smuggling boundary — the
  weather-app shape

## Reach — what the fetch gets
- `file-read.md` — the file:// map — flag-paths, /proc- discovery,
  config/source/log/session paths, the cwd-trick
- `protocol-smuggling.md` — the scheme-table — gopher/dict/ldap/
  jar/netdoc/php-filter/expect/http+unix
- `internal-pivot.md` — the loopback-inventory, the admin-route,
  the subnet-sweep
- `internal-services.md` — per-service exploitation — redis/es/
  docker/k8s/consul/etcd/memcached/admin-consoles
- `cloud-metadata.md` — aws/gcp/azure/do/alibaba/ecs/k8s — the
  metadata playbook + the flag-locations
- `unix-socket.md` — docker.sock and the unix-aware fetchers

## Composition — the heavy machinery
- `gopher-deep.md` — the gopher wire-shape, encoding, the redis/
  memcached/smtp/zabbix/fcgi dialogs
- `fastcgi-gopher.md` — the FastCGI binary-records + the
  auto_prepend RCE chain
- `framework-sinks.md` — where the url-param lives per-stack —
  php-wrappers, urllib, java-handlers, open-uri

## Corpus & process
- `payload-dictionary.md` — ~700 payloads categorized by purpose —
  the take-the-family-that-fits index
- `ctf-shapes.md` — the 20 challenge-archetypes — surface → flag-
  location → chain
- `workflow.md` — the ordered probe-phases + the per-branch
  falsifiers + the budget-shape
- `tooling.md` — `ssrf_probe`/`gopher_gen`/`oob_listener`/
  `http_probe`/`read_loop`/`sanitizer_fuzz` — verified flags only
- `whitelist-shapes.md` — the allowlist bypasses — endswith/
  contains/startswith/regex/parse-then-check
- `json-params.md` — the param-vocabulary + the structural shapes —
  objects/arrays/nested/encoded-layers
- `request-shapes.md` — where the url-control enters — query/json/
  multipart/header/cookie/path — the decode-order question
- `egress-blocked.md` — the no-external-fetch model — the internal-
  echo channel, the link-local exception
- `webhook-deferred.md` — the async surface — the results-channel,
  the schedule, the worker-context
- `second-order.md` — the store-then-fetch gap — the write-check vs
  fetch-parse differential
- `common-mistakes.md` — the failure-modes — canary-silence, error-
  bodies, the fetcher-fingerprint
- `taxonomy.md` — the shape-tree — read-channel/fetch-context/scope/
  check-type — the class-boundaries
- `evidence-rules.md` — the proof-ladder — surface/class/impact —
  the substring-binding, the verdict-map
- `advanced-reach.md` — ipv6-shadows, name-forms, port-boundaries,
  the combined-chains, the last-hop tricks
- `host-header-ssrf.md` — the trusted-header fetch-source —
  X-Forwarded-Host/Referer/X-Original-URL — the header-as-target
- `internal-routes.md` — the loopback-route wordlist — flag/admin/
  actuator/debug/console routes + the route-discovery paths
- `cheatsheet.md` — the field-manual tables — probes, checks→bypasses,
  ports→services, schemes→reach, metadata→flag-paths
- `probe-sequences.md` — the ordered play-books — A through L per
  situation
- `theory-primitives.md` — the conceptual frame — position/trust,
  the three axes, the mechanism-layers
- `flag-locations.md` — where the flag actually lives — routes/files/
  env/metadata/stores/messages/control-planes
- `fetcher-fingerprint.md` — reading the callback's raw request —
  the UA/source-ip/headers/body/timing as the fetch-context
- `framework-checks.md` — the per-framework filter-implementations
